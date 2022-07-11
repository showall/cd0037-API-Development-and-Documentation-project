from cgitb import reset
import os
from re import L
from flask import Flask, request, abort, jsonify, Response
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random
from werkzeug import Response
from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def paginate_question(request, selection):
    page = request.args.get("page", 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE
    selection = [
        {
            "id": item.id,
            "question": item.question,
            "answer": item.answer,
            "difficulty": item.difficulty,
            "category": item.category,
        }
        for item in selection
    ]
    current_selection = selection[start:end]
    return current_selection


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    CORS(app)

    @app.after_request
    def after_request(response):
        response.headers.add(
            "Access-Control-Allow-Headers", "Content-Type,Authorization,true"
        )
        response.headers.add(
            "Access-Control-Allow-Methods", "GET,PUT,POST,DELETE,OPTIONS"
        )
        return response

    @app.route("/categories")
    def retrieve_categories():
        category = Category.query.all()
        category = {item.id: item.type for item in category}
        return jsonify(
            {
                "categories": category,
            }
        )

    @app.route("/questions", methods=["GET"])
    def retrieve_questions():
        currentCategory = None
        question = Question.query.order_by(Question.id).all()
        count = len(question)
        category = Category.query.all()
        question = paginate_question(request, question)
        category = {item.id: item.type for item in category}
        return jsonify(
            (
                {
                    "questions": question,
                    "totalQuestions": count,
                    "categories": category,
                    "currentCategory": currentCategory,
                }
            )
        )

    @app.route("/categories/<id>/questions", methods=["GET"])
    def retrieve_specific_question(id):
        question = Question.query.order_by(Question.id).all()
        count = len(question)
        question = Question.query.filter(Question.category == id).all()
        category = Category.query.filter(Category.id == id).one_or_none()
        selection = [
            {
                "id": item.id,
                "question": item.question,
                "difficulty": item.difficulty,
                "category": item.category,
            }
            for item in question
        ]
        return jsonify(
            (
                {
                    "questions": selection,
                    "totalQuestions": count,
                    "currentCategory": category.id,
                }
            )
        )

    @app.route("/questions/<id>", methods=["DELETE"])
    def delete_specific_question(id):
        try:
            question = Question.query.filter(Question.id == id).one_or_none()
            if question is None:
                abort(404)
            question.delete()
            return (
                jsonify(
                    {
                        "deleted": str(id),
                    }
                ),
                200,
            )
        except Exception as e:
            abort(422)

    @app.route("/questions", methods=["GET", "POST"])
    def create_question():
        body = request.get_json()
        question = body.get("question", None)
        answer = body.get("answer", None)
        difficulty = body.get("difficulty", None)
        category = body.get("category", None)
        searchTerm = body.get("searchTerm", None)
        if searchTerm is None:
            if question is None or answer is None:
                abort(422)
            try:
                question = Question(question, answer, category, difficulty)
                question.insert()
                selection = Question.query.order_by(Question.id).all()
                selection = [item.format() for item in selection]
                return jsonify(
                    {
                        "success": True,
                        "created": question.id,
                        "questions": selection,
                        "totalQuestions": len(Question.query.all()),
                    }
                )
            except Exception as e:
                abort(422)
        else:
            try:
                selection = (
                    Question.query.filter(
                        Question.question.ilike("%" + searchTerm + "%")
                    )
                    .order_by(Question.id)
                    .all()
                )
                selection = [item.format() for item in selection]
                return jsonify(
                    (
                        {
                            "questions": selection,
                            "totalQuestions": len(
                                Question.query.order_by(Question.id).all()
                            ),
                            "currentCategory": "unknown",
                        }
                    )
                )
            except Exception as e:
                abort(422)

    @app.route("/quizzes", methods=["GET", "POST"])
    def play_quiz():
        if request is not None:
            body = request.get_json()
            previous_questions = body.get("previous_questions", [])
            quiz_category = body.get("quiz_category", None)
            if quiz_category is None or quiz_category["type"] == "click":
                category_id = random.randint(1, 6)
                category = Category.query.filter(
                    Category.id == str(category_id)).one()
                selection = (
                    Question.query.filter(
                        Question.id.notin_(previous_questions)) .filter(
                        Question.category == str(
                            category.id)) .all())
            else:
                try:
                    category = Category.query.filter(
                        Category.type == quiz_category["type"]
                    ).first()
                    selection = (
                        Question.query.filter(
                            Question.id.notin_(previous_questions)) .filter(
                            Question.category == str(
                                category.id)) .all())
                except Exception as e:
                    abort(422)
        else:
            selection = Question.query.all()
        selection = [question.format() for question in selection]
        if len(selection) > 0:
            question_picked = selection[random.randint(0, len(selection) - 1)]
        else:
            question_picked = None
        return jsonify(
            (
                {
                    "question": question_picked,
                }
            )
        )

    """
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    """

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({"success": False, "error": 400,
                       "message": "bad request"}), 400

    @app.errorhandler(404)
    def ressource_not_found(error):
        return (jsonify({"success": False, "error": 404,
                         "message": "resource not found"}), 404, )

    @app.errorhandler(405)
    def method_not_allowed(error):
        return (jsonify({"success": False, "error": 405,
                         "message": "method not allowed"}), 405, )

    @app.errorhandler(422)
    def unprocessable(error):
        return (
            jsonify({"success": False,
                     "error": 422,
                     "message": "unprocessable"
                     }),
            422,
        )

    @app.errorhandler(500)
    def internal_server_error(error):
        return (
            jsonify(
                {"success": False,
                 "error": 500,
                 "message": "internal server error"
                 }
            ),
            500,
        )

    return app
