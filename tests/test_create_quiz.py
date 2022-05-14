# -*- coding:utf-8 -*-

import json
import requests
import pytest
import copy
import random

from tests.conf import PREFIX, PASSWORD
from tests.utis import execute_sql, convert_string_to_list, decoded_id

url = PREFIX + "quiz"

questions = [{
    "question": "How much is 1 + 1?",
    "options": [1, 2, 3, 4],
    "answers":[2, 2, 2],
    "single_answer": 1
},
    {
    "question": "What are the seasons of a year?",
    "options": ["summer", "spring", "cold", "hot", "winter"],
    "answers":["summer", "summer", "summer", "spring", "winter"],
    "single_answer": 0
},
    {
    "question": "How much is 12 + 1?",
    "options": [1, 2, 13, 4],
    "answers": [13],
    "single_answer": 1
},
    {
    "question": "Which of the following countries are in Asia?",
    "options": ["China", "UK", "India", "USA"],
    "answers":["China", "India", "India"],
    "single_answer": 0
}
]


@pytest.mark.run(order=4)
@pytest.mark.parametrize("email", ["automation1@quiz.com", "automation2@quiz.com"])
def test_create_success(email):
    sql = "select token from user_token_tab where email='%s'" % email
    token = execute_sql(sql, fetchOne=True)[0]
    headers = {"Authorization": "Bearer %s" % token}
    for i in range(10):
        data = {
            "title": "quiz demo from %s" % email,
            "questions": questions
        }
        print(data)
        resp = requests.post(url, json=data, headers=headers, verify=False)
        print(resp.url)
        print(resp.text)
        print(resp.status_code)
        assert resp.status_code == 201
        res_dict = json.loads(resp.text)
        assert res_dict.get("error_code") == 0
        quiz_id = res_dict["data"]["added"]
        quiz_id = decoded_id(quiz_id)
        sql = "select * from quiz_tab where id=%s" % quiz_id
        results = execute_sql(sql, fetchOne=True)
        assert results[1] == email and results[2] == "quiz demo from %s" % email
        sql = "select * from quiz_question_tab where quiz_id=%s" % quiz_id
        results = execute_sql(sql)
        for idx, result in enumerate(results):
            assert result[2] == questions[idx]["question"] \
                   and sorted(convert_string_to_list(result[3])) == sorted(list(set(questions[idx]["options"]))) \
                   and sorted(convert_string_to_list(result[4])) == sorted(list(set(questions[idx]["answers"]))) \
                   and result[5] == questions[idx]["single_answer"]



@pytest.mark.parametrize("email", ["automation1@quiz.com", "automation2@quiz.com"])
def test_create_with_invalid_token_fail(email):
    sql = "select token from user_token_tab where email='%s'" % email
    token = execute_sql(sql, fetchOne=True)[0]
    headers = {"Authorization": "Bearer %s" % token+"falsified"}
    data = {
        "title": "quiz demo from %s" % email,
        "questions": questions
    }
    print(data)
    resp = requests.post(url, json=data, headers=headers, verify=False)
    print(resp.url)
    print(resp.text)
    print(resp.status_code)
    assert resp.status_code != 201
    res_dict = json.loads(resp.text)
    assert res_dict.get("error_code") != 0


@pytest.mark.parametrize("email", ["automation1@quiz.com", "automation2@quiz.com"])
def test_create_with_over_10_questions_fail(email):
    sql = "select token from user_token_tab where email='%s'" % email
    token = execute_sql(sql, fetchOne=True)[0]
    headers = {"Authorization": "Bearer %s" % token}
    questions_temp = copy.deepcopy(questions)
    while len(questions_temp) < 10:
        questions_temp.extend(questions)
    data = {
        "title": "quiz demo from %s" % email,
        "questions": questions_temp
    }
    print(data)
    resp = requests.post(url, json=data, headers=headers, verify=False)
    print(resp.url)
    print(resp.text)
    print(resp.status_code)
    assert resp.status_code != 201
    res_dict = json.loads(resp.text)
    assert res_dict.get("error_code") != 0


@pytest.mark.parametrize("email", ["automation1@quiz.com", "automation2@quiz.com"])
def test_create_with_over_5_options_fail(email):
    sql = "select token from user_token_tab where email='%s'" % email
    token = execute_sql(sql, fetchOne=True)[0]
    headers = {"Authorization": "Bearer %s" % token}
    questions_temp = copy.deepcopy(questions)
    idx = random.randint(0, len(questions_temp)-1)
    while len(questions_temp[idx]["options"]) <= 5:
        questions_temp[idx]["options"].append("extra_option_%s" % str(random.randint(0, 10000)))
    data = {
        "title": "quiz demo from %s" % email,
        "questions": questions_temp
    }
    print(data)
    resp = requests.post(url, json=data, headers=headers, verify=False)
    print(resp.url)
    print(resp.text)
    print(resp.status_code)
    assert resp.status_code != 201
    res_dict = json.loads(resp.text)
    assert res_dict.get("error_code") != 0


@pytest.mark.parametrize("email", ["automation1@quiz.com", "automation2@quiz.com"])
def test_create_with_answer_not_in_options_fail(email):
    sql = "select token from user_token_tab where email='%s'" % email
    token = execute_sql(sql, fetchOne=True)[0]
    headers = {"Authorization": "Bearer %s" % token}
    questions_temp = copy.deepcopy(questions)
    idx = random.randint(0, len(questions_temp)-1)
    questions_temp[idx]["answers"][random.randint(0, len(questions_temp[idx]["answers"])-1)] = \
        "extra_option_%s" % str(random.randint(0, 10000))
    data = {
        "title": "quiz demo from %s" % email,
        "questions": questions_temp
    }
    print(data)
    resp = requests.post(url, json=data, headers=headers, verify=False)
    print(resp.url)
    print(resp.text)
    print(resp.status_code)
    assert resp.status_code != 201
    res_dict = json.loads(resp.text)
    assert res_dict.get("error_code") != 0


@pytest.mark.parametrize("email", ["automation1@quiz.com", "automation2@quiz.com"])
def test_create_with_mutiple_answer_for_single_answer_question_fail(email):
    sql = "select token from user_token_tab where email='%s'" % email
    token = execute_sql(sql, fetchOne=True)[0]
    headers = {"Authorization": "Bearer %s" % token}
    questions_temp = copy.deepcopy(questions)
    for question in questions_temp:
        if question["single_answer"]:
            question["answers"].append("extra_option_%s" % str(random.randint(0, 10000)))
            break
    data = {
        "title": "quiz demo from %s" % email,
        "questions": questions_temp
    }
    print(data)
    resp = requests.post(url, json=data, headers=headers, verify=False)
    print(resp.url)
    print(resp.text)
    print(resp.status_code)
    assert resp.status_code != 201
    res_dict = json.loads(resp.text)
    assert res_dict.get("error_code") != 0


@pytest.mark.parametrize("email", ["automation1@quiz.com", "automation2@quiz.com"])
@pytest.mark.parametrize("value", ["", " ", [], None])
def test_create_with_invalid_questions_fields_fail(email, value):
    sql = "select token from user_token_tab where email='%s'" % email
    token = execute_sql(sql, fetchOne=True)[0]
    headers = {"Authorization": "Bearer %s" % token}
    for key in questions[0].keys():
        questions_temp = copy.deepcopy(questions)
        idx = random.randint(0, len(questions_temp) - 1)
        questions_temp[idx][key] = value
        data = {
            "title": "quiz demo from %s" % email,
            "questions": questions_temp
        }
        print(data)
        resp = requests.post(url, json=data, headers=headers, verify=False)
        print(resp.url)
        print(resp.text)
        print(resp.status_code)
        assert resp.status_code != 201
        res_dict = json.loads(resp.text)
        assert res_dict.get("error_code") != 0


@pytest.mark.parametrize("email", ["automation1@quiz.com", "automation2@quiz.com"])
@pytest.mark.parametrize("value", ["", " ", [], None])
def test_create_with_invalid_outer_fields_fail(email, value):
    sql = "select token from user_token_tab where email='%s'" % email
    token = execute_sql(sql, fetchOne=True)[0]
    headers = {"Authorization": "Bearer %s" % token}
    for key in questions[0].keys():
        questions_temp = copy.deepcopy(questions)
        idx = random.randint(0, len(questions_temp) - 1)
        questions_temp[idx][key] = value
        data = {
            "title": value,
            "questions": questions_temp
        }
        print(data)
        resp = requests.post(url, json=data, headers=headers, verify=False)
        print(resp.url)
        print(resp.text)
        print(resp.status_code)
        assert resp.status_code != 201
        res_dict = json.loads(resp.text)
        assert res_dict.get("error_code") != 0

        data = {
            "title": "quiz demo from %s" % email,
            "questions": value
        }
        print(data)
        resp = requests.post(url, json=data, headers=headers, verify=False)
        print(resp.url)
        print(resp.text)
        print(resp.status_code)
        assert resp.status_code != 201
        res_dict = json.loads(resp.text)
        assert res_dict.get("error_code") != 0


@pytest.mark.parametrize("email", ["automation1@quiz.com", "automation2@quiz.com"])
@pytest.mark.parametrize("data", [{"title": "automation4@quiz.com"}, {"questions": questions}, {}])
def test_register_with_outer_field_skipped_fail(email, data):
    sql = "select token from user_token_tab where email='%s'" % email
    token = execute_sql(sql, fetchOne=True)[0]
    headers = {"Authorization": "Bearer %s" % token}
    print(data)
    resp = requests.post(url, json=data, headers=headers, verify=False)
    print(resp.url)
    print(resp.text)
    print(resp.status_code)
    assert resp.status_code != 201
    res_dict = json.loads(resp.text)
    assert res_dict.get("error_code") != 0


@pytest.mark.parametrize("email", ["automation1@quiz.com", "automation2@quiz.com"])
@pytest.mark.parametrize("key", list(questions[0].keys()))
def test_register_with_question_field_skipped_fail(email, key):
    sql = "select token from user_token_tab where email='%s'" % email
    token = execute_sql(sql, fetchOne=True)[0]
    headers = {"Authorization": "Bearer %s" % token}
    questions_temp = copy.deepcopy(questions)
    idx = random.randint(0, len(questions_temp) - 1)
    questions_temp[idx].pop(key)
    data = {
        "title": "quiz demo from %s" % email,
        "questions": questions_temp
    }
    print(data)
    resp = requests.post(url, json=data, headers=headers, verify=False)
    print(resp.url)
    print(resp.text)
    print(resp.status_code)
    assert resp.status_code != 201
    res_dict = json.loads(resp.text)
    assert res_dict.get("error_code") != 0



