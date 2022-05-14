# -*- coding:utf-8 -*-

import json
import requests
import pytest

from tests.conf import PREFIX
from tests.utis import execute_sql, convert_string_to_list, decoded_id

url1 = PREFIX + "solution/list"


@pytest.mark.parametrize("email", ["automation1@quiz.com", "automation2@quiz.com", "automation3@quiz.com"])
def test_get_solution_list_success(email):
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
    sql = "select * from solution_tab where user='%s'" % email
    results_solved = execute_sql(sql)
    if not results_solved:
        assert resp["data"] == []
    else:
        solution_ids = []
        for result_solved in results_solved:
            sql = "select is_deleted from quiz_tab where id=%s" % result_solved[1]
            quiz_deleted = execute_sql(sql, fetchOne=True)
            if not quiz_deleted[0]:
                solution_ids.append(result_solved[0])
        resp_ids = [ele["id"] for ele in resp["data"]]
        assert sorted(solution_ids) == sorted(resp_ids)


@pytest.mark.parametrize("email", ["automation1@quiz.com", "automation2@quiz.com", "automation3@quiz.com"])
def test_get_solution_list_with_invalid_token_fails(email):
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


url2 = PREFIX + "solution/details"


@pytest.mark.parametrize("email", ["automation1@quiz.com", "automation2@quiz.com", "automation3@quiz.com"])
def test_get_solution_details_success(email):
    sql = "select token from user_token_tab where email='%s'" % email
    token = execute_sql(sql, fetchOne=True)[0]
    headers = {"Authorization": "Bearer %s" % token}
    sql = "select * from solution_tab where user='%s'" % email
    results_solved = execute_sql(sql)
    solution_ids = []
    for result_solved in results_solved:
        sql = "select is_deleted from quiz_tab where id=%s" % result_solved[1]
        quiz_deleted = execute_sql(sql, fetchOne=True)
        if not quiz_deleted[0]:
            solution_ids.append(result_solved[0])
    if len(solution_ids) > 2:
        solution_ids = solution_ids[:2]
    for id in solution_ids:
        params = {"id": id}
        print(params)
        resp = requests.get(url2, headers=headers, params=params, verify=False)
        print(resp.url)
        print(resp.text)
        print(resp.status_code)
        assert resp.status_code == 200
        res_dict = json.loads(resp.text)
        assert res_dict["error_code"] == 0
        sql = "select * from solution_tab where id=%s" % id
        solution_info = execute_sql(sql, fetchOne=True)
        sql = "select * from solution_answer_tab where solution_id=%s" % id
        solution_answers = execute_sql(sql)
        solution_question_ids = [solution[2] for solution in solution_answers]
        sql = "select * from quiz_tab where id=%s" % solution_info[1]
        quiz_info = execute_sql(sql, fetchOne=True)
        assert decoded_id(res_dict["data"]["quiz_id"]) == solution_info[1]
        assert res_dict["data"]["quiz_title"] == quiz_info[2]
        assert res_dict["data"]["quiz_creator"] == quiz_info[1]
        assert res_dict["data"]["user_score"] == '{:.0%}'.format(solution_info[-1]/len(solution_answers))
        resp_question_ids = [ele["question_id"] for ele in res_dict["data"]["solution"]]
        assert sorted(solution_question_ids) == sorted(resp_question_ids)
        for sol in res_dict["data"]["solution"]:
            sql = "select * from quiz_question_tab where id=%s" % sol["question_id"]
            question = execute_sql(sql, fetchOne=True)
            sql = "select * from solution_answer_tab where id=%s and question_id=%s" % (sol["id"], sol["question_id"])
            answer = execute_sql(sql, fetchOne=True)
            assert sol["question"] == question[2] and sorted(sol["options"]) == sorted(convert_string_to_list(question[3]))
            assert sol["single_answer"] == question[-1] and sorted(sol["user_answers"]) == sorted(convert_string_to_list(answer[3]))
            assert sol["user_score"] == '{:.0%}'.format(answer[-1]/1)


@pytest.mark.parametrize("email", ["automation1@quiz.com", "automation2@quiz.com", "automation3@quiz.com"])
def test_get_solution_details_with_invalid_token_fails(email):
    sql = "select token from user_token_tab where email='%s'" % email
    token = execute_sql(sql, fetchOne=True)[0]
    headers = {"Authorization": "Bearer %s" % token+"falsified"}
    sql = "select * from solution_tab where user='%s'" % email
    results_solved = execute_sql(sql)
    solution_ids = []
    for result_solved in results_solved:
        sql = "select is_deleted from quiz_tab where id=%s" % result_solved[1]
        quiz_deleted = execute_sql(sql, fetchOne=True)
        if not quiz_deleted[0]:
            solution_ids.append(result_solved[0])
    if len(solution_ids) > 2:
        solution_ids = solution_ids[:2]
    for id in solution_ids:
        params = {"id": id}
        print(params)
        resp = requests.get(url2, headers=headers, params=params, verify=False)
        print(resp.url)
        print(resp.text)
        print(resp.status_code)
        assert resp.status_code != 200
        res_dict = json.loads(resp.text)
        assert res_dict["error_code"] != 0
        assert not res_dict["data"]


@pytest.mark.parametrize("email", ["automation1@quiz.com", "automation2@quiz.com", "automation3@quiz.com"])
def test_get_solution_details_with_invalid_param_fail(email):
    sql = "select token from user_token_tab where email='%s'" % email
    token = execute_sql(sql, fetchOne=True)[0]
    headers = {"Authorization": "Bearer %s" % token}
    for id in ["", 0, None]:
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
        assert not res_dict["data"]


@pytest.mark.parametrize("email", ["automation1@quiz.com", "automation2@quiz.com", "automation3@quiz.com"])
def test_get_solution_details_with_no_param_fail(email):
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
    assert not res_dict["data"]



