# -*- coding:utf-8 -*-

import json
import requests
import pytest

from tests.conf import PREFIX
from tests.utis import execute_sql, encoded_id

url = PREFIX + "quiz"


@pytest.mark.parametrize("email", ["automation1@quiz.com", "automation2@quiz.com"])
def test_delete_success(email):
    sql = "select token from user_token_tab where email='%s'" % email
    token = execute_sql(sql, fetchOne=True)[0]
    headers = {"Authorization": "Bearer %s" % token}
    sql = "select id from quiz_tab where creator='%s' and is_deleted=0" % email
    results = execute_sql(sql, fetchOne=True)
    params = {
        "id": encoded_id(str(results[0])),
    }
    print(params)
    resp = requests.delete(url, params=params, headers=headers, verify=False)
    print(resp.url)
    print(resp.text)
    print(resp.status_code)
    assert resp.status_code == 204
    assert not resp.text
    sql = "select is_deleted from quiz_tab where id = %s" % results[0]
    results = execute_sql(sql, fetchOne=True)
    assert results[0] == 1


@pytest.mark.parametrize("email", ["automation1@quiz.com", "automation2@quiz.com"])
def test_delete_with_invalid_token_fail(email):
    sql = "select token from user_token_tab where email='%s'" % email
    token = execute_sql(sql, fetchOne=True)[0]
    headers = {"Authorization": "Bearer %s" % token + "falsified"}
    sql = "select id from quiz_tab where creator='%s' and is_deleted=0" % email
    results = execute_sql(sql, fetchOne=True)
    params = {
        "id": encoded_id(str(results[0])),
    }
    print(params)
    resp = requests.delete(url, params=params, headers=headers, verify=False)
    print(resp.url)
    print(resp.text)
    print(resp.status_code)
    assert resp.status_code != 204
    res_dict = json.loads(resp.text)
    assert res_dict["error_code"] != 0
    sql = "select is_deleted from quiz_tab where id = %s" % results[0]
    results = execute_sql(sql, fetchOne=True)
    assert results[0] == 0


@pytest.mark.parametrize("email", ["automation1@quiz.com", "automation2@quiz.com"])
def test_delete_others_created_quiz_fail(email):
    sql = "select token from user_token_tab where email='%s'" % email
    token = execute_sql(sql, fetchOne=True)[0]
    headers = {"Authorization": "Bearer %s" % token}
    sql = "select id from quiz_tab where creator!='%s' and is_deleted=0" % email
    results = execute_sql(sql, fetchOne=True)
    params = {
        "id": encoded_id(str(results[0])),
    }
    print(params)
    resp = requests.delete(url, params=params, headers=headers, verify=False)
    print(resp.url)
    print(resp.text)
    print(resp.status_code)
    assert resp.status_code != 204
    res_dict = json.loads(resp.text)
    assert res_dict["error_code"] != 0
    sql = "select is_deleted from quiz_tab where id = %s" % results[0]
    results = execute_sql(sql, fetchOne=True)
    assert results[0] == 0


@pytest.mark.parametrize("email", ["automation1@quiz.com", "automation2@quiz.com"])
def test_delete_with_invalid_param_fail(email):
    sql = "select token from user_token_tab where email='%s'" % email
    token = execute_sql(sql, fetchOne=True)[0]
    headers = {"Authorization": "Bearer %s" % token}
    sql = "select id from quiz_tab where creator='%s' and is_deleted=0" % email
    results = execute_sql(sql, fetchOne=True)
    for id in ["", 0, results[0], None]:
        params = {
            "id": id,
        }
        print(params)
        resp = requests.delete(url, params=params, headers=headers, verify=False)
        print(resp.url)
        print(resp.text)
        print(resp.status_code)
        assert resp.status_code != 204
        res_dict = json.loads(resp.text)
        assert res_dict["error_code"] != 0


@pytest.mark.parametrize("email", ["automation1@quiz.com", "automation2@quiz.com"])
def test_delete_with_no_param_fail(email):
    sql = "select token from user_token_tab where email='%s'" % email
    token = execute_sql(sql, fetchOne=True)[0]
    headers = {"Authorization": "Bearer %s" % token}
    resp = requests.delete(url, headers=headers, verify=False)
    print(resp.url)
    print(resp.text)
    print(resp.status_code)
    assert resp.status_code != 204
    res_dict = json.loads(resp.text)
    assert res_dict["error_code"] != 0





