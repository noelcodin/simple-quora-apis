# -*- coding:utf-8 -*-

import json
import requests
import pytest
import time

from tests.conf import PREFIX, PASSWORD
from tests.utis import execute_sql

url = PREFIX + "login"

@pytest.mark.run(order=3)
@pytest.mark.parametrize("email", ["automation1@quiz.com", "automation2@quiz.com", "automation3@quiz.com"])
def test_login_success(email):
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
    token = res_dict["data"]["token"]
    sql = "select * from user_token_tab where token='%s'" % token
    results = execute_sql(sql, fetchOne=True)
    assert results and results[1] == email and results[3] > int(time.time())+60*60*24*29


@pytest.mark.parametrize("email", ["automation1@quiz.com", "automation 4@quiz.com", "automation5#quiz.com",
                                   "automation2@quiz.com", " ", None, "automation4@qu iz.com"])
@pytest.mark.parametrize("pswd", [PASSWORD+"_new", PASSWORD+"_old", "", " ", None])
def test_login_with_invaid_params_fail(email, pswd):
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


@pytest.mark.parametrize("data", [{"email": "automation4@quiz.com"}, {"password": PASSWORD}, {}])
def test_login_with_field_skipped_fail(data):
    resp = requests.post(url, json=data, verify=False)
    print(resp.url)
    print(resp.text)
    print(resp.status_code)
    assert resp.status_code != 201
    res_dict = json.loads(resp.text)
    assert res_dict.get("error_code") != 0



