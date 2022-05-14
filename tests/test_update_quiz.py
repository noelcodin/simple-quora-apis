# -*- coding:utf-8 -*-

import json
import requests
import pytest
import copy
import random

from tests.conf import PREFIX
from tests.utis import execute_sql, convert_string_to_list, encoded_id

url = PREFIX + "quiz/update"


@pytest.mark.run(order=5)
@pytest.mark.parametrize("email", ["automation1@quiz.com", "automation2@quiz.com"])
def test_update_success(email):
    sql = "select token from user_token_tab where email='%s'" % email
    token = execute_sql(sql, fetchOne=True)[0]
    headers = {"Authorization": "Bearer %s" % token}
    sql = "select id from quiz_tab where creator='%s' and is_deleted=0 and published=0" % email
    quiz_ids = execute_sql(sql)
    quiz_ids = [quiz_id[0] for quiz_id in quiz_ids]
    quiz_id = quiz_ids[random.randint(0, len(quiz_ids)-1)]
    sql = "select * from quiz_tab where id=%s" % quiz_id
    quiz_info = execute_sql(sql, fetchOne=True)
    sql = "select * from quiz_question_tab where quiz_id=%s" % quiz_id
    quiz_questions = execute_sql(sql)
    questions = []
    for question in quiz_questions:
        temp = {
            "question": question[2]+"updated",
            "options": convert_string_to_list(question[3]),
            "answers": convert_string_to_list(question[4]),
            "single_answer": question[-1]
        }
        if type(temp["options"][0]) == int:
            new_option = random.randint(100, 2000)
        else:
            new_option = "extra_option_%s" % random.randint(1, 10000)
        if len(temp["options"]) < 5 :
            temp["options"].append(new_option)
            if not question[-1]:
                temp["answers"].append(new_option)
        questions.append(temp)
    data = {
        "id": encoded_id(quiz_id),
        "title": quiz_info[2]+"_updated",
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
    sql = "select * from quiz_tab where id=%s" % quiz_id
    results = execute_sql(sql, fetchOne=True)
    assert results[1] == email and results[2] == quiz_info[2]+"_updated"
    sql = "select * from quiz_question_tab where quiz_id=%s" % quiz_id
    results = execute_sql(sql)
    for idx, result in enumerate(results):
        assert result[2] == questions[idx]["question"]
        print(convert_string_to_list(result[3]))
        print(list(set(questions[idx]["options"])))
        assert sorted(convert_string_to_list(result[3])) == sorted(list(set(questions[idx]["options"])))
        assert sorted(convert_string_to_list(result[4])) == sorted(list(set(questions[idx]["answers"])))
        assert result[5] == questions[idx]["single_answer"]


@pytest.mark.parametrize("email", ["automation1@quiz.com", "automation2@quiz.com"])
def test_update_with_invalid_token_fail(email):
    sql = "select token from user_token_tab where email='%s'" % email
    token = execute_sql(sql, fetchOne=True)[0]
    headers = {"Authorization": "Bearer %s" % token+"falsified"}
    sql = "select id from quiz_tab where creator='%s' and is_deleted=0 and published=0" % email
    quiz_ids = execute_sql(sql)
    quiz_ids = [quiz_id[0] for quiz_id in quiz_ids]
    quiz_id = quiz_ids[random.randint(0, len(quiz_ids) - 1)]
    sql = "select * from quiz_tab where id=%s" % quiz_id
    quiz_info = execute_sql(sql, fetchOne=True)
    sql = "select * from quiz_question_tab where quiz_id=%s" % quiz_id
    quiz_questions = execute_sql(sql)
    questions = []
    for question in quiz_questions:
        questions.append({
            "question": question[2] + "updated",
            "options": convert_string_to_list(question[3]),
            "answers": convert_string_to_list(question[4]),
            "single_answer": question[-1]
        })
    data = {
        "id": encoded_id(quiz_id),
        "title": quiz_info[2] + "_updated",
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
    assert not res_dict["data"]


@pytest.mark.parametrize("email", ["automation1@quiz.com", "automation2@quiz.com"])
def test_update_with_over_10_questions_fail(email):
    sql = "select token from user_token_tab where email='%s'" % email
    token = execute_sql(sql, fetchOne=True)[0]
    headers = {"Authorization": "Bearer %s" % token}
    sql = "select id from quiz_tab where creator='%s' and is_deleted=0 and published=0" % email
    quiz_ids = execute_sql(sql)
    quiz_ids = [quiz_id[0] for quiz_id in quiz_ids]
    for quiz_id in quiz_ids:
        sql = "select * from quiz_tab where id=%s" % quiz_id
        quiz_info = execute_sql(sql, fetchOne=True)
        sql = "select * from quiz_question_tab where quiz_id=%s" % quiz_id
        quiz_questions = execute_sql(sql)
        if quiz_questions:
            questions = []
            for question in quiz_questions:
                questions.append({
                    "question": question[2] + "updated",
                    "options": convert_string_to_list(question[3]),
                    "answers": convert_string_to_list(question[4]),
                    "single_answer": question[-1]
                })
            while len(questions) <= 10:
                questions.extend(questions)
            data = {
                "id": encoded_id(quiz_id),
                "title": quiz_info[2] + "_updated",
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
            assert not res_dict["data"]
            break


@pytest.mark.parametrize("email", ["automation1@quiz.com", "automation2@quiz.com"])
def test_update_with_over_5_options_fail(email):
    sql = "select token from user_token_tab where email='%s'" % email
    token = execute_sql(sql, fetchOne=True)[0]
    headers = {"Authorization": "Bearer %s" % token}
    sql = "select id from quiz_tab where creator='%s' and is_deleted=0 and published=0" % email
    quiz_ids = execute_sql(sql)
    quiz_ids = [quiz_id[0] for quiz_id in quiz_ids]
    for quiz_id in quiz_ids:
        sql = "select * from quiz_tab where id=%s" % quiz_id
        quiz_info = execute_sql(sql, fetchOne=True)
        sql = "select * from quiz_question_tab where quiz_id=%s" % quiz_id
        quiz_questions = execute_sql(sql)
        if quiz_questions:
            questions = []
            for question in quiz_questions:
                questions.append({
                    "question": question[2] + "updated",
                    "options": convert_string_to_list(question[3]),
                    "answers": convert_string_to_list(question[4]),
                    "single_answer": question[-1]
                })
            idx = random.randint(0, len(questions)-1)
            while len(questions[idx]["options"]) <= 5:
                questions[idx]["options"].extend(questions[idx]["options"])
            data = {
                "id": encoded_id(quiz_id),
                "title": quiz_info[2] + "_updated",
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
            assert not res_dict["data"]
            break


@pytest.mark.parametrize("email", ["automation1@quiz.com", "automation2@quiz.com"])
def test_update_with_answer_not_in_options_fail(email):
    sql = "select token from user_token_tab where email='%s'" % email
    token = execute_sql(sql, fetchOne=True)[0]
    headers = {"Authorization": "Bearer %s" % token}
    sql = "select id from quiz_tab where creator='%s' and is_deleted=0 and published=0" % email
    quiz_ids = execute_sql(sql)
    quiz_ids = [quiz_id[0] for quiz_id in quiz_ids]
    for quiz_id in quiz_ids:
        sql = "select * from quiz_tab where id=%s" % quiz_id
        quiz_info = execute_sql(sql, fetchOne=True)
        sql = "select * from quiz_question_tab where quiz_id=%s" % quiz_id
        quiz_questions = execute_sql(sql)
        if quiz_questions:
            questions = []
            for question in quiz_questions:
                questions.append({
                    "question": question[2] + "updated",
                    "options": convert_string_to_list(question[3]),
                    "answers": convert_string_to_list(question[4]),
                    "single_answer": question[-1]
                })
            idx = random.randint(0, len(questions)-1)
            questions[idx]["answers"].append("extra_answer_%s" % random.randint(0, 10000))
            data = {
                "id": encoded_id(quiz_id),
                "title": quiz_info[2] + "_updated",
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
            assert not res_dict["data"]
            break


@pytest.mark.parametrize("email", ["automation1@quiz.com", "automation2@quiz.com"])
def test_update_with_mutiple_answer_for_single_answer_question_fail(email):
    sql = "select token from user_token_tab where email='%s'" % email
    token = execute_sql(sql, fetchOne=True)[0]
    headers = {"Authorization": "Bearer %s" % token}
    sql = "select id from quiz_tab where creator='%s' and is_deleted=0 and published=0" % email
    quiz_ids = execute_sql(sql)
    quiz_ids = [quiz_id[0] for quiz_id in quiz_ids]
    for quiz_id in quiz_ids:
        sql = "select * from quiz_tab where id=%s" % quiz_id
        quiz_info = execute_sql(sql, fetchOne=True)
        sql = "select * from quiz_question_tab where quiz_id=%s" % quiz_id
        quiz_questions = execute_sql(sql)
        if quiz_questions:
            questions = []
            for question in quiz_questions:
                questions.append({
                    "question": question[2] + "updated",
                    "options": convert_string_to_list(question[3]),
                    "answers": convert_string_to_list(question[4]),
                    "single_answer": 1 - question[-1]
                })
            data = {
                "id": encoded_id(quiz_id),
                "title": quiz_info[2] + "_updated",
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
            assert not res_dict["data"]
            break


@pytest.mark.parametrize("email", ["automation1@quiz.com", "automation2@quiz.com"])
@pytest.mark.parametrize("value", ["", " ", [], None])
def test_update_with_invalid_questions_fields_fail(email, value):
    sql = "select token from user_token_tab where email='%s'" % email
    token = execute_sql(sql, fetchOne=True)[0]
    headers = {"Authorization": "Bearer %s" % token}
    sql = "select id from quiz_tab where creator='%s' and is_deleted=0 and published=0" % email
    quiz_ids = execute_sql(sql)
    quiz_ids = [quiz_id[0] for quiz_id in quiz_ids]
    for quiz_id in quiz_ids:
        sql = "select * from quiz_tab where id=%s" % quiz_id
        quiz_info = execute_sql(sql, fetchOne=True)
        sql = "select * from quiz_question_tab where quiz_id=%s" % quiz_id
        quiz_questions = execute_sql(sql)
        if quiz_questions:
            questions = []
            for question in quiz_questions:
                questions.append({
                    "question": question[2] + "updated",
                    "options": convert_string_to_list(question[3]),
                    "answers": convert_string_to_list(question[4]),
                    "single_answer": question[-1]
                })

            for key in questions[0].keys():
                questions_temp = copy.deepcopy(questions)
                idx = random.randint(0, len(questions_temp) - 1)
                questions_temp[idx][key] = value
                data = {
                    "id": encoded_id(quiz_id),
                    "title": quiz_info[2] + "_updated",
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
            break

@pytest.mark.parametrize("email", ["automation1@quiz.com", "automation2@quiz.com"])
@pytest.mark.parametrize("value", ["", " ", [], None])
def test_update_with_invalid_outer_fields_fail(email, value):
    sql = "select token from user_token_tab where email='%s'" % email
    token = execute_sql(sql, fetchOne=True)[0]
    headers = {"Authorization": "Bearer %s" % token}
    sql = "select id from quiz_tab where creator='%s' and is_deleted=0 and published=0" % email
    quiz_ids = execute_sql(sql)
    quiz_ids = [quiz_id[0] for quiz_id in quiz_ids]
    for quiz_id in quiz_ids:
        sql = "select * from quiz_tab where id=%s" % quiz_id
        quiz_info = execute_sql(sql, fetchOne=True)
        sql = "select * from quiz_question_tab where quiz_id=%s" % quiz_id
        quiz_questions = execute_sql(sql)
        if quiz_questions:
            questions = []
            for question in quiz_questions:
                questions.append({
                    "question": question[2] + "updated",
                    "options": convert_string_to_list(question[3]),
                    "answers": convert_string_to_list(question[4]),
                    "single_answer": question[-1]
                })
            data = {
                "id": value,
                "title": quiz_info[2] + "_updated",
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

            data = {
                "id": encoded_id(quiz_id),
                "title": value,
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

            data = {
                "id": encoded_id(quiz_id),
                "title": quiz_info[2] + "_updated",
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
            break


@pytest.mark.parametrize("email", ["automation1@quiz.com", "automation2@quiz.com"])
def test_udpate_with_outer_field_skipped_fail(email):
    sql = "select token from user_token_tab where email='%s'" % email
    token = execute_sql(sql, fetchOne=True)[0]
    headers = {"Authorization": "Bearer %s" % token}
    sql = "select id from quiz_tab where creator='%s' and is_deleted=0 and published=0" % email
    quiz_ids = execute_sql(sql)
    quiz_ids = [quiz_id[0] for quiz_id in quiz_ids]
    for quiz_id in quiz_ids:
        sql = "select * from quiz_tab where id=%s" % quiz_id
        quiz_info = execute_sql(sql, fetchOne=True)
        sql = "select * from quiz_question_tab where quiz_id=%s" % quiz_id
        quiz_questions = execute_sql(sql)
        if quiz_questions:
            new_option = "updated_new_%s" % random.randint(1, 10000)
            questions = []
            for question in quiz_questions:
                temp = {
                    "question": question[2] + "updated",
                    "options": convert_string_to_list(question[3]),
                    "answers": convert_string_to_list(question[4]),
                    "single_answer": question[-1]
                }
                if len(temp["options"]) < 5:
                    temp["options"].append(new_option)
                    temp["answers"].append(new_option)
                questions.append(temp)
            data = {
                "id": encoded_id(quiz_id),
                "title": quiz_info[2] + "_updated",
                "questions": questions
            }
            for key in data.keys():
                data_temp = copy.deepcopy(data)
                data_temp.pop(key)
                resp = requests.post(url, json=data_temp, headers=headers, verify=False)
                print(resp.url)
                print(resp.text)
                print(resp.status_code)
                assert resp.status_code != 201
                res_dict = json.loads(resp.text)
                assert res_dict.get("error_code") != 0
            break


@pytest.mark.parametrize("email", ["automation1@quiz.com", "automation2@quiz.com"])
def test_update_with_question_field_skipped_fail(email):
    sql = "select token from user_token_tab where email='%s'" % email
    token = execute_sql(sql, fetchOne=True)[0]
    headers = {"Authorization": "Bearer %s" % token}
    sql = "select id from quiz_tab where creator='%s' and is_deleted=0 and published=0" % email
    quiz_ids = execute_sql(sql)
    quiz_ids = [quiz_id[0] for quiz_id in quiz_ids]
    for quiz_id in quiz_ids:
        sql = "select * from quiz_tab where id=%s" % quiz_id
        quiz_info = execute_sql(sql, fetchOne=True)
        sql = "select * from quiz_question_tab where quiz_id=%s" % quiz_id
        quiz_questions = execute_sql(sql)
        if quiz_questions:
            new_option = "updated_new_%s" % random.randint(1, 10000)
            questions = []
            for question in quiz_questions:
                temp = {
                    "question": question[2] + "updated",
                    "options": convert_string_to_list(question[3]),
                    "answers": convert_string_to_list(question[4]),
                    "single_answer": question[-1]
                }
                if len(temp["options"]) < 5:
                    temp["options"].append(new_option)
                    temp["answers"].append(new_option)
                questions.append(temp)
            for key in questions[0].keys():
                questions_temp = copy.deepcopy(questions)
                idx = random.randint(0, len(questions_temp)-1)
                questions_temp[idx].pop(key)
                data = {
                    "id": encoded_id(quiz_id),
                    "title": quiz_info[2] + "_updated",
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
            break

@pytest.mark.parametrize("email", ["automation1@quiz.com", "automation2@quiz.com"])
def test_update_others_created_quiz_fail(email):
    sql = "select token from user_token_tab where email='%s'" % email
    token = execute_sql(sql, fetchOne=True)[0]
    headers = {"Authorization": "Bearer %s" % token}
    sql = "select id from quiz_tab where creator!='%s' and is_deleted=0 and published=0" % email
    quiz_ids = execute_sql(sql)
    quiz_ids = [quiz_id[0] for quiz_id in quiz_ids]
    quiz_id = quiz_ids[random.randint(0, len(quiz_ids) - 1)]
    sql = "select * from quiz_tab where id=%s" % quiz_id
    quiz_info = execute_sql(sql, fetchOne=True)
    sql = "select * from quiz_question_tab where quiz_id=%s" % quiz_id
    quiz_questions = execute_sql(sql)
    questions = []
    for question in quiz_questions:
        questions.append({
            "question": question[2] + "updated",
            "options": convert_string_to_list(question[3]),
            "answers": convert_string_to_list(question[4]),
            "single_answer": question[-1]
        })
    data = {
        "id": encoded_id(quiz_id),
        "title": quiz_info[2] + "_updated",
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
    assert not res_dict["data"]


@pytest.mark.parametrize("email", ["automation1@quiz.com", "automation2@quiz.com"])
def test_update_own_published_quiz_fail(email):
    sql = "select token from user_token_tab where email='%s'" % email
    token = execute_sql(sql, fetchOne=True)[0]
    headers = {"Authorization": "Bearer %s" % token}
    sql = "select id from quiz_tab where creator='%s' and is_deleted=0 and published=1" % email
    quiz_ids = execute_sql(sql)
    quiz_ids = [quiz_id[0] for quiz_id in quiz_ids]
    quiz_id = quiz_ids[random.randint(0, len(quiz_ids) - 1)]
    sql = "select * from quiz_tab where id=%s" % quiz_id
    quiz_info = execute_sql(sql, fetchOne=True)
    sql = "select * from quiz_question_tab where quiz_id=%s" % quiz_id
    quiz_questions = execute_sql(sql)
    questions = []
    for question in quiz_questions:
        questions.append({
            "question": question[2] + "updated",
            "options": convert_string_to_list(question[3]),
            "answers": convert_string_to_list(question[4]),
            "single_answer": question[-1]
        })
    data = {
        "id": encoded_id(quiz_id),
        "title": quiz_info[2] + "_updated",
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
    assert not res_dict["data"]