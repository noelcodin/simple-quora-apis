# -*- coding:utf-8 -*-

import ast
import base64
import random
import re
import string
import jwt
from flask import jsonify
from enum import Enum
from hashids import Hashids

from model.quiz_db import UserTab
from common.config import app, SECRET_KEY, SALT


# Define internal errors
class ErrorCode:
    def __init__(self, code, msg, status_code):
        self.code = code
        self.msg = msg
        self.status_code = status_code


class InternalError(Enum):
    DBError = ErrorCode(401, "Database has some issue now", 500)
    DataNotFound = ErrorCode(402, "Data does not exist", 404)
    RegisterError = ErrorCode(403, "Register fails", 400)
    LoginError = ErrorCode(404, "Login fails", 400)
    NoEligibleQuiz = ErrorCode(405, "No quiz can be provided to you now", 200)
    NoPermissionError = ErrorCode(406, "Current user has no permission to perform this operation", 403)
    NotAuthenticatedUser = ErrorCode(407, "No operation is allowed until you have signed in", 401)
    ParamError = ErrorCode(408, "Parameters in the request are not as expected", 400)
    EmailRegistered = ErrorCode(409, "This email has already been registered", 200)


# Jsonfy successful response
def common_json_response(data, error_code=0, err_msg='success', method="get"):
    resp = jsonify({
        "error_code": error_code,
        "err_msg": err_msg,
        "data": data
    })
    if method == "get":
        resp.status_code = 200
    elif method == "post":
        resp.status_code = 201
    elif method == "delete":
        resp.status_code = 204
    return resp


# Jsonfy error response
def error_response(error, data=None):
    resp = jsonify({
        "error_code": error.code,
        "error_msg": error.msg,
        "data": data
    })
    resp.status_code = error.status_code
    return resp


# b64 encode strings
def b64_encode(input):
    return base64.b64encode(input.encode('ascii')).decode('ascii')


# b64 decode strings
def b64_decode(input):
    return base64.b64decode(input.encode('ascii')).decode('ascii')


# b64 encode password with random prefix and suffix
def encoded_pswd(input):
    b64_pswd = b64_encode(input)
    prefix = "".join(random.sample(string.ascii_letters, 5))
    suffix = "".join(random.sample(string.ascii_letters, 5))
    return prefix+b64_pswd+suffix


# b64 decode password, trim random prefix and suffix
def decoded_pswd(input):
    return b64_decode(input[5:-5])


# validate account info for login
def verify_login(email, password):
    try:
        user = UserTab.query.filter_by(email=email).first()
    except Exception as e:
        app.logger.exception(str(e))
        return InternalError.DBError, None
    if not user or decoded_pswd(user.password) != password:
        return None, False
    return None, True


# validate email format
def validate_email_format(email):
    validated = re.match(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)", email)
    return bool(validated)


# b64 encode id with random prefix and suffix
def encoded_id(input):
    input = int(input)
    hashids = Hashids(salt=SALT, min_length=16)
    return hashids.encode(input)


# b64 decode id, trim random prefix and suffix
def decoded_id(input):
    hashids = Hashids(salt=SALT, min_length=16)
    decoded = hashids.decode(input)
    if decoded:
        return decoded[0]
    return 0


# convert string type list
def convert_string_to_list(input):
    return ast.literal_eval(input)


# create a jwt token after login
def create_token(name, exp):
    headers = {
        "alg": "HS256",
        "typ": "JWT"
    }
    payload = {
        "name": name,
        "exp": exp
    }
    token = jwt.encode(payload=payload, key=SECRET_KEY, algorithm='HS256', headers=headers)\
        .encode('utf-8').decode('utf-8')
    return token


# decode the jwt token and return error or email
def validate_token(token):
    payload = None
    msg = None
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms='HS256')
    except jwt.exceptions.ExpiredSignatureError:
        msg = 'token expired'
    except jwt.DecodeError:
        msg = 'token validation fails'
    except jwt.InvalidTokenError:
        msg = 'invalid token'
    return payload, msg

# validate questions when create / update a quiz
def validate_quiz_questions(questions):
    for question in questions:
        text = str(question.get("question")).strip()
        options = question.get("options")
        answers = question.get("answers")
        single_answer = question.get("single_answer")
        # all the required fields in each question must be filled, can not create a question with over 5 answers
        if not (text and options and answers and single_answer in [0, 1]) or len(options) > 5:
            return InternalError.ParamError.value, None
        # transform type in case of non-list input
        answers, options = list(answers), list(options)
        for answer in answers:
            # answer must be any of the options
            if answer not in options:
                return InternalError.ParamError.value, None
        # single answer questions can only have one answer
        if single_answer and len(set(answers)) > 1:
            return InternalError.ParamError.value, None
        # remove duplication in options or answers
        question["options"], question["answers"] = list(set(question.get("options"))), list(set(question.get("answers")))
    return None, questions
