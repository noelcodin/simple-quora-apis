# -*- coding:utf-8 -*-

import time
from datetime import datetime, timedelta

from model.quiz_db import UserTab, UserTokenTab, QuizTab, QuizQuestionTab, SolutionTab, SolutionAnswerTab
from common import utils


# controller for /register
def register_controller(email, password):
    # b64 encode the password with salt
    password = utils.encoded_pswd(password)
    # store the encoded password
    err, _ = UserTab.add_new_row(email, password)
    if err:
        return err, None
    return None, {"registered": email}


# controller for /login
def login_controller(email, password):
    # call the func to verify login info validation
    err, login_success = utils.verify_login(
        email=email,
        password=password
    )
    if err:
        return err.value, None
    if not login_success:
        return utils.InternalError.LoginError.value, None
    # expired in 30 days
    expiration = datetime.now() + timedelta(days=30)
    # create a jwt token
    token = utils.create_token(utils.b64_encode(email), expiration)
    err, _ = UserTokenTab.add_new_row(email, token,  int(time.mktime(expiration.timetuple())))
    if err:
        return err, None
    return None, {"token": token}


# controller for POST::/quiz
def create_quiz_controller(token, questions, title):
    # validate the jwt token
    payload, msg = utils.validate_token(token)
    if msg:
        return utils.InternalError.NotAuthenticatedUser.value, None
    # parse email
    email = utils.b64_decode(payload['name'])
    # can only create a quiz with 1-10 questions
    if not str(title).strip() or len(questions) < 1 or len(questions) > 10 or type(questions) != list:
        return utils.InternalError.ParamError.value, None
    # validate the questions
    err, questions = utils.validate_quiz_questions(questions)
    if err:
        return err, None
    # save to quiz_tab
    err, quiz_id = QuizTab.add_new_row(email, title)
    if err:
        return err, None
    # save to quiz_question_tab
    err, _ = QuizQuestionTab.add_new_rows(quiz_id, questions)
    if err:
        # delete the quiz if the questions fail to be saved
        QuizTab.delete_row_by_id(quiz_id)
        return err, None
    # all quiz ids will be returned encoded
    encoded_id = utils.encoded_id(quiz_id)
    return None, {"added": encoded_id}

# controller for POST::/quiz/update
def update_quiz_controller(token, id, questions, title):
    # validate the jwt token
    payload, msg = utils.validate_token(token)
    if msg:
        return utils.InternalError.NotAuthenticatedUser.value, None
    # parse email
    email = utils.b64_decode(payload['name'])
    quiz_id = utils.decoded_id(id)
    err, quiz_info = QuizTab.get_row_by_id(quiz_id)
    if err:
        return err, None
    if not quiz_id or not quiz_info:
        return utils.InternalError.DataNotFound.value, None
    if email != quiz_info.creator or quiz_info.published:
        return utils.InternalError.NoPermissionError.value, None
    # can only create a quiz with 1-10 questions
    if not str(title).strip() or len(questions) < 1 or len(questions) > 10 or type(questions) != list:
        return utils.InternalError.ParamError.value, None
    # validate the questions
    err, questions = utils.validate_quiz_questions(questions)
    if err:
        return err, None
    # update to quiz_tab
    err, _ = QuizTab.update_row(quiz_id, {"title": title})
    if err:
        return err, None
    # delete existing questions
    err, _ = QuizQuestionTab.delete_rows_by_quiz_id(quiz_id)
    if err:
        # delete the quiz if the questions fail to be saved
        return err, None
    # save to quiz_question_tab
    err, _ = QuizQuestionTab.add_new_rows(quiz_id, questions)
    if err:
        # delete the quiz if the questions fail to be saved
        return err, None
    # all quiz ids will be returned encoded
    return None, {"updated": id}

# controller for POST::/quiz/publish
def publish_quiz_controller(token, id):
    # validate the jwt token
    payload, msg = utils.validate_token(token)
    if msg:
        return utils.InternalError.NotAuthenticatedUser.value, None
    # parse email
    email = utils.b64_decode(payload['name'])
    quiz_id = utils.decoded_id(id)
    err, quiz_info = QuizTab.get_row_by_id(quiz_id)
    if err:
        return err, None
    if quiz_info.is_deleted:
        return utils.InternalError.DataNotFound.value, None
    if email != quiz_info.creator:
        return utils.InternalError.NoPermissionError.value, None
    err, _ = QuizTab.update_row(quiz_id, {"published": 1})
    if err:
        return err, None
    return None, {"published": id}

# controller for DELETE::/quiz
def delete_quiz_controller(token, id):
    # validate jwt token
    payload, msg = utils.validate_token(token)
    if msg:
        return utils.InternalError.NotAuthenticatedUser.value, None
    email = utils.b64_decode(payload['name'])
    # decode the quiz id passed by user
    quiz_id = utils.decoded_id(str(id))
    err, quiz_info = QuizTab.get_row_by_id(quiz_id)
    if err:
        return err, None
    # only quiz owner is allowed to delete
    if email != quiz_info.creator:
        return utils.InternalError.NoPermissionError.value, None
    # quiz will be soft deleted
    err, _ = QuizTab.soft_delete_row_by_id(quiz_id)
    if err:
        return err, None
    return None, {}

# controller for GET::/quiz
def get_own_quizzes_controller(token):
    # validate jwt token
    payload, msg = utils.validate_token(token)
    if msg:
        return utils.InternalError.NotAuthenticatedUser.value, None
    email = utils.b64_decode(payload['name'])
    res = []
    # get a list of undeleted quizzes created by user
    err, quiz_objs = QuizTab.get_rows_filter_by_creator(email)
    if err:
        return err, None
    # fetch each quiz's details
    for quiz in quiz_objs:
        id = utils.encoded_id(quiz.id)
        err, quiz_details = get_own_quiz_details_controller(token, id)
        if err:
            return err, None
        quiz_details["question_count"] = len(quiz_details.pop("questions"))
        res.append(quiz_details)
    return None, res


# controller for GET::/quiz/details
def get_own_quiz_details_controller(token, id):
    # validate jwt token
    payload, msg = utils.validate_token(token)
    if msg:
        return utils.InternalError.NotAuthenticatedUser.value, None
    email = utils.b64_decode(payload['name'])
    # decode the quiz id passed by user
    quiz_id = utils.decoded_id(id)
    # fetch quiz info
    err, quiz_obj = QuizTab.get_row_by_id(quiz_id)
    if err:
        return err, None
    # if quiz id does not exist
    if not quiz_obj:
        return utils.InternalError.DataNotFound.value, None
    # only quiz owner is allowed to fetch the details with answers
    if quiz_obj.creator != email:
        return utils.InternalError.NoPermissionError.value, None
    err, questions = QuizQuestionTab.filter_rows_by_quiz_id(quiz_id)
    if err:
        return err, None
    questions_temp = []
    # assemble question json
    for question in questions:
        question_temp = {
            "id": question.id,
            "question": question.question,
            "options": utils.convert_string_to_list(question.options),
            "answers": utils.convert_string_to_list(question.answers),
            "single_answer": question.single_answer
        }
        questions_temp.append(question_temp)
    return None, {"id": id, "title": quiz_obj.title, "creator": quiz_obj.creator, "published": quiz_obj.published,
                  "questions": questions_temp}


# controller for GET::/quiz/solve/list
def get_quizzes_to_solve(token):
    # validate jwt token
    payload, msg = utils.validate_token(token)
    if msg:
        return utils.InternalError.NotAuthenticatedUser.value, None
    email = utils.b64_decode(payload['name'])
    # fetch a list of quizzes not created by user
    err, quizzes = QuizTab.get_rows_not_as_creator(email)
    if err:
        return err, None
    # no available quiz
    if not quizzes:
        return None, []
    res = []
    for quiz in quizzes:
        # filter out the quizzes user already submitted a solution
        err, solved = SolutionTab.get_rows_filter_by_user_and_quiz_id(email, quiz.id)
        if err:
            return err, None
        if not solved:
            # if user has not submitted a solution, add in quiz details with no answer
            err, quiz_info = get_a_quiz_to_solve(token, utils.encoded_id(quiz.id))
            if err:
                return err, None
            quiz_info["question_count"] = len(quiz_info.pop("questions"))
            res.append(quiz_info)
    return None, res

# controller for GET::/quiz/solve
def get_a_quiz_to_solve(token, quiz_id):
    # validate jwt token
    payload, msg = utils.validate_token(token)
    if msg:
        return utils.InternalError.NotAuthenticatedUser.value, None
    email = utils.b64_decode(payload['name'])
    # decode quiz id passed by user
    id = utils.decoded_id(quiz_id)
    # fetch quiz info
    err, quiz_info = QuizTab.get_row_by_id(id)
    if err:
        return err, None
    if not quiz_info.published:
        return utils.InternalError.NoPermissionError.value, None
    # fetch quiz questions
    err, questions = QuizQuestionTab.filter_rows_by_quiz_id(id)
    if err:
        return err, None
    question_temp = []
    # assemble question json
    for question in questions:
        question_temp.append({
            "id": question.id,
            "question": question.question,
            "options": utils.convert_string_to_list(question.options),
            "single_answer": question.single_answer
        })
    return None, {"id": quiz_id, "title": quiz_info.title, "creator": quiz_info.creator, "questions": question_temp}


# controller for POST::/quiz/solve
def submit_solution_controller(token, id, solution):
    # validate jwt token
    payload, msg = utils.validate_token(token)
    if msg:
        return utils.InternalError.NotAuthenticatedUser.value, None
    email = utils.b64_decode(payload['name'])
    # decode the quiz id passed by user
    quiz_id = utils.decoded_id(str(id))
    # fetch quiz info
    err, quiz_info = QuizTab.get_row_by_id(quiz_id)
    if err:
        return err, None
    # block submit if the quiz gets deleted or does not exist
    if quiz_info.is_deleted or not quiz_info:
        return utils.InternalError.DataNotFound.value, None
    # check if user has submitted a solution to the quiz
    err, solved = SolutionTab.get_rows_filter_by_user_and_quiz_id(email, quiz_id)
    if err:
        return err, None
    # block submit if user is the creator or user has solved the quiz before
    # or the quiz is not published
    if not quiz_info.published or solved or email == quiz_info.creator:
        return utils.InternalError.NoPermissionError.value, None
    # fetch quiz question
    err, questions = QuizQuestionTab.filter_rows_by_quiz_id(quiz_id)
    if err:
        return err, None
    # question ids in quiz and answer should match
    question_ids = [str(question.id) for question in questions]
    if type(solution) != list:
        return utils.InternalError.ParamError.value, None
    answer_ids = [str(answer.get("question_id")) for answer in solution]
    # block submit if the answer json is not valid
    if type(answer_ids) != list:
        return utils.InternalError.ParamError.value, None
    if sorted(question_ids) != sorted(answer_ids):
        return utils.InternalError.ParamError.value, None
    solution_answers = []
    total_score = 0
    for sol in solution:
        question_id = sol.get("question_id")
        answers = sol.get("answers")
        # validate each solution format 
        if not (question_id and type(answers) == list):
            return utils.InternalError.ParamError.value, None
        # reduce duplications in answers
        answers = list(set(answers))
        err, question = QuizQuestionTab.get_row_by_id(question_id)
        if err:
            return err, None
        # fetch options and answers of quiz and convert to list
        answers_of_question = utils.convert_string_to_list(question.answers)
        options_of_question = utils.convert_string_to_list(question.options)
        for ele in answers:
            # submitted answer must be any of the quiz options
            if ele not in options_of_question:
                return utils.InternalError.ParamError.value, None
        # return error if user submits multiple answers to a single-answer question
        if question.single_answer and len(answers) > 1:
            return utils.InternalError.ParamError.value, None
        # score 0 if skip the question
        if not answers:
            score = 0
        # for single-answer questions, user will score 1/-1 if not skip it
        elif question.single_answer:
            if sorted(answers) == sorted(answers_of_question):
                score = 1
            else:
                score = -1
        else:
            # for multiple-answer questions, user's each correct answer will score 1/answers
            # each wrong answer will score -1/(options=answers) if not skip it
            score = 0
            right_answer = len(answers_of_question)
            wrong_answer = len(options_of_question) - right_answer
            for ele in answers:
                if ele in answers_of_question:
                    score += 1/right_answer
                else:
                    score -= 1/wrong_answer
        # add question score upon total score
        total_score += score
        solution_answers.append({"question_id": question_id, "answers": str(answers), "score": round(score, 2)})
    # save the solution 
    err, solution_id = SolutionTab.add_new_row(email, quiz_id, round(total_score, 2))
    if err:
        return err, None
    # save the solution answers
    err, _ = SolutionAnswerTab.add_new_rows(solution_id, solution_answers)
    if err:
        # when fail to save the solution answers, delete the saved solution instance
        SolutionTab.delete_row_by_id(solution_id)
        return err, None
    # after submit a solution successfully, return the solution details
    err, solution_details = get_own_solution_details(token, solution_id)
    if err:
        return err, None
    return None, solution_details


# controller for GET::/solution/details
def get_own_solution_details(token, id):
    # validate solution details
    payload, msg = utils.validate_token(token)
    if msg:
        return utils.InternalError.NotAuthenticatedUser.value, None
    email = utils.b64_decode(payload['name'])
    # fetch solution info
    err, solution_info = SolutionTab.get_row_by_id(id)
    if err:
        return err, None
    # fetch solution answers
    err, solution_answers = SolutionAnswerTab.filter_rows_by_solution_id(id)
    if err:
        return err, None
    # fetch the quiz info
    err, quiz_info = QuizTab.get_row_by_id(solution_info.quiz_id)
    if err:
        return err, None
    # only quiz owner or solution submit user is allowed to check the solution details
    if email != quiz_info.creator and email != solution_info.user:
        return utils.InternalError.NoPermissionError.value, None
    # fetch the quiz questions
    err, quiz_questions = QuizQuestionTab.filter_rows_by_quiz_id(solution_info.quiz_id)
    if err:
        return err, None
    answer_temp = []
    quiz_score = 0
    # assemble the solution answer json
    for answer in solution_answers:
        quiz_score += 1
        question_id = answer.question_id
        err, question_info = QuizQuestionTab.get_row_by_id(question_id)
        answer_temp.append({
            "id": answer.id,
            "question_id": question_id,
            "question": question_info.question,
            "options": utils.convert_string_to_list(question_info.options),
            "single_answer": question_info.single_answer,
            "user_answers": utils.convert_string_to_list(answer.answers),
            "user_score": '{:.0%}'.format(answer.score/1)
        })
    return None, {"id": id, "quiz_id": utils.encoded_id(solution_info.quiz_id), "quiz_title": quiz_info.title, 
                  "quiz_creator": quiz_info.creator, "solution": answer_temp, "user_score": '{:.0%}'.format(solution_info.score/quiz_score)}


# controller for GET::/solution/list
def get_own_solution_list(token):
    # validate jwt token
    payload, msg = utils.validate_token(token)
    if msg:
        return utils.InternalError.NotAuthenticatedUser.value, None
    email = utils.b64_decode(payload['name'])
    # fetch a list of solutions submitted by user
    err, solutions = SolutionTab.get_rows_filter_by_user(email)
    res = []
    for solution in solutions:
        err, quiz_info = QuizTab.get_row_by_id(solution.quiz_id)
        if err:
            return err, None
        # filter out the solution if the quiz gets deleted
        if quiz_info.is_deleted:
            continue
        # fetch the solution details
        err, solution_info = get_own_solution_details(token, solution.id)
        if err:
            return err, None
        solution_info.pop("solution")
        res.append(solution_info)
    return None, res

# controller for GET::/solution/my_quizzes
def get_own_solution_to_quizzes_mapping_controller(token):
    # validate jwt token
    payload, msg = utils.validate_token(token)
    if msg:
        return utils.InternalError.NotAuthenticatedUser.value, None
    email = utils.b64_decode(payload['name'])
    res = []
    # fetch a list of quizzes created by user
    err, quiz_objs = QuizTab.get_published_rows_filter_by_creator(email)
    if err:
        return err, None
    for quiz in quiz_objs:
        # fetch a list of solutions submitted to the quiz
        err, solutions = SolutionTab.get_rows_filter_by_quiz_id(quiz.id)
        if err:
            return err, None
        solutions_temp = []
        for solution in solutions:
            total_score = 0
            err, solution_answers = SolutionAnswerTab.filter_rows_by_solution_id(solution.id)
            if err:
                return err, None
            for _ in solution_answers:
                total_score += 1
            solutions_temp.append({"solution_id": solution.id, "score": '{:.0%}'.format(solution.score/total_score),
                                   "submitted_user": solution.user})
        res.append({"quiz_id": utils.encoded_id(quiz.id), "title": quiz.title, 
                    "creator": quiz.creator, "submitted_solutions": solutions_temp})
    return None, res
