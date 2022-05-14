# -*- coding:utf-8 -*-

import json
import requests
import pytest

from tests.conf import PREFIX
from tests.utis import execute_sql, convert_string_to_list, encoded_id, decoded_id

url1 = PREFIX + "quiz/solve/list"


@pytest.mark.parametrize("email", ["automation1@quiz.com", "automation3@quiz.com"])
def test_get_quiz_list_to_solve_success(email):
    sql = "select token from user_token_tab where email='%s'" % email
    token = execute_sql(sql, fetchOne=True)[0]
    headers = {"Authorization": "Bearer %s" % token}
    response = requests.get(url1, headers=headers, verify=False)
    print(response.url)
    print(response.text)
    print(response.status_code)
    assert response.status_code == 200
    resp = json.loads(response.text)
    assert resp["error_code"] == 0
    sql = "select * from quiz_tab where creator!='%s' and is_deleted=0 and published=1" % email
    results = execute_sql(sql)
    sql = "select quiz_id from solution_tab where user='%s'" % email
    results_solved = execute_sql(sql)
    if not results:
        assert resp["data"] == []
    else:
        db_quizzes = [result[0] for result in results]
        db_solved = [result_solved[0] for result_solved in results_solved]
        res_quizzes = []
        for id in db_quizzes:
            if id not in db_solved:
                res_quizzes.append(id)
        resp_quizzes = [decoded_id(ele["id"]) for ele in resp["data"]]
        assert sorted(res_quizzes) == sorted(resp_quizzes)


@pytest.mark.parametrize("email", ["automation1@quiz.com", "automation3@quiz.com"])
def test_get_quiz_list_to_solve_with_invalid_token_fails(email):
    sql = "select token from user_token_tab where email='%s'" % email
    token = execute_sql(sql, fetchOne=True)[0]
    headers = {"Authorization": "Bearer %s" % token+"_falsified"}
    response = requests.get(url1, headers=headers, verify=False)
    print(response.url)
    print(response.text)
    print(response.status_code)
    assert response.status_code != 200
    resp = json.loads(response.text)
    assert resp["error_code"] != 0
    assert not resp["data"]


url2 = PREFIX + "quiz/solve"


@pytest.mark.parametrize("email", ["automation1@quiz.com", "automation3@quiz.com"])
def test_get_quiz_details_to_solve_success(email):
    sql = "select token from user_token_tab where email='%s'" % email
    token = execute_sql(sql, fetchOne=True)[0]
    headers = {"Authorization": "Bearer %s" % token}
    sql = "select * from quiz_tab where creator!='%s' and is_deleted=0 and published=1" % email
    results = list(execute_sql(sql))
    sql = "select quiz_id from solution_tab where user='%s'" % email
    results_solved = execute_sql(sql)
    db_solved = [result_solved[0] for result_solved in results_solved]
    for idx, quiz in enumerate(results):
        if quiz[0] in db_solved:
            results.pop(idx)
    if len(results) > 2:
        results = results[:2]
    for quiz in results:
        quiz_id = encoded_id(quiz[0])
        print({"id": quiz_id})
        resp = requests.get(url2, headers=headers, params={"id": quiz_id}, verify=False)
        print(resp.url)
        print(resp.text)
        print(resp.status_code)
        assert resp.status_code == 200
        res_dict = json.loads(resp.text)
        assert res_dict["error_code"] == 0
        assert res_dict["data"]["title"] == quiz[2]
        assert res_dict["data"]["creator"] == quiz[1]
        for question in res_dict["data"]["questions"]:
            sql = "select * from quiz_question_tab where quiz_id=%s and id=%s" % (quiz[0], question["id"])
            results = execute_sql(sql, fetchOne=True)
            assert results
            assert question["question"] == results[2] and sorted(convert_string_to_list(results[3])) == sorted(question["options"]) \
                                                        and question["single_answer"] == results[5]
            assert not question.get("answers")


@pytest.mark.parametrize("email", ["automation1@quiz.com", "automation3@quiz.com"])
def test_get_quiz_details_to_solve_with_invalid_token_fails(email):
    sql = "select token from user_token_tab where email='%s'" % email
    token = execute_sql(sql, fetchOne=True)[0]
    headers = {"Authorization": "Bearer %s" % token+"falsified"}
    sql = "select * from quiz_tab where creator!='%s' and is_deleted=0 and published=1" % email
    results = list(execute_sql(sql))
    sql = "select quiz_id from solution_tab where user='%s'" % email
    results_solved = execute_sql(sql)
    db_solved = [result_solved[0] for result_solved in results_solved]
    for idx, quiz in enumerate(results):
        if quiz[0] in db_solved:
            results.pop(idx)
    if len(results) > 2:
        results = results[:2]
    for quiz in results:
        quiz_id = encoded_id(quiz[0])
        print({"id": quiz_id})
        resp = requests.get(url2, headers=headers, params={"id": quiz_id}, verify=False)
        print(resp.url)
        print(resp.text)
        print(resp.status_code)
        assert resp.status_code != 200
        res_dict = json.loads(resp.text)
        assert res_dict["error_code"] != 0
        assert not res_dict["data"]



@pytest.mark.parametrize("email", ["automation1@quiz.com", "automation3@quiz.com"])
def test_get_quiz_details_to_solve_with_invalid_param_fail(email):
    sql = "select token from user_token_tab where email='%s'" % email
    token = execute_sql(sql, fetchOne=True)[0]
    headers = {"Authorization": "Bearer %s" % token}
    sql = "select id from quiz_tab where creator!='%s' and is_deleted=0 and published=1" % email
    results = list(execute_sql(sql))
    sql = "select quiz_id from solution_tab where user='%s'" % email
    results_solved = execute_sql(sql)
    db_solved = [result_solved[0] for result_solved in results_solved]
    for idx, quiz in enumerate(results):
        print(quiz)
        if quiz[0] in db_solved:
            results.pop(idx)
    ids = ["", 0, None]
    if results:
        ids.append(results[0])
    for id in ids:
        params = {
            "id": id,
        }
        print(params)
        resp = requests.get(url2, headers=headers, params=params, verify=False)
        print(resp.url)
        print(resp.text)
        print(resp.status_code)
        assert resp.status_code != 200
        res_dict = json.loads(resp.text)
        assert res_dict["error_code"] != 0


@pytest.mark.parametrize("email", ["automation1@quiz.com", "automation3@quiz.com"])
def test_get_own_quiz_details_with_no_param_fail(email):
    sql = "select token from user_token_tab where email='%s'" % email
    token = execute_sql(sql, fetchOne=True)[0]
    headers = {"Authorization": "Bearer %s" % token}
    resp = requests.get(url2, headers=headers, verify=False)
    print(resp.url)
    print(resp.text)
    print(resp.status_code)
    assert resp.status_code != 200
    res_dict = json.loads(resp.text)
    assert res_dict["error_code"] != 0


@pytest.mark.parametrize("email", ["automation1@quiz.com", "automation3@quiz.com"])
def test_get_unpublished_quiz_details_to_solve_with_fails(email):
    sql = "select token from user_token_tab where email='%s'" % email
    token = execute_sql(sql, fetchOne=True)[0]
    headers = {"Authorization": "Bearer %s" % token}
    sql = "select * from quiz_tab where creator!='%s' and is_deleted=0 and published=0" % email
    results = list(execute_sql(sql))
    if len(results) > 2:
        results = results[:2]
    for quiz in results:
        quiz_id = encoded_id(quiz[0])
        print({"id": quiz_id})
        resp = requests.get(url2, headers=headers, params={"id": quiz_id}, verify=False)
        print(resp.url)
        print(resp.text)
        print(resp.status_code)
        assert resp.status_code != 200
        res_dict = json.loads(resp.text)
        assert res_dict["error_code"] != 0
        assert not res_dict["data"]



