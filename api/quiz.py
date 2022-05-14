# -*- coding:utf-8 -*-

import sys
from flask_restful import Resource
from flask import request
from flask_docs import ApiDoc

from common.config import api_prefix, api, app
from common import utils
from controller import quiz_controller

ApiDoc(
    app,
    title="Quiz App",
    version="1.0.0",
    description="Quiz App REST APIs",
)

# Api /register
class UserResource(Resource):
    def post(self):
        """Register

           @@@
           ### args
           |  args | nullable | request type | type |  remarks |
           |-------|----------|--------------|------|----------|
           | email |  false   |    body      | str  | email    |
           | password  |  false   |    body      | str  | password |

           ### request
           ```json
           {"email": "automation1@quiz.com", "password": "xxx"}
           ```

           ### return
           ```json
           {"registered": "automation1@quiz.com"}
           ```
           @@@
           """
        try:
            # parse json format input
            email = request.json["email"]
            password = request.json["password"]
        except Exception as e:
            app.logger.exception(str(e))
            return utils.error_response(utils.InternalError.ParamError.value)
        app.logger.info("token: %s, endpoint: %s, json: %s, params: %s" %
                        (request.cookies, "%s/register" % api_prefix, request.json, request.args))
        # validate email format
        validate_email = utils.validate_email_format(str(email))
        if not validate_email:
            return utils.error_response(utils.InternalError.ParamError.value)
        # call register controller
        err, data = quiz_controller.register_controller(email, password)
        if err:
            app.logger.error("response: %s" % str(err))
            return utils.error_response(err)
        app.logger.info("response: %s" % str(data))
        return utils.common_json_response(data, method=sys._getframe().f_code.co_name)


api.add_resource(UserResource, "%s/register" % api_prefix)


# Api /login
class UserTokenResource(Resource):
    def post(self):
        """Sign in

                   @@@
                   ### args
                   |  args | nullable | request type | type |  remarks |
                   |-------|----------|--------------|------|----------|
                   | email |  false   |    body      | str  | email    |
                   | password  |  false   |    body      | str  | password |

                   ### request
                   ```json
                   {"email": "automation1@quiz.com", "password": "xxx"}
                   ```

                   ### return
                   ```json
                   {"token": "xxx"}
                   ```
                   @@@
                   """
        try:
            # parse json input
            email = request.json["email"]
            password = request.json["password"]
        except Exception as e:
            app.logger.exception(str(e))
            return utils.error_response(utils.InternalError.ParamError.value)
        app.logger.info("token: %s, endpoint: %s, json: %s, params: %s" %
                        (request.cookies, "%s/login" % api_prefix, request.json, request.args))
        # call login controller
        err, data = quiz_controller.login_controller(email, password)
        if err:
            app.logger.error("response: %s" % str(err))
            return utils.error_response(err)
        app.logger.info("response: %s" % str(data))
        return utils.common_json_response(data, method=sys._getframe().f_code.co_name)


api.add_resource(UserTokenResource, "%s/login" % api_prefix)

# Api /quiz/create
class QuizResource(Resource):
    def post(self):
        """Create a quiz

                   @@@
                   ### json
                   |  args | nullable | request type | type |  remarks |
                   |-------|----------|--------------|------|----------|
                   | title |  false   |    body      | str  | Quiz Demo |
                   | questions  |  false   |    body      | list  | list  of maps |

                   ### headers
                   ```json
                    {"Authorization": "Bearer %s" % token}
                   ```

                   ### request
                   ```json
                   {'title': 'quiz demo from automation1@quiz.com',
                   'questions': [
                                    {
                                    'question': 'How much is 1 + 1?',
                                    'options': [1, 2, 3, 4],
                                    'answers': [2, 2, 2],
                                    'single_answer': 1
                                    },
                                    ...
    ]
}
                   ```

                   ### return
                   ```json
                   {"added": "xxx"}
                   ```
                   @@@
                   """
        try:
            # fetch token
            token = request.headers.get("Authorization").split()[-1]
            if not token:
                return utils.error_response(utils.InternalError.NotAuthenticatedUser.value)
            # parse json format input
            questions = request.json["questions"]
            title = request.json["title"]
            if not questions:
                return utils.error_response(utils.InternalError.ParamError.value)
        except Exception as e:
            app.logger.exception(str(e))
            return utils.error_response(utils.InternalError.ParamError.value)
        app.logger.info("token: %s, endpoint: %s, json: %s, params: %s" %
                        (request.cookies, "%s/quiz" % api_prefix, request.json, request.args))
        # call create quiz controller
        err, data = quiz_controller.create_quiz_controller(token, questions, title)
        if err:
            app.logger.error("response: %s" % str(err))
            return utils.error_response(err)
        app.logger.info("response: %s" % str(data))
        return utils.common_json_response(data, method=sys._getframe().f_code.co_name)

    def delete(self):
        """Delete one's own quiz

                   @@@
                   ### args
                   |  args | nullable | request type | type |  remarks |
                   |-------|----------|--------------|------|----------|
                   | id |  false   |    body      | str  |  |

                    ### headers
                   ```json
                    {"Authorization": "Bearer %s" % token}
                   ```

                   ### request
                   ```params
                    {"id": "xxx"}
                   ```

                   ### no return
                   @@@
                   """
        try:
            # fetch token
            token = request.headers.get("Authorization").split()[-1]
            if not token:
                return utils.error_response(utils.InternalError.NotAuthenticatedUser.value)
            # parse input params
            id = request.args.get("id")
        except Exception as e:
            app.logger.exception(str(e))
            return utils.error_response(utils.InternalError.ParamError.value)
        app.logger.info("token: %s, endpoint: %s, params: %s" % (request.cookies, "%s/quiz" % api_prefix, request.args))
        # call delete quiz controller
        err, data = quiz_controller.delete_quiz_controller(token, id)
        if err:
            app.logger.error("response: %s" % str(err))
            return utils.error_response(err)
        app.logger.info("response: %s" % str(data))
        return utils.common_json_response(data, method=sys._getframe().f_code.co_name)

    def get(self):
        """Get a list of quizzes created by the user

                   @@@
                   ### no args

                   ### headers
                   ```json
                    {"Authorization": "Bearer %s" % token}
                   ```

                   ### return
                   ```json
                   [
                    {
                     "creator": "automation1@quiz.com",
                      "id": "8g49vQYLP6Y3nRxw",
                      "published": 0,
                      "question_count": 4,
                      "title": "quiz demo from automation1@quiz.com"
                    },
                    ...
]
                   ```
                   @@@
                   """
        try:
            # fetch token
            token = request.headers.get("Authorization").split()[-1]
            if not token:
                return utils.error_response(utils.InternalError.NotAuthenticatedUser.value)
        except Exception as e:
            app.logger.exception(str(e))
            return utils.error_response(utils.InternalError.ParamError.value)
        app.logger.info("token: %s, endpoint: %s, params: %s" % (request.cookies, "%s/quiz" % api_prefix, request.args))
        # call get own quiz list controller
        err, data = quiz_controller.get_own_quizzes_controller(token)
        if err:
            app.logger.error("response: %s" % str(err))
            return utils.error_response(err)
        app.logger.info("response: %s" % str(data))
        return utils.common_json_response(data, method=sys._getframe().f_code.co_name)


api.add_resource(QuizResource, "%s/quiz" % api_prefix)


# Api /quiz/details
class QuizDetailsResource(Resource):
    def get(self):
        """Get one's own quiz details by id

                   @@@
                   ### args
                   |  args | nullable | request type | type |  remarks |
                   |-------|----------|--------------|------|----------|
                   | id |  false   |    body      | str  |  |

                   ### headers
                   ```json
                    {"Authorization": "Bearer %s" % token}
                   ```

                   ### request
                   ```params
                    {"id": "xxx"}
                   ```

                   ### return
                   ```json
                   {
                    "creator": "automation1@quiz.com",
                    "id": "6PxZQDYbDarqpo3k",
                    "published": 1,
                    "questions": [
                      {
                        "answers": [
                          2
                        ],
                        "id": 222,
                        "options": [
                          1,
                          514,
                          2,
                          3,
                          4
                        ],
                        "question": "How much is 1 + 1?updated",
                        "single_answer": 1
                      },
                      ...
                    ],
                    "title": "quiz demo from automation1@quiz.com_updated"
}
                   ```
                   @@@
                   """
        try:
            # fetch token
            token = request.headers.get("Authorization").split()[-1]
            if not token:
                return utils.error_response(utils.InternalError.NotAuthenticatedUser.value)
            # parse input params
            id = request.args["id"]
        except Exception as e:
            app.logger.exception(str(e))
            return utils.error_response(utils.InternalError.ParamError.value)
        app.logger.info("token: %s, endpoint: %s, params: %s" %
                        (request.cookies, "%s/quiz/details" % api_prefix, request.args))
        # call get quiz details for owners controller
        err, data = quiz_controller.get_own_quiz_details_controller(token, id)
        if err:
            app.logger.error("response: %s" % str(err))
            return utils.error_response(err)
        app.logger.info("response: %s" % str(data))
        return utils.common_json_response(data, method=sys._getframe().f_code.co_name)


api.add_resource(QuizDetailsResource, "%s/quiz/details" % api_prefix)


# Api /quiz/solve/list
class QuizSolveListResource(Resource):
    def get(self):
        """Get the quiz list to solve

                   @@@
                   ### no args

                   ### headers
                   ```json
                    {"Authorization": "Bearer %s" % token}
                   ```

                   ### return
                   ```json
                   [
                    {
                      "creator": "automation2@quiz.com",
                      "id": "vaV6zlYEmMYRA1Zd",
                      "question_count": 4,
                      "title": "quiz demo from automation2@quiz.com"
                    },
                    ...
]
                   ```
                   @@@
                   """
        try:
            # fetch token
            token = request.headers.get("Authorization").split()[-1]
            if not token:
                return utils.error_response(utils.InternalError.NotAuthenticatedUser.value)
        except Exception as e:
            app.logger.exception(str(e))
            return utils.error_response(utils.InternalError.ParamError.value)
        app.logger.info("token: %s, endpoint: %s, params: %s" %
                        (request.cookies, "%s/quiz/solve/list" % api_prefix, request.args))
        # call get available quiz list to solve controller
        err, data = quiz_controller.get_quizzes_to_solve(token)
        if err:
            app.logger.error("response: %s" % str(err))
            return utils.error_response(err)
        app.logger.info("response: %s" % str(data))
        return utils.common_json_response(data, method=sys._getframe().f_code.co_name)


api.add_resource(QuizSolveListResource, "%s/quiz/solve/list" % api_prefix)


# Api /quiz/solve
class QuizSolveResource(Resource):
    def get(self):
        """Get a quiz details to solve by id

                   @@@
                   ### args
                   |  args | nullable | request type | type |  remarks |
                   |-------|----------|--------------|------|----------|
                   | id |  false      |    body      | str  |          |

                   ### headers
                   ```json
                    {"Authorization": "Bearer %s" % token}
                   ```
                   ### request
                   ```params
                    {"id": "xxx"}
                   ```

                   ### return
                   ```json
                   {
                    "creator": "automation2@quiz.com",
                    "id": "vaV6zlYEmMYRA1Zd",
                    "questions": [
                      {
                        "id": 206,
                        "options": [
                          1,
                          2,
                          3,
                          4
                        ],
                        "question": "How much is 1 + 1?",
                        "single_answer": 1
                      },
                      ...
                    ],
                    "title": "quiz demo from automation2@quiz.com"
}
                   ```
                   @@@
                   """
        try:
            # fetch token
            token = request.headers.get("Authorization").split()[-1]
            if not token:
                return utils.error_response(utils.InternalError.NotAuthenticatedUser.value)
            # parse input params
            id = request.args["id"]
        except Exception as e:
            app.logger.exception(str(e))
            return utils.error_response(utils.InternalError.ParamError.value)
        app.logger.info("token: %s, endpoint: %s, params: %s" %
                        (request.cookies, "%s/quiz/solve" % api_prefix, request.args))
        # call get a quiz details to solve controller
        err, data = quiz_controller.get_a_quiz_to_solve(token, id)
        if err:
            app.logger.error("response: %s" % str(err))
            return utils.error_response(err)
        app.logger.info("response: %s" % str(data))
        return utils.common_json_response(data, method=sys._getframe().f_code.co_name)


    def post(self):
        """Submit a quiz solution
          @@@
          ### json
           |  args | nullable | request type | type |  remarks |
           |-------|----------|--------------|------|----------|
           | id    |  false   |    body      | str  | quiz id  |
           | solution |  false |    body     | list  | list  of maps |

           ### headers
           ```json
            {"Authorization": "Bearer %s" % token}
           ```
           ### request
           ```json
            {
                'id': 'BPRnODYkkEYeVLwG',
                'solution': [
                                {
                                    'question_id': 182,
                                    'answers': [3]
                                },
                                ...
                            ]
}
           ```
           ### return
           ```json
           {
                "id": 15,
                "quiz_creator": "automation1@quiz.com",
                "quiz_id": "BPRnODYkkEYeVLwG",
                "quiz_title": "quiz demo from automation1@quiz.com",
                "solution": [
                  {
                    "id": 57,
                    "options": [
                      1,
                      2,
                      3,
                      4
                    ],
                    "question": "How much is 1 + 1?",
                    "question_id": 182,
                    "single_answer": 1,
                    "user_answers": [
                      3
                    ],
                    "user_score": "-100%"
                  },
                  ...
                ],
                "user_score": "25%"
}
           ```
           @@@
           """
        try:
            # fetch token
            token = request.headers.get("Authorization").split()[-1]
            if not token:
                return utils.error_response(utils.InternalError.NotAuthenticatedUser.value)
            # parse json format input
            id = request.json["id"]
            solution = request.json["solution"]
        except Exception as e:
            app.logger.exception(str(e))
            return utils.error_response(utils.InternalError.ParamError.value)
        app.logger.info("token: %s, endpoint: %s, json: %s, params: %s" %
                        (request.cookies, "%s/quiz/solve" % api_prefix, request.json, request.args))
        # call submit a quiz solution controller
        err, data = quiz_controller.submit_solution_controller(token, id, solution)
        if err:
            app.logger.error("response: %s" % str(err))
            return utils.error_response(err)
        app.logger.info("response: %s" % str(data))
        return utils.common_json_response(data, method=sys._getframe().f_code.co_name)


api.add_resource(QuizSolveResource, "%s/quiz/solve" % api_prefix)


# Api /solution/list
class SolutionListResource(Resource):
    def get(self):
        """Get own submitted solution list
        @@@
           ### no args

           ### headers
           ```json
            {"Authorization": "Bearer %s" % token}
           ```

           ### return
        ```json
           [
                {
                  "id": 19,
                  "quiz_creator": "automation1@quiz.com",
                  "quiz_id": "6PxZQDYbDarqpo3k",
                  "quiz_title": "quiz demo from automation1@quiz.com_updated",
                  "user_score": "0%"
                },
                ...
]
        ```
        @@@
        """
        try:
            # fetch token
            token = request.headers.get("Authorization").split()[-1]
            if not token:
                return utils.error_response(utils.InternalError.NotAuthenticatedUser.value)
        except Exception as e:
            app.logger.exception(str(e))
            return utils.error_response(utils.InternalError.ParamError.value)
        app.logger.info("token: %s, endpoint: %s, params: %s" %
                        (request.cookies, "%s/solution/list" % api_prefix, request.args))
        # call solution list for submitted user controller
        err, data = quiz_controller.get_own_solution_list(token)
        if err:
            app.logger.error("response: %s" % str(err))
            return utils.error_response(err)
        app.logger.info("response: %s" % str(data))
        return utils.common_json_response(data, method=sys._getframe().f_code.co_name)


api.add_resource(SolutionListResource, "%s/solution/list" % api_prefix)


# Api /solution/details
class SolutionDetailsResource(Resource):
    def get(self):
        """Get own submitted solution details

                @@@
                   ### args
                   |  args | nullable | request type | type |  remarks |
                   |-------|----------|--------------|------|----------|
                   | id |  false      |    body      | int  |          |

                   ### headers
                   ```json
                    {"Authorization": "Bearer %s" % token}
                   ```

                   ### request
                   ```json
                    {"id": 19}
                   ```

                   ### return
                   ```json
                   {
                        "id": "19",
                        "quiz_creator": "automation1@quiz.com",
                        "quiz_id": "6PxZQDYbDarqpo3k",
                        "quiz_title": "quiz demo from automation1@quiz.com_updated",
                        "solution": [
                          {
                            "id": 73,
                            "options": [
                              1,
                              514,
                              2,
                              3,
                              4
                            ],
                            "question": "How much is 1 + 1?updated",
                            "question_id": 222,
                            "single_answer": 1,
                            "user_answers": [
                              2
                            ],
                            "user_score": "100%"
                          },
                          ...
                        ],
                        "user_score": "0%"
    }
    ```

@@@
"""
        try:
            # fetch token
            token = request.headers.get("Authorization").split()[-1]
            if not token:
                return utils.error_response(utils.InternalError.NotAuthenticatedUser.value)
            # parse input params
            id = request.args["id"]
        except Exception as e:
            app.logger.exception(str(e))
            return utils.error_response(utils.InternalError.ParamError.value)
        app.logger.info("token: %s, endpoint: %s, params: %s" %
                        (request.cookies, "%s/solution/details" % api_prefix, request.args))
        # call get solution details for submitted user / quiz owner controller
        err, data = quiz_controller.get_own_solution_details(token, id)
        if err:
            app.logger.error("response: %s" % str(err))
            return utils.error_response(err)
        app.logger.info("response: %s" % str(data))
        return utils.common_json_response(data, method=sys._getframe().f_code.co_name)


api.add_resource(SolutionDetailsResource, "%s/solution/details" % api_prefix)


# Api /solution/my_quizzes
class SolutionToQuizzesResource(Resource):
    def get(self):
        """Get solution list submitted to user's own quizzes

        @@@
           ### no args

           ### headers
           ```json
            {"Authorization": "Bearer %s" % token}
           ```

            ### return
            ```json
                [
                    {
                      "creator": "automation1@quiz.com",
                      "quiz_id": "6PxZQDYbDarqpo3k",
                      "submitted_solutions": [
                        {
                          "score": "29%",
                          "solution_id": 16,
                          "submitted_user": "automation3@quiz.com"
                        },
                        {
                          "score": "0%",
                          "solution_id": 19,
                          "submitted_user": "automation2@quiz.com"
                        }
                      ],
                      "title": "quiz demo from automation1@quiz.com_updated"
                    },
                 ...
                  ]
            ```
            @@@
        """
        try:
            # fetch token
            token = request.headers.get("Authorization").split()[-1]
            if not token:
                return utils.error_response(utils.InternalError.NotAuthenticatedUser.value)
        except Exception as e:
            app.logger.exception(str(e))
            return utils.error_response(utils.InternalError.ParamError.value)
        app.logger.info("token: %s, endpoint: %s, params: %s" %
                        (request.cookies, "%s/solution/my_quizzes" % api_prefix, request.args))
        # call get solutions submitted to user's created quizzes controller
        err, data = quiz_controller.get_own_solution_to_quizzes_mapping_controller(token)
        if err:
            app.logger.error("response: %s" % str(err))
            return utils.error_response(err)
        app.logger.info("response: %s" % str(data))
        return utils.common_json_response(data, method=sys._getframe().f_code.co_name)


api.add_resource(SolutionToQuizzesResource, "%s/solution/my_quizzes" % api_prefix)


# Api /quiz/update
class QuizUpdateResource(Resource):
    def post(self):
        """Update a quiz

                   @@@
                   ### json
                   |  args | nullable | request type | type |  remarks |
                   |-------|----------|--------------|------|----------|
                   | id |  false      |    body      | str  |          |
                   | title  |  false   |    body      | str  |         |
                   | questions |  false |    body      | list  |  |

                   ### headers
                   ```json
                    {"Authorization": "Bearer %s" % token}
                   ```

                   ### request
                   ```json
                   {
                       'id': '6PxZQDYbDarqpo3k',
                       'title': 'quiz demo from automation1@quiz.com_updated',
                       'questions': [
                                        {
                                            'question': 'How much is 1 + 1?updated',
                                            'options': [1, 2, 3, 4, 514],
                                            'answers': [2],
                                            'single_answer': 1},
                                            ...
                                        ]
                    }
                   ```

                   ### return
                   ```json
                   {"updated": "6PxZQDYbDarqpo3k" }
                   ```
                   @@@
                   """
        try:
            # fetch token
            token = request.headers.get("Authorization").split()[-1]
            if not token:
                return utils.error_response(utils.InternalError.NotAuthenticatedUser.value)
            # parse json format input
            questions = request.json["questions"]
            title = request.json["title"]
            id = request.json["id"]
            if not questions:
                return utils.error_response(utils.InternalError.ParamError.value)
        except Exception as e:
            app.logger.exception(str(e))
            return utils.error_response(utils.InternalError.ParamError.value)
        app.logger.info("token: %s, endpoint: %s, json: %s, params: %s" %
                        (request.cookies, "%s/quiz" % api_prefix, request.json, request.args))
        # call update quiz controller
        err, data = quiz_controller.update_quiz_controller(token, id, questions, title)
        if err:
            app.logger.error("response: %s" % str(err))
            return utils.error_response(err)
        app.logger.info("response: %s" % str(data))
        return utils.common_json_response(data, method=sys._getframe().f_code.co_name)


api.add_resource(QuizUpdateResource, "%s/quiz/update" % api_prefix)


# Api /quiz/publish
class QuizPublishResource(Resource):
    def post(self):
        """Publish a quiz
        @@@
           ### args
           |  args | nullable | request type | type |  remarks |
           |-------|----------|--------------|------|----------|
           | id |  false      |    body      | int  |          |

           ### headers
           ```json
            {"Authorization": "Bearer %s" % token}
           ```

           ### request
           ```json
           {'id': 'BPRnODYkkEYeVLwG'}
           ```

           ### return
           ```json
           {"published": "BPRnODYkkEYeVLwG"}
           ```
       @@@
       """
        try:
            # fetch token
            token = request.headers.get("Authorization").split()[-1]
            if not token:
                return utils.error_response(utils.InternalError.NotAuthenticatedUser.value)
            # parse json format input
            id = request.args["id"]
        except Exception as e:
            app.logger.exception(str(e))
            return utils.error_response(utils.InternalError.ParamError.value)
        app.logger.info("token: %s, endpoint: %s, params: %s" %
                        (request.cookies, "%s/quiz" % api_prefix, request.args))
        # call publish quiz controller
        err, data = quiz_controller.publish_quiz_controller(token, id)
        if err:
            app.logger.error("response: %s" % str(err))
            return utils.error_response(err)
        app.logger.info("response: %s" % str(data))
        return utils.common_json_response(data, method=sys._getframe().f_code.co_name)


api.add_resource(QuizPublishResource, "%s/quiz/publish" % api_prefix)


if __name__ == "__main__":
    app.run(debug=True)
