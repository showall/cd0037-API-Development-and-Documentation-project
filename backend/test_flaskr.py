import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, String, Integer, create_engine
from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = 'postgresql://{}@{}/{}'.format("postgres:demo",'localhost:5432',self.database_name)
        setup_db(self.app, self.database_path)
       #database_path = 'postgres://{}@{}/{}'.format("postgres:demo",'localhost:5432',database_name)
        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """

#----------------------------------------------------------------------------#
# Tests for GET '/categories'
#----------------------------------------------------------------------------#

    def test_get_categories(self):
        res = self.client().get('/categories')
        self.assertEqual(res.status_code, 200)

    def test_post_categories(self):
        res = self.client().post('/categories')
        self.assertEqual(res.status_code, 405) #method not allowed

#----------------------------------------------------------------------------#
# Tests for GET '/questions?page=${integer}'
#----------------------------------------------------------------------------#
    def test_get_questions_with_pagination(self):
        res = self.client().get('/questions?page=1')
        self.assertEqual(res.status_code, 200)

    def test_delete_questions_with_pagination(self):
        """Test if could delete entire page"""
        res = self.client().delete('/questions?page=1000')
        self.assertEqual(res.status_code, 405)

#----------------------------------------------------------------------------#
# Tests for GET '/categories/${id}/questions'
#----------------------------------------------------------------------------#
    def test_get_questions_by_categoryid(self):
        res = self.client().get('/categories/2/questions')
        self.assertEqual(res.status_code, 200)
    def test_post_questions_by_categoryid(self):
        res = self.client().post('/categories/2/questions')
        self.assertEqual(res.status_code, 405)

#-------------------------------------------------h---------------------------#
# Tests DELETE '/questions/${id}'
#----------------------------------------------------------------------------#
    
    def test_delete_question(self):
        last_id = Question.query.order_by(Question.id).first().id # contains id from last created category
        res = self.client().delete('/questions/'+str(last_id))
        self.assertEqual(res.status_code, 200)

    def test_delete_invalid_question(self):
        invalid_id = 0
        res = self.client().delete('/questions/'+str(invalid_id))
        self.assertEqual(res.status_code, 422) 

#----------------------------------------------------------------------------#
# Tests for POST '/quizzes'
#----------------------------------------------------------------------------#
    def test_post_quiz(self):
        request = {
        "previous_questions": [1, 4, 20, 15],
        "quiz_category": 'Science'
        }

        res = self.client().post('/quizzes', json = request)
        self.assertEqual(res.status_code, 200)
    
    def test_post_quiz_with_invalid_category(self):
        request = {
        "previous_questions": [1, 4, 20, 15],
        "quiz_category": 'science'
        }
        res = self.client().post('/quizzes', json = request)
        self.assertEqual(res.status_code, 422)

#----------------------------------------------------------------------------#
# Tests for POST '/questions'
#----------------------------------------------------------------------------#

    def test_post_question(self):

        # Used as header to POST /question
        request = {
        'question':  'Heres a new question string',
        'answer':  'Heres a new answer string',
        'difficulty': 1,
        'category': 3,
         }

        res = self.client().post('/questions', json = request)
        self.assertEqual(res.status_code, 200)

    def test_post_invalid_question(self):
        """Test POST a new question with missing category """
        invalid_request = {
        'questions':  'Heres a new question string',
        'answer':  'Heres a new answer string',
        'difficulty': 1
         }
        res = self.client().post('/questions', json = invalid_request)
        self.assertEqual(res.status_code, 422)

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()