# -*- coding:utf-8 -*-

import json
import requests
import pytest

from tests.conf import PREFIX
from tests.utis import execute_sql, encoded_id

url = PREFIX + "quiz/publish"


@pytest.mark.run(order=6)
@pytest.mark.parametrize("email", ["automation1@quiz.com", "automation2@quiz.com"])
def test_publish_success(email):
    sql = "select token from user_token_tab where email='%s'" % email
    token = execute_sql(sql, fetchOne=True)[0]
    headers = {"Authorization": "Bearer %s" % token}
    for i in range(6):
        sql = "select id from quiz_tab where creator='%s' and is_deleted=0 and published=0" % email
        results = execute_sql(sql, fetchOne=True)
        params = {
            "id": encoded_id(results[0]),
        }
        print(params)
        resp = requests.post(url, params=params, headers=headers, verify=False)
        print(resp.url)
        print(resp.text)
        print(resp.status_code)
        assert resp.status_code == 201
        res_dict = json.loads(resp.text)
        assert res_dict["error_code"] == 0
        sql = "select published from quiz_tab where id = %s" % results[0]
        results = execute_sql(sql, fetchOne=True)
        assert results[0] == 1


@pytest.mark.parametrize("email", ["automation1@quiz.com", "automation2@quiz.com"])
def test_publish_with_invalid_token_fail(email):
    sql = "select token from user_token_tab where email='%s'" % email
    token = execute_sql(sql, fetchOne=True)[0]
    headers = {"Authorization": "Bearer %s" % token + "falsified"}
    sql = "select id from quiz_tab where creator='%s' and is_deleted=0 and published=0" % email
    results = execute_sql(sql, fetchOne=True)
    params = {
        "id": encoded_id(results[0]),
    }
    print(params)
    resp = requests.post(url, params=params, headers=headers, verify=False)
    print(resp.url)
    print(resp.text)
    print(resp.status_code)
    assert resp.status_code != 201
    res_dict = json.loads(resp.text)
    assert res_dict["error_code"] != 0
    sql = "select published from quiz_tab where id = %s" % results[0]
    results = execute_sql(sql, fetchOne=True)
    assert results[0] == 0


@pytest.mark.parametrize("email", ["automation1@quiz.com", "automation2@quiz.com"])
def test_publish_others_created_quiz_fail(email):
    sql = "select token from user_token_tab where email='%s'" % email
    token = execute_sql(sql, fetchOne=True)[0]
    headers = {"Authorization": "Bearer %s" % token}
    sql = "select id from quiz_tab where creator!='%s' and is_deleted=0 and published=0" % email
    results = execute_sql(sql, fetchOne=True)
    params = {
        "id": encoded_id(results[0]),
    }
    print(params)
    resp = requests.post(url, params=params, headers=headers, verify=False)
    print(resp.url)
    print(resp.text)
    print(resp.status_code)
    assert resp.status_code != 201
    res_dict = json.loads(resp.text)
    assert res_dict["error_code"] != 0
    sql = "select published from quiz_tab where id = %s" % results[0]
    results = execute_sql(sql, fetchOne=True)
    assert results[0] == 0


@pytest.mark.parametrize("email", ["automation1@quiz.com", "automation2@quiz.com"])
def test_post_with_invalid_param_fail(email):
    sql = "select token from user_token_tab where email='%s'" % email
    token = execute_sql(sql, fetchOne=True)[0]
    headers = {"Authorization": "Bearer %s" % token}
    sql = "select id from quiz_tab where creator='%s' and is_deleted=0 and published=0" % email
    results = execute_sql(sql, fetchOne=True)
    ids = ["", 0, None]
    if results:
        ids.append(results[0])
    for id in ids:
        params = {
            "id": id,
        }
        print(params)
        resp = requests.post(url, params=params, headers=headers, verify=False)
        print(resp.url)
        print(resp.text)
        print(resp.status_code)
        assert resp.status_code != 201
        res_dict = json.loads(resp.text)
        assert res_dict["error_code"] != 0



@pytest.mark.parametrize("email", ["automation1@quiz.com", "automation2@quiz.com"])
def test_publish_with_no_param_fail(email):
    sql = "select token from user_token_tab where email='%s'" % email
    token = execute_sql(sql, fetchOne=True)[0]
    headers = {"Authorization": "Bearer %s" % token}
    resp = requests.post(url, headers=headers, verify=False)
    print(resp.url)
    print(resp.text)
    print(resp.status_code)
    assert resp.status_code != 201
    res_dict = json.loads(resp.text)
    assert res_dict["error_code"] != 0





