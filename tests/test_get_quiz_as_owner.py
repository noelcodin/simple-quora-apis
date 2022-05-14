# -*- coding:utf-8 -*-

import json
import requests
import pytest

from tests.conf import PREFIX
from tests.utis import execute_sql, convert_string_to_list, decoded_id, encoded_id

url1 = PREFIX + "quiz"


@pytest.mark.parametrize("email", ["automation1@quiz.com", "automation3@quiz.com"])
def test_get_own_quiz_list(email):
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
    sql = "select * from quiz_tab where creator='%s' and is_deleted=0" % email
    results = execute_sql(sql)
    if not results:
        assert resp["data"] == []
    else:
        assert len(resp["data"]) == len(results)
        db_quizzes = [result[0] for result in results]
        resp_quizzes = [decoded_id(ele["id"]) for ele in resp["data"]]
        assert sorted(db_quizzes) == sorted(resp_quizzes)


@pytest.mark.parametrize("email", ["automation1@quiz.com", "automation3@quiz.com"])
def test_get_own_quiz_list_with_invalid_token_fails(email):
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


url2 = PREFIX + "quiz/details"


@pytest.mark.parametrize("email", ["automation1@quiz.com", "automation3@quiz.com"])
def test_get_own_quiz_details_success(email):
    sql = "select token from user_token_tab where email='%s'" % email
    token = execute_sql(sql, fetchOne=True)[0]
    headers = {"Authorization": "Bearer %s" % token}
    sql = "select * from quiz_tab where creator='%s' and is_deleted=0" % email
    results = execute_sql(sql)
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
        assert res_dict["data"]["published"] == quiz[-1]
        for question in res_dict["data"]["questions"]:
            sql = "select * from quiz_question_tab where quiz_id=%s and id=%s" % (quiz[0], question["id"])
            results = execute_sql(sql, fetchOne=True)
            assert results
            assert question["question"] == results[2] and sorted(convert_string_to_list(results[3])) \
                == sorted(question["options"]) and sorted(convert_string_to_list(results[4])) \
                == sorted(question["answers"]) and question["single_answer"] == results[5]


@pytest.mark.parametrize("email", ["automation1@quiz.com", "automation3@quiz.com"])
def test_get_other_quiz_details_as_owner_fail(email):
    sql = "select token from user_token_tab where email='%s'" % email
    token = execute_sql(sql, fetchOne=True)[0]
    headers = {"Authorization": "Bearer %s" % token}
    sql = "select * from quiz_tab where creator!='%s' and is_deleted=0" % email
    results = execute_sql(sql)
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
def test_get_other_quiz_details_with_invalid_toke__fail(email):
    sql = "select token from user_token_tab where email='%s'" % email
    token = execute_sql(sql, fetchOne=True)[0]
    headers = {"Authorization": "Bearer %s" % token+"falsified"}
    sql = "select * from quiz_tab where creator='%s' and is_deleted=0" % email
    results = execute_sql(sql)
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
def test_get_own_quiz_details_with_invalid_param_fail(email):
    sql = "select token from user_token_tab where email='%s'" % email
    token = execute_sql(sql, fetchOne=True)[0]
    headers = {"Authorization": "Bearer %s" % token}
    sql = "select id from quiz_tab where creator='%s' and is_deleted=0" % email
    results = execute_sql(sql, fetchOne=True)
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





