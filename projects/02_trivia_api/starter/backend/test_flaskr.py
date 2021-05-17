import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    #setUp is run before every test method.
    def setUp(self):
        """Define test variables and initialize app.""" 
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgres://{}/{}".format('localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

        self.new_question = {
            'question': 'Who is a little puppy',
            'answer': 'Romeo',
            'category': 4,
            'difficulty': 3 
        }

    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """

    def test_get_categories(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['categories'])
        self.assertTrue(data['number_categories'])

    #test is failing because our database has categories
    def test_404_if_no_categories_found(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    def test_post_new_question(self):
        res = self.client().post('/questions', json=self.new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['created'])
        self.assertTrue(data['total_number_questions'])
        self.assertEqual(data['success'], True)

    def test_422_post_error_incomplete_question(self):
        #defining incomplete question to send to endpoint 
        self.incomplete_question = {
            'question': 'What is my name?',
            'difficulty': 3 
        }
        res =  self.client().post('/questions', json=self.incomplete_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'unable to be processed')

    def test_400_post_question_without_sending_question(self):
        res = self.client().post('/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'invalid request')

    def test_get_questions(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertTrue(len(data['questions']))
        self.assertTrue(data['page'])
        self.assertTrue(data['total_questions'])
        self.assertTrue(data['categories'])

    #test if failing because our database has questions.
    def test_404_if_no_questions(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    def test_404_no_questions_returned_because_page_number_too_high(self):
        res = self.client().get('/questions?page=1000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['message'], 'resource not found')
        self.assertFalse(data['success'])

    def test_get_questions_by_category(self):
        res = self.client().get('/categories/4/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['current_category'], 4)
        self.assertTrue(data['questions'])
        self.assertTrue(data['total_questions'])
    
    def test_404_get_questions_by_category_when_category_does_not_exist(self):
        res = self.client().get('/categories/40/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    def test_404_get_questions_by_category_when_category_is_a_string(self):
        res = self.client().get('/categories/science/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    def test_delete_question(self):
        question_id = 14

        res = self.client().delete('/questions/' + str(question_id))
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['deleted'], question_id)
        self.assertTrue(data['total_number_questions'])

    def test_404_delete_question_does_not_exist(self):
        question_id = 1000

        res = self.client().delete('/questions/' + str(question_id))
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    def test_search_questions(self):
        res = self.client().post('/questions/search', json={'searchTerm': 'little puppy'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['search_terms'], 'little puppy')
        self.assertTrue(data['questions'])
        self.assertTrue(data['total_questions'])
        self.assertFalse(data['current_category'])

    def test_404_search_title_without_resutls(self):
        res = self.client().post('/questions/search', json={'searchTerm':'batman'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    def test_404_failed_search_question(self):
        res = self.client().post('/questions/search', json={'searchTerm':'batman'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    def test_400_no_search_term_to_search(self):
        res = self.client().post('/questions/search')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'invalid request')

    def test_get_random_question_for_quizz(self):
        res = self.client().post('/quizzes', json={'quiz_category': {'id':'4'}, 'previous_questions': [{'question': 'placeholder question?', 'id': '1'}]})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['quiz_category'], '4')
        self.assertEqual(data['success'], True)
        self.assertTrue(data['question'])

    def test_get_random_question_from_any_category(self):
        res = self.client().post('/quizzes', json={'quiz_category': {'id': 0 }, 'previous_questions': []})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['question'])

    def test_get_random_question_for_quizz_without_category(self):
        res = self.client().post('/quizzes', json={'previous_questions':[1,2,3,4,5,6]})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'invalid request')
    
    def test_get_random_question_for_quizz_with_no_parameters(self):
        res = self.client().post('/quizzes')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'invalid request')

    def test_get_random_question_for_quizz_with_unexisting_category(self):
        res = self.client().post('/quizzes', json={'quiz_category':{'id' : '7'}})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    def test_no_more_question_in_that_category(self):
        #I pass as the previous question list, a list of integers with a range higher than the range of question ids -> all the questions ids will be a subset of that list, as long as we don't enter more than 250 questions.
        res = self.client().post('/quizzes', json={'quiz_category': {'id' : '4'}, 'previous_questions': list(range(1,251))})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertFalse(data['question'])
        self.assertEqual(data['quiz_category'], '4')

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()