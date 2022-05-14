# -*- coding:utf-8 -*-

import pytest

from tests.utis import execute_sql


@pytest.mark.run(order=1)
def test_setup():
    for email in ["automation1@quiz.com", "automation2@quiz.com", "automation3@quiz.com"]:
        sql = "delete from user_tab where email='%s'" % email
        execute_sql(sql, commit=True)
        sql = "delete from user_token_tab where email='%s'" % email
        execute_sql(sql, commit=True)
        sql = "select id from quiz_tab where creator='%s'" % email
        quiz_ids = execute_sql(sql)
        quiz_ids = [quiz_id[0] for quiz_id in quiz_ids]
        for quiz_id in quiz_ids:
            sql = "delete from quiz_question_tab where quiz_id=%s" % quiz_id
            execute_sql(sql, commit=True)
        sql = "delete from quiz_tab where creator='%s'" % email
        execute_sql(sql, commit=True)
        sql = "select id from solution_tab where user='%s'" % email
        solution_ids = execute_sql(sql)
        solution_ids = [solution_id[0] for solution_id in solution_ids]
        for solution_id in solution_ids:
            sql = "delete from solution_answer_tab where solution_id=%s" % solution_id
            execute_sql(sql, commit=True)
        sql = "delete from solution_tab where user='%s'" % email
        execute_sql(sql, commit=True)


def teardown():
    for email in ["automation1@quiz.com", "automation2@quiz.com", "automation3@quiz.com"]:
        sql = "delete from user_tab where email='%s'" % email
        execute_sql(sql, commit=True)
        sql = "delete from user_token_tab where email='%s'" % email
        execute_sql(sql, commit=True)
        sql = "select id from quiz_tab where creator='%s'" % email
        quiz_ids = execute_sql(sql)
        quiz_ids = [quiz_id[0] for quiz_id in quiz_ids]
        for quiz_id in quiz_ids:
            sql = "delete from quiz_question_tab where quiz_id=%s" % quiz_id
            execute_sql(sql, commit=True)
        sql = "delete from quiz_tab where creator='%s'" % email
        execute_sql(sql, commit=True)
        sql = "select id from solution_tab where user='%s'" % email
        solution_ids = execute_sql(sql)
        solution_ids = [solution_id[0] for solution_id in solution_ids]
        for solution_id in solution_ids:
            sql = "delete from solution_answer_tab where solution_id=%s" % solution_id
            execute_sql(sql, commit=True)
        sql = "delete from solution_tab where user='%s'" % email
        execute_sql(sql, commit=True)





