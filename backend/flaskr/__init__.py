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
  page = request.args.get('page', 1, type=int)
  start =  (page - 1) * QUESTIONS_PER_PAGE
  end = start + QUESTIONS_PER_PAGE
  selection = [{"id":item.id, "question":item.question, "answer":item.answer, "difficulty":item.difficulty, "category":item.category} for item in selection]
  current_selection = selection[start:end]
  return current_selection


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    """
    @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    """
    CORS(app)
    """
    @TODO: Use the after_request decorator to set Access-Control-Allow
    """
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        return response


    """
    @TODO:
    Create an endpoint to handle GET requests
    for all available categories.
    """
    @app.route('/categories')
    def retrieve_categories():
        category = Category.query.all()
        category = {item.id : item.type for item in category}
        return jsonify({
        'categories': category,
        })


    """
    @TODO:
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    """
    @app.route('/questions', methods=["GET"])
    def retrieve_questions():
        currentCategory = None
        question = Question.query.order_by(Question.id).all()
        count = len(question)
        category = Category.query.all()
        question = paginate_question(request,question)
        category = {item.id : item.type for item in category}
        return jsonify(({
        'questions': question,
        'totalQuestions': count,
        'categories': category,
        'currentCategory': currentCategory,
        }))

    @app.route('/categories/<id>/questions',methods=["GET"])
    def retrieve_specific_question(id):
        question = Question.query.order_by(Question.id).all()
        count = len(question)
        question = Question.query.filter(Question.category==id).all()
        category = Category.query.filter(Category.id==id).one_or_none()
        selection = [{"id":item.id, "question":item.question, "difficulty":item.difficulty, "category":item.category} for item in question]
        return jsonify(({
        'questions':  selection,
        'totalQuestions': count,
        'currentCategory': category.id,
        }))

    """

    @TODO:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """
    @app.route('/questions/<id>', methods=['DELETE'])
    def delete_specific_question(id):
        try:
            question = Question.query.filter(Question.id == id).one_or_none()
            if question is None:
                abort(404)
            question.delete()
            return jsonify({
                'deleted': str(id),
                }),200        
        except:
           abort(422)

    """
    @TODO:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """
    @app.route('/questions', methods=['GET','POST'])
    def create_question():
        body = request.get_json()
        question = body.get('question', None)
        answer = body.get('answer', None)
        difficulty = body.get('difficulty', None)
        category = body.get('category', None)
        searchTerm = body.get('searchTerm', None)
        if searchTerm == None:
            if question == None or answer == None:
                abort(422)
            try:
                question = Question(question,answer, category,difficulty)
                question.insert()
                selection = Question.query.order_by(Question.id).all()
                selection = [item.format() for item in selection]
                return jsonify({
                    'success': True,
                    'created': question.id,
                    'questions': selection,
                    'totalQuestions': len(Question.query.all())
                    })
            except:
                abort(422)
        else :
            try:
                selection = Question.query.filter(Question.question.ilike("%" + searchTerm + "%")).order_by(Question.id).all()
                selection = [item.format() for item in selection]
                return jsonify(({
                'questions':  selection,
                'totalQuestions': len(Question.query.order_by(Question.id).all()),
                'currentCategory': "unknown",
                }))
            except:
                abort(422)            

    """
    @TODO:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """

    """
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """

    """
    @TODO:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    """
    @app.route('/quizzes', methods=['GET','POST'])
    def play_quiz():
        #try:
        body = request.get_json()
        if body != None:
            previous_questions = body.get('previous_questions',[])
            quiz_category = body.get('quiz_category', None)
            if quiz_category == None:
                category_id = random.randint(1,6)
                category = Category.query.filter(Category.id==str(category_id)).one()
            else : 
                try:
                    category = Category.query.filter(Category.type==quiz_category).one()
                    selection = Question.query.filter(Question.id.notin_(previous_questions)).filter(Question.category==str(category.id)).all()
                except:
                    abort(422)
        else:
            selection = Question.query.all()  
        selection = [question.format() for question in selection]
        if len(selection)>0:
            question_picked = selection[random.randint(0, len(selection)-1)]
        else:
            question_picked = None        
        return jsonify(({
        'question':  question_picked,
        }))


    """
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    """
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "success": False, 
            "error": 400,
            "message": "bad request"
            }), 400

    @app.errorhandler(404)
    def ressource_not_found(error):
        return jsonify({
            "success": False, 
            "error": 404,
            "message": "resource not found"
            }), 404

    @app.errorhandler(405)
    def method_not_allowed(error):
        return jsonify({
            "success": False, 
            "error": 405,
            "message": "method not allowed"
            }), 405

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            "success": False, 
            "error": 422,
            "message": "unprocessable"
            }), 422

    @app.errorhandler(500)
    def internal_server_error(error):
        return jsonify({
            "success": False, 
            "error": 500,
            "message": "internal server error"
            }), 500

    return app

