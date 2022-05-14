# -*- coding:utf-8 -*-

import copy
import json
import requests
import pytest
import random

from tests.conf import PREFIX
from tests.utis import execute_sql, convert_string_to_list, encoded_id, decoded_id

url = PREFIX + "quiz/solve"


@pytest.mark.run(order=7)
@pytest.mark.parametrize("email", ["automation3@quiz.com", "automation2@quiz.com"])
def test_submit_success(email):
    for i in range(3):
        sql = "select token from user_token_tab where email='%s'" % email
        token = execute_sql(sql, fetchOne=True)[0]
        headers = {"Authorization": "Bearer %s" % token}
        sql = "select * from quiz_tab where creator!='%s' and is_deleted!=1 and published=1" % email
        results = execute_sql(sql)
        sql = "select * from solution_tab where user='%s'" % email
        results_solved = execute_sql(sql)
        db_solved = [result_solved[1] for result_solved in results_solved]
        score_map = {}
        for quiz in results:
            if quiz[0] not in db_solved:
                total_score = 0
                data = {
                    "id": encoded_id(quiz[0]),
                    "solution": []
                }
                sql = "select * from quiz_question_tab where quiz_id=%s" % quiz[0]
                questions = execute_sql(sql)
                question_ids = []
                for question in questions:
                    right_answers = convert_string_to_list(question[4])
                    wrong_answers = []
                    options = convert_string_to_list(question[3])
                    for answer in options:
                        if answer not in right_answers:
                            wrong_answers.append(answer)
                    if question[-1]:
                        random_answer = random.choice([(1, right_answers), (0, []),
                                                       (-1, [wrong_answers[random.randint(0, len(wrong_answers)-1)]])])
                        score = random_answer[0]
                        answer_list = random_answer[1]
                    else:
                        score_temp = 0
                        random_answer_temp = []
                        for i in range(random.randint(0, len(options)-1)):
                            choice = options[random.randint(0, len(options)-1)]
                            if choice in right_answers and choice not in random_answer_temp:
                                score_temp += 1/len(right_answers)
                            elif choice in wrong_answers and choice not in random_answer_temp:
                                score_temp -= 1/len(wrong_answers)
                            random_answer_temp.append(choice)

                        random_answer = random.choice([(1, right_answers), (-1, wrong_answers), (0, []),
                                                       (round(score_temp, 2), random_answer_temp)])
                        score = random_answer[0]
                        answer_list = random_answer[1]
                    score_map[question[0]] = round(score, 2)
                    total_score += score
                    data["solution"].append({
                        "question_id": question[0],
                        "answers": answer_list
                    })
                    question_ids.append(question[0])
                print(data)
                resp = requests.post(url, json=data, headers=headers, verify=False)
                print(resp.url)
                print(resp.text)
                print(resp.status_code)
                assert resp.status_code == 201
                res_dict = json.loads(resp.text)
                assert res_dict.get("error_code") == 0
                for answer in res_dict["data"]["solution"]:
                    assert answer["question_id"] in question_ids
                    assert answer["user_score"] == '{:.0%}'.format(score_map[answer["question_id"]]/1)
                assert decoded_id(res_dict["data"]["quiz_id"]) == quiz[0] and res_dict["data"]["quiz_title"] \
                       == quiz[2] and res_dict["data"]["quiz_creator"] == quiz[1] \
                       and res_dict["data"]["user_score"] == '{:.0%}'.format(round(total_score, 2)/len(data["solution"]))
                break


@pytest.mark.parametrize("email", ["automation3@quiz.com", "automation2@quiz.com"])
def test_submit_with_invalid_token_fail(email):
    sql = "select token from user_token_tab where email='%s'" % email
    token = execute_sql(sql, fetchOne=True)[0]
    headers = {"Authorization": "Bearer %s" % token+"falsified"}
    sql = "select * from quiz_tab where creator!='%s' and is_deleted!=1 and published=1" % email
    results = execute_sql(sql)
    sql = "select * from solution_tab where user='%s'" % email
    results_solved = execute_sql(sql)
    db_solved = [result_solved[1] for result_solved in results_solved]
    for quiz in results:
        if quiz[0] not in db_solved:
            data = {
                "id": encoded_id(quiz[0]),
                "solution": []
            }
            sql = "select * from quiz_question_tab where quiz_id=%s" % quiz[0]
            questions = execute_sql(sql)
            question_ids = []
            for question in questions:
                right_answers = convert_string_to_list(question[4])
                answer_list = right_answers
                data["solution"].append({
                    "question_id": question[0],
                    "answers": answer_list
                })
                question_ids.append(question[0])
            print(data)
            resp = requests.post(url, json=data, headers=headers, verify=False)
            print(resp.url)
            print(resp.text)
            print(resp.status_code)
            assert resp.status_code != 201
            res_dict = json.loads(resp.text)
            assert res_dict["error_code"] != 0 and not res_dict["data"]
            break


@pytest.mark.parametrize("email", ["automation3@quiz.com", "automation2@quiz.com"])
def test_submit_with_answer_not_in_options_fail(email):
    sql = "select token from user_token_tab where email='%s'" % email
    token = execute_sql(sql, fetchOne=True)[0]
    headers = {"Authorization": "Bearer %s" % token}
    sql = "select * from quiz_tab where creator!='%s' and is_deleted!=1 and published=1" % email
    results = execute_sql(sql)
    sql = "select * from solution_tab where user='%s'" % email
    results_solved = execute_sql(sql)
    db_solved = [result_solved[1] for result_solved in results_solved]
    for quiz in results:
        if quiz[0] not in db_solved:
            data = {
                "id": encoded_id(quiz[0]),
                "solution": []
            }
            sql = "select * from quiz_question_tab where quiz_id=%s" % quiz[0]
            questions = execute_sql(sql)
            question_ids = []
            for question in questions:
                right_answers = convert_string_to_list(question[4])
                answer_list = right_answers
                idx = random.randint(0, len(answer_list)-1)
                answer_list[idx] = "%s_updated_%s" % (answer_list[idx], random.randint(0, 10000))
                data["solution"].append({
                    "question_id": question[0],
                    "answers": answer_list
                })
                question_ids.append(question[0])
            print(data)
            resp = requests.post(url, json=data, headers=headers, verify=False)
            print(resp.url)
            print(resp.text)
            print(resp.status_code)
            assert resp.status_code != 201
            res_dict = json.loads(resp.text)
            assert res_dict["error_code"] != 0 and not res_dict["data"]
            break


@pytest.mark.parametrize("email", ["automation3@quiz.com", "automation2@quiz.com"])
def test_submit_with_mutiple_answer_for_single_answer_question_fail(email):
    sql = "select token from user_token_tab where email='%s'" % email
    token = execute_sql(sql, fetchOne=True)[0]
    headers = {"Authorization": "Bearer %s" % token}
    sql = "select * from quiz_tab where creator!='%s' and is_deleted!=1 and published=1" % email
    results = execute_sql(sql)
    sql = "select * from solution_tab where user='%s'" % email
    results_solved = execute_sql(sql)
    db_solved = [result_solved[1] for result_solved in results_solved]
    for quiz in results:
        if quiz[0] not in db_solved:
            data = {
                "id": encoded_id(quiz[0]),
                "solution": []
            }
            sql = "select * from quiz_question_tab where quiz_id=%s" % quiz[0]
            questions = execute_sql(sql)
            question_ids = []
            for question in questions:
                options = convert_string_to_list(question[3])
                data["solution"].append({
                    "question_id": question[0],
                    "answers": options
                })
                question_ids.append(question[0])
            print(data)
            resp = requests.post(url, json=data, headers=headers, verify=False)
            print(resp.url)
            print(resp.text)
            print(resp.status_code)
            assert resp.status_code != 201
            res_dict = json.loads(resp.text)
            assert res_dict["error_code"] != 0 and not res_dict["data"]
            break


@pytest.mark.parametrize("email", ["automation3@quiz.com", "automation2@quiz.com"])
@pytest.mark.parametrize("value", ["", " ", [], None])
def test_submit_with_invalid_solution_fields_fail(email, value):
    sql = "select token from user_token_tab where email='%s'" % email
    token = execute_sql(sql, fetchOne=True)[0]
    headers = {"Authorization": "Bearer %s" % token}
    sql = "select * from quiz_tab where creator!='%s' and is_deleted!=1 and published=1" % email
    results = execute_sql(sql)
    sql = "select * from solution_tab where user='%s'" % email
    results_solved = execute_sql(sql)
    db_solved = [result_solved[1] for result_solved in results_solved]
    for quiz in results:
        if quiz[0] not in db_solved:
            data = {
                "id": encoded_id(quiz[0]),
                "solution": []
            }
            sql = "select * from quiz_question_tab where quiz_id=%s" % quiz[0]
            questions = execute_sql(sql)
            question_ids = []
            for question in questions:
                right_answers = convert_string_to_list(question[4])
                data["solution"].append({
                    "question_id": question[0],
                    "answers": right_answers
                })
                question_ids.append(question[0])
            for key in data["solution"][0].keys():
                if key == "answers" and value == []:
                    continue
                data_temp = copy.deepcopy(data)
                data_temp["solution"][random.randint(0, len(data_temp["solution"])-1)][key] = value
                print(data_temp)
                resp = requests.post(url, json=data_temp, headers=headers, verify=False)
                print(resp.url)
                print(resp.text)
                print(resp.status_code)
                assert resp.status_code != 201
                res_dict = json.loads(resp.text)
                assert res_dict["error_code"] != 0 and not res_dict["data"]
            break


@pytest.mark.parametrize("email", ["automation3@quiz.com", "automation2@quiz.com"])
@pytest.mark.parametrize("value", ["", " ", [], None])
def test_submit_with_invalid_outer_fields_fail(email, value):
    sql = "select token from user_token_tab where email='%s'" % email
    token = execute_sql(sql, fetchOne=True)[0]
    headers = {"Authorization": "Bearer %s" % token}
    sql = "select * from quiz_tab where creator!='%s' and is_deleted!=1 and published=1" % email
    results = execute_sql(sql)
    sql = "select * from solution_tab where user='%s'" % email
    results_solved = execute_sql(sql)
    db_solved = [result_solved[1] for result_solved in results_solved]
    for quiz in results:
        if quiz[0] not in db_solved:
            data = {
                "id": encoded_id(quiz[0]),
                "solution": []
            }
            sql = "select * from quiz_question_tab where quiz_id=%s" % quiz[0]
            questions = execute_sql(sql)
            question_ids = []
            for question in questions:
                right_answers = convert_string_to_list(question[4])
                data["solution"].append({
                    "question_id": question[0],
                    "answers": right_answers
                })
                question_ids.append(question[0])
            for key in data.keys():
                data_temp = copy.deepcopy(data)
                data_temp[key] = value
                print(data_temp)
                resp = requests.post(url, json=data_temp, headers=headers, verify=False)
                print(resp.url)
                print(resp.text)
                print(resp.status_code)
                assert resp.status_code != 201
                res_dict = json.loads(resp.text)
                assert res_dict["error_code"] != 0 and not res_dict["data"]
            break


@pytest.mark.parametrize("email", ["automation3@quiz.com", "automation2@quiz.com"])
def test_submit_with_outer_fields_skipped_fail(email):
    sql = "select token from user_token_tab where email='%s'" % email
    token = execute_sql(sql, fetchOne=True)[0]
    headers = {"Authorization": "Bearer %s" % token}
    sql = "select * from quiz_tab where creator!='%s' and is_deleted!=1 and published=1" % email
    results = execute_sql(sql)
    sql = "select * from solution_tab where user='%s'" % email
    results_solved = execute_sql(sql)
    db_solved = [result_solved[1] for result_solved in results_solved]
    for quiz in results:
        if quiz[0] not in db_solved:
            data = {
                "id": encoded_id(quiz[0]),
                "solution": []
            }
            sql = "select * from quiz_question_tab where quiz_id=%s" % quiz[0]
            questions = execute_sql(sql)
            question_ids = []
            for question in questions:
                right_answers = convert_string_to_list(question[4])
                data["solution"].append({
                    "question_id": question[0],
                    "answers": right_answers
                })
                question_ids.append(question[0])
            for key in data.keys():
                data_temp = copy.deepcopy(data)
                data_temp.pop(key)
                print(data_temp)
                resp = requests.post(url, json=data_temp, headers=headers, verify=False)
                print(resp.url)
                print(resp.text)
                print(resp.status_code)
                assert resp.status_code != 201
                res_dict = json.loads(resp.text)
                assert res_dict["error_code"] != 0 and not res_dict["data"]
            break


@pytest.mark.parametrize("email", ["automation3@quiz.com", "automation2@quiz.com"])
def test_submit_with_solution_fields_skipped_fail(email):
    sql = "select token from user_token_tab where email='%s'" % email
    token = execute_sql(sql, fetchOne=True)[0]
    headers = {"Authorization": "Bearer %s" % token}
    sql = "select * from quiz_tab where creator!='%s' and is_deleted!=1 and published=1" % email
    results = execute_sql(sql)
    sql = "select * from solution_tab where user='%s'" % email
    results_solved = execute_sql(sql)
    db_solved = [result_solved[1] for result_solved in results_solved]
    for quiz in results:
        if quiz[0] not in db_solved:
            data = {
                "id": encoded_id(quiz[0]),
                "solution": []
            }
            sql = "select * from quiz_question_tab where quiz_id=%s" % quiz[0]
            questions = execute_sql(sql)
            question_ids = []
            for question in questions:
                right_answers = convert_string_to_list(question[4])
                data["solution"].append({
                    "question_id": question[0],
                    "answers": right_answers
                })
                question_ids.append(question[0])
            for key in data["solution"][0].keys():
                data_temp = copy.deepcopy(data)
                data_temp["solution"][random.randint(0, len(data_temp["solution"])-1)].pop(key)
                print(data_temp)
                resp = requests.post(url, json=data_temp, headers=headers, verify=False)
                print(resp.url)
                print(resp.text)
                print(resp.status_code)
                assert resp.status_code != 201
                res_dict = json.loads(resp.text)
                assert res_dict["error_code"] != 0 and not res_dict["data"]
            break


@pytest.mark.parametrize("email", ["automation3@quiz.com", "automation2@quiz.com"])
def test_submit_to_unpublished_quizzes_fail(email):
    sql = "select token from user_token_tab where email='%s'" % email
    token = execute_sql(sql, fetchOne=True)[0]
    headers = {"Authorization": "Bearer %s" % token+"falsified"}
    sql = "select * from quiz_tab where creator!='%s' and is_deleted!=1 and published=0" % email
    results = execute_sql(sql)
    for quiz in results:
        data = {
            "id": encoded_id(quiz[0]),
            "solution": []
        }
        sql = "select * from quiz_question_tab where quiz_id=%s" % quiz[0]
        questions = execute_sql(sql)
        question_ids = []
        for question in questions:
            right_answers = convert_string_to_list(question[4])
            answer_list = right_answers
            data["solution"].append({
                "question_id": question[0],
                "answers": answer_list
            })
            question_ids.append(question[0])
        print(data)
        resp = requests.post(url, json=data, headers=headers, verify=False)
        print(resp.url)
        print(resp.text)
        print(resp.status_code)
        assert resp.status_code != 201
        res_dict = json.loads(resp.text)
        assert res_dict["error_code"] != 0 and not res_dict["data"]
        break