# -*- coding:utf-8 -*-

import json
import requests
import pytest

from tests.conf import PREFIX, PASSWORD
from tests.utis import execute_sql, b64_decode

url = PREFIX + "register"


@pytest.mark.run(order=2)
@pytest.mark.parametrize("email", ["automation1@quiz.com", "automation2@quiz.com", "automation3@quiz.com"])
def test_register_success(email):
    sql = "delete from user_tab where email='%s'" % email
    execute_sql(sql, commit=True)
    data = {
        "email": email,
        "password": PASSWORD
    }
    print(data)
    resp = requests.post(url, json=data, verify=False)
    print(resp.url)
    print(resp.text)
    print(resp.status_code)
    assert resp.status_code == 201
    res_dict = json.loads(resp.text)
    assert res_dict.get("error_code") == 0
    sql = "select * from user_tab where email='%s'" % email
    results = execute_sql(sql, fetchOne=True)
    assert results
    assert b64_decode(results[2][5:-5]) == PASSWORD


@pytest.mark.parametrize("email", ["automation 4@quiz.com", "automation5#quiz.com", " ", None, "automation4@qu iz.com"])
@pytest.mark.parametrize("pswd", ["", " ", None])
def test_register_with_invaid_params_fail(email, pswd):
    data = {
        "email": email,
        "password": pswd
    }
    print(data)
    resp = requests.post(url, json=data, verify=False)
    print(resp.url)
    print(resp.text)
    print(resp.status_code)
    assert resp.status_code != 201
    res_dict = json.loads(resp.text)
    assert res_dict.get("error_code") != 0
    sql = "select * from user_tab where email='%s'" % email
    results = execute_sql(sql, fetchOne=True)
    assert not results


@pytest.mark.parametrize("email", ["automation1@quiz.com", "automation2@quiz.com", "automation3@quiz.com"])
def test_re_register_fail(email):
    data = {
        "email": email,
        "password": PASSWORD+"_new"
    }
    print(data)
    resp = requests.post(url, json=data, verify=False)
    print(resp.url)
    print(resp.text)
    print(resp.status_code)
    assert resp.status_code != 201
    res_dict = json.loads(resp.text)
    assert res_dict.get("error_code") != 0
    sql = "select * from user_tab where email='%s'" % email
    results = execute_sql(sql, fetchOne=True)
    assert results
    assert b64_decode(results[2][5:-5]) != PASSWORD+"_new"


@pytest.mark.parametrize("data", [{"email": "automation4@quiz.com"}, {"password": PASSWORD}, {}])
def test_register_with_field_skipped_fail(data):
    print(data)
    resp = requests.post(url, json=data, verify=False)
    print(resp.url)
    print(resp.text)
    print(resp.status_code)
    assert resp.status_code != 201
    res_dict = json.loads(resp.text)
    assert res_dict.get("error_code") != 0



