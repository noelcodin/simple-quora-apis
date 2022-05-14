# -*- coding:utf-8 -*-

import json
import requests
import pytest

from tests.conf import PREFIX
from tests.utis import execute_sql, decoded_id

url = PREFIX + "solution/my_quizzes"


@pytest.mark.parametrize("email", ["automation1@quiz.com", "automation2@quiz.com", "automation3@quiz.com"])
def test_get_quiz_to_solution_list_success(email):
    sql = "select token from user_token_tab where email='%s'" % email
    token = execute_sql(sql, fetchOne=True)[0]
    headers = {"Authorization": "Bearer %s" % token}
    response = requests.get(url, headers=headers, verify=False)
    print(response.url)
    print(response.text)
    print(response.status_code)
    assert response.status_code == 200
    resp = json.loads(response.text)
    assert resp["error_code"] == 0
    sql = "select id from quiz_tab where creator='%s' and is_deleted=0 and published=1" % email
    quiz_ids = execute_sql(sql)
    if not quiz_ids:
        assert resp["data"] == []
    else:
        quiz_ids = [quiz_id[0] for quiz_id in quiz_ids]
        resp_quiz_ids = [decoded_id(ele["quiz_id"]) for ele in resp["data"]]
        assert sorted(quiz_ids) == sorted(resp_quiz_ids)
        for quiz in resp["data"]:
            sql = "select * from quiz_tab where id=%s" % decoded_id(quiz["quiz_id"])
            quiz_info = execute_sql(sql, fetchOne=True)
            assert quiz["title"] == quiz_info[2]
            assert quiz["creator"] == quiz_info[1]
            sql = "select * from solution_tab where quiz_id=%s" % decoded_id(quiz["quiz_id"])
            db_solutions = execute_sql(sql)
            if not db_solutions:
                assert quiz["submitted_solutions"] == []
            else:
                db_solution_ids = [ele[0] for ele in db_solutions]
                resp_solution_ids = [ele["solution_id"] for ele in quiz["submitted_solutions"]]
                assert sorted(db_solution_ids) == sorted(resp_solution_ids)
                for sol in quiz["submitted_solutions"]:
                    sql = "select * from solution_tab where id=%s" % sol["solution_id"]
                    solution_info = execute_sql(sql, fetchOne=True)
                    sql = "select * from solution_answer_tab where solution_id=%s" % sol["solution_id"]
                    solution_answers = execute_sql(sql)
                    total_score = 0
                    for _ in solution_answers:
                        total_score += 1
                    assert sol["score"] == '{:.0%}'.format(solution_info[-1]/total_score)
                    assert sol["submitted_user"] == solution_info[2]


@pytest.mark.parametrize("email", ["automation1@quiz.com", "automation2@quiz.com", "automation3@quiz.com"])
def test_get_quiz_to_solution_list_with_invalid_token_fails(email):
    sql = "select token from user_token_tab where email='%s'" % email
    token = execute_sql(sql, fetchOne=True)[0]
    headers = {"Authorization": "Bearer %s" % token+"_falsified"}
    response = requests.get(url, headers=headers, verify=False)
    print(response.url)
    print(response.text)
    print(response.status_code)
    assert response.status_code != 200
    resp = json.loads(response.text)
    assert resp["error_code"] != 0
    assert not resp["data"]