# -*- coding:utf-8 -*-

from common.config import db
from common import utils
from common.config import app
from sqlalchemy import and_, or_

# user_tab
class UserTab(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(255), nullable=False)
    password = db.Column(db.String(255), nullable=False)

    # insert a new row
    def add_new_row(email, password):
        try:
            existing_user = UserTab.query.filter(UserTab.email == email).first()
            # block re-register
            if existing_user:
                return utils.InternalError.EmailRegistered.value, None
            new_user = UserTab(
                email=email,
                password=password
            )
            db.session.add(new_user)
            db.session.commit()
            return None, None
        except Exception as e:
            app.logger.exception(str(e))
            db.session.rollback()
            return utils.InternalError.DBError.value, None

# user_token_tab
class UserTokenTab(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(255), nullable=False)
    token = db.Column(db.String(255), nullable=False)
    expiration = db.Column(db.BigInteger, nullable=False)

    # insert a new row
    def add_new_row(email, token, expiration):
        try:
            new_token = UserTokenTab(
                email=email,
                token=token,
                expiration=expiration
            )
            db.session.add(new_token)
            db.session.commit()
            return None, None
        except Exception as e:
            app.logger.exception(str(e))
            db.session.rollback()
            return utils.InternalError.DBError.value, None


# quiz_tab
class QuizTab(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    creator = db.Column(db.String(255), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    is_deleted = db.Column(db.Integer, default=0)
    published = db.Column(db.Integer, default=0)

    # insert a new row, return its id
    def add_new_row(creator, title):
        try:
            new_quiz = QuizTab(
                creator=creator,
                title=title
            )
            db.session.add(new_quiz)
            db.session.flush()
            db.session.commit()
            return None, new_quiz.id
        except Exception as e:
            app.logger.exception(str(e))
            db.session.rollback()
            return utils.InternalError.DBError.value, None

    # filter quizzes created by a user
    def get_rows_filter_by_creator(creator):
        try:
            quizzes = QuizTab.query.filter(and_(QuizTab.creator == creator,
                                                or_(QuizTab.is_deleted != 1, QuizTab.is_deleted.is_(None))))
            return None, quizzes
        except Exception as e:
            app.logger.exception(str(e))
            return utils.InternalError.DBError.value, None

    # filter quizzes not created by a user
    def get_rows_not_as_creator(creator):
        try:
            quizzes = QuizTab.query.filter(and_(QuizTab.creator != creator,
                                                or_(QuizTab.is_deleted != 1, QuizTab.is_deleted.is_(None)),
                                                QuizTab.published == 1))
            return None, quizzes
        except Exception as e:
            app.logger.exception(str(e))
            return utils.InternalError.DBError.value, None

    # hard delete a row by id
    def delete_row_by_id(id):
        try:
            QuizTab.query.filter(QuizTab.id == id).delete()
            QuizQuestionTab.query.filter(QuizQuestionTab.quiz_id == id).delete()
            db.session.commit()
            return None, None
        except Exception as e:
            app.logger.exception(str(e))
            db.session.rollback()
            return utils.InternalError.DBError.value, None

    # soft delete a row by id
    def soft_delete_row_by_id(id):
        try:
            QuizTab.query.filter(QuizTab.id == id).update({"is_deleted": 1})
            db.session.commit()
            return None, None
        except Exception as e:
            app.logger.exception(str(e))
            db.session.rollback()
            return utils.InternalError.DBError.value, None

    # get a row by id
    def get_row_by_id(id):
        try:
            quiz = QuizTab.query.filter(QuizTab.id == id).first()
            if not quiz:
                return utils.InternalError.DataNotFound.value, None
            return None, quiz
        except Exception as e:
            app.logger.exception(str(e))
            return utils.InternalError.DBError.value, None

    # get a row by id
    def update_row(id, data):
        try:
            QuizTab.query.filter(QuizTab.id == id).update(data)
            db.session.commit()
            return None, None
        except Exception as e:
            app.logger.exception(str(e))
            db.session.rollback()
            return utils.InternalError.DBError.value, None

    # filter published_quizzes created by a user
    def get_published_rows_filter_by_creator(creator):
        try:
            quizzes = QuizTab.query.filter(and_(QuizTab.creator == creator,
                                                or_(QuizTab.is_deleted != 1, QuizTab.is_deleted.is_(None)),
                                                QuizTab.published == 1))
            return None, quizzes
        except Exception as e:
            app.logger.exception(str(e))
            return utils.InternalError.DBError.value, None


# quiz_question_tab
class QuizQuestionTab(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    quiz_id = db.Column(db.Integer, nullable=False)
    question = db.Column(db.String(500), nullable=False)
    options = db.Column(db.String(500), nullable=False)
    answers = db.Column(db.String(500), nullable=False)
    single_answer = db.Column(db.Integer, nullable=False)

    # insert multiple new rows
    def add_new_rows(quiz_id, questions):
        try:
            quiz_questions = []
            for question in questions:
                quiz_questions.append(QuizQuestionTab(
                    quiz_id=quiz_id,
                    question=question.get("question"),
                    options=str(question.get("options")),
                    answers=str(question.get("answers")),
                    single_answer=question.get("single_answer")
                ))
            db.session.add_all(quiz_questions)
            db.session.commit()
            return None, None
        except Exception as e:
            app.logger.exception(str(e))
            db.session.rollback()
            return utils.InternalError.DBError.value, None

    # filter rows by quiz id and delete them
    def delete_rows_by_quiz_id(quiz_id):
        try:
            QuizQuestionTab.query.filter(QuizQuestionTab.quiz_id == quiz_id).delete()
            db.session.commit()
            return None, None
        except Exception as e:
            app.logger.exception(str(e))
            db.session.rollback()
            return utils.InternalError.DBError.value, None

    # filter rows by quiz id
    def filter_rows_by_quiz_id(quiz_id):
        try:
            quizzes = QuizQuestionTab.query.filter(QuizQuestionTab.quiz_id == quiz_id)
            return None, quizzes
        except Exception as e:
            app.logger.exception(str(e))
            return utils.InternalError.DBError.value, None

    # get a row by id
    def get_row_by_id(id):
        try:
            quiz_question = QuizQuestionTab.query.filter(QuizQuestionTab.id == id).first()
            if not quiz_question:
                return utils.InternalError.DataNotFound.value, None
            return None, quiz_question
        except Exception as e:
            app.logger.exception(str(e))
            return utils.InternalError.DBError.value, None


# solution_tab
class SolutionTab(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    quiz_id = db.Column(db.Integer, nullable=False)
    user = db.Column(db.String(255), nullable=False)
    score = db.Column(db.Float(precision=2), nullable=False)

    # insert a new row, return its id
    def add_new_row(user, quiz_id, score):
        try:
            new_solution = SolutionTab(
                user=user,
                quiz_id=quiz_id,
                score=score
            )
            db.session.add(new_solution)
            db.session.flush()
            db.session.commit()
            return None, new_solution.id
        except Exception as e:
            app.logger.exception(str(e))
            db.session.rollback()
            return utils.InternalError.DBError.value, None

    # filter solutions submitted by a user
    def get_rows_filter_by_user(user):
        try:
            solutions = SolutionTab.query.filter(SolutionTab.user == user)
            return None, solutions
        except Exception as e:
            app.logger.exception(str(e))
            return utils.InternalError.DBError.value, None

    # get a row by id
    def get_row_by_id(id):
        try:
            solution = SolutionTab.query.filter(SolutionTab.id == id).first()
            if not solution:
                return utils.InternalError.DataNotFound.value, None
            return None, solution
        except Exception as e:
            app.logger.exception(str(e))
            return utils.InternalError.DBError.value, None

    # filter solutions submitted by submit user and quiz id
    def get_rows_filter_by_user_and_quiz_id(user, quiz_id):
        try:
            solutions = SolutionTab.query.filter(and_(SolutionTab.user == user, SolutionTab.quiz_id == quiz_id)).first()
            return None, solutions
        except Exception as e:
            app.logger.exception(str(e))
            return utils.InternalError.DBError.value, None

    # delete a row by id
    def delete_row_by_id(id):
        try:
            QuizTab.query.filter(SolutionTab.id == id).delete()
            QuizQuestionTab.query.filter(SolutionAnswerTab.quiz_id == id).delete()
            db.session.commit()
            return None, None
        except Exception as e:
            app.logger.exception(str(e))
            db.session.rollback()
            return utils.InternalError.DBError.value, None

    # filter solutions submitted by quiz id
    def get_rows_filter_by_quiz_id(id):
        try:
            solutions = SolutionTab.query.filter(SolutionTab.quiz_id == id)
            return None, solutions
        except Exception as e:
            app.logger.exception(str(e))
            return utils.InternalError.DBError.value, None


#solution_answer_tab
class SolutionAnswerTab(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    solution_id = db.Column(db.Integer, nullable=False)
    question_id = db.Column(db.Integer, nullable=False)
    answers = db.Column(db.String(500), nullable=False)
    score = db.Column(db.Float(precision=2), nullable=False)

    # insert multiple new rows
    def add_new_rows(solution_id, answers):
        try:
            solution_answers = []
            for answer in answers:
                solution_answers.append(SolutionAnswerTab(
                    solution_id=solution_id,
                    question_id=answer.get("question_id"),
                    answers=answer.get("answers"),
                    score=answer.get("score")
                ))
            db.session.add_all(solution_answers)
            db.session.commit()
            return None, None
        except Exception as e:
            app.logger.exception(str(e))
            db.session.rollback()
            return utils.InternalError.DBError.value, None

    # filter rows by solution id
    def filter_rows_by_solution_id(solution_id):
        try:
            answers = SolutionAnswerTab.query.filter(SolutionAnswerTab.solution_id == solution_id)
            return None, answers
        except Exception as e:
            app.logger.exception(str(e))
            return utils.InternalError.DBError.value, None


db.create_all()
