# -*- coding:utf-8 -*-

import base64
import ast
import pymysql
from hashids import Hashids
from tests.conf import SALT

def execute_sql(sql, commit=False, fetchOne=False):
    # Open database connection
    db = pymysql.connect(host='localhost', user="root", password="root", database="quiz_db")
    # prepare a cursor object using cursor() method
    cursor = db.cursor()
    # execute SQL query using execute() method.
    cursor.execute(sql)
    if commit:
        db.commit()

    if fetchOne:
        # Fetch a single row using fetchone() method.
        data = cursor.fetchone()
    else:
        data = cursor.fetchall()
    # disconnect from server
    db.close()
    return data

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

# b64 encode strings
def b64_encode(input):
    return base64.b64encode(input.encode('ascii')).decode('ascii')


# b64 decode strings
def b64_decode(input):
    return base64.b64decode(input.encode('ascii')).decode('ascii')