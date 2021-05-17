import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  
  '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
  CORS(app)

  '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''
  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Hearders', 'Content-Type,Autorization,true')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PATCH,POST,DELETE,OPTIONS')
    return response

  '''
  @TODO: 
  Create an endpoint to handle GET requests 
  for all available categories.
  '''
  @app.route('/categories')
  def get_categories():

    try: 
      categories = Category.query.order_by(Category.id).all()
    except:
      abort(422)

    list_categories = [category.format() for category in categories]
    
    dict_categories = {}
    if len(list_categories) == 0:
      abort(404)
    else:
      for cat in list_categories:
        dict_categories[cat["id"]] = cat["type"]

    return jsonify({
      'success': True,
      'categories': dict_categories,
      'number_categories': len(list_categories)
    })

  '''
  @TODO: 
  Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. 

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  '''

  def paginate_questions(request, selection):
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE
    
    list_questions = [question.format() for question in selection]
    current_list = list_questions[start:end]

    return current_list
  
  @app.route('/questions')
  def get_questions():
    
    try: 
      questions = Question.query.order_by(Question.id).all()
      categories = Category.query.order_by(Category.id).all()
    except: 
      abort(422)

    current_list_questions = paginate_questions(request, questions)
    list_categories = [category.format() for category in categories]

    if len(current_list_questions) == 0:
      abort(404)

    dict_categories = {}
    for cat in list_categories:
      dict_categories[cat['id']] = cat['type']

    return jsonify({
      'success': True,
      'questions': current_list_questions,
      'page': request.args.get('page', 1, type=int),
      'total_questions': len(questions),
      'categories': dict_categories,
      'current_category': None
    })

  '''
  @TODO: 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''

  @app.route('/questions/<int:question_id>', methods=['DELETE'])
  def delete_question(question_id):
    
    try: 
      question_to_delete = Question.query.filter(Question.id == question_id).one_or_none()
    except: 
      abort(422)

    if question_to_delete is None:
      abort(404)

    question_to_delete.delete()

    return jsonify({
      'success':True,
      'deleted': question_id,
      'total_number_questions': len(Question.query.all())
    })

  '''
  @TODO: 
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''

  @app.route('/questions', methods=['POST'])
  def add_question():
    
    body = request.get_json()

    if body is None: 
      abort(400)

    new_question = body.get('question', None)
    new_answer = body.get('answer', None)
    new_category = body.get('category', None)
    new_difficulty = body.get('difficulty', None)

    if all(v is not None for v in [new_question, new_answer, new_category, new_difficulty]):
      try:
        question_to_add = Question(question = new_question, answer = new_answer, category = new_category, difficulty = new_difficulty)
        question_to_add.insert()

        return jsonify({
          'success': True,
          'created': question_to_add.id,
          'total_number_questions': len(Question.query.all())
        })

      except: 
        abort(422)
    
    else:
      abort(422)


  '''
  @TODO: 
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''

  @app.route('/questions/search', methods=['POST'])
  def search_questions():
    
    data = request.get_json()
    
    if data is None:
      abort(400)

    search_terms = data.get('searchTerm', None)

    if search_terms:
      try:
        list_questions = Question.query.order_by(Question.id).filter(Question.question.ilike(f'%{search_terms}%'))
      except:
        abort(422)

      formatted_list_questions = [question.format() for question in list_questions]
      
      if formatted_list_questions:
        return jsonify({
          'success': True,
          'search_terms': search_terms,
          'questions': formatted_list_questions,
          'total_questions': list_questions.count(),
          'current_category': None
        })
      else:
        abort(404)
    else:
      abort(400)

  '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''

  @app.route('/categories/<int:category_id>/questions')
  def get_question_by_cat(category_id):

    #models.py is only what the python application can see and know. foreign key is defined in trivia.psql
    try:
      list_questions = Question.query.order_by(Question.id).filter(Question.category == str(category_id)).all() 
    except:
      abort(422)

    if len(list_questions) == 0:
      abort(404)

    formatted_list_questions = [question.format() for question in list_questions]

    return jsonify({
      'questions': formatted_list_questions,
      'current_category': category_id,
      'success': True,
      'total_questions': len(formatted_list_questions)
    })
  

  '''
  @TODO: 
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''

  @app.route('/quizzes', methods=['POST'])
  def get_random_question():
    data = request.get_json()

    #if no json object is passed, the request is invalid.  
    if data is None:
      abort(400)

    category = data.get('quiz_category', None)
    previous_questions = data.get('previous_questions', [])

    #if there are no value associated to 'quiz_category'
    if category is None: 
      abort(400)

    try:
      if category['id'] != 0:
        list_questions = Question.query.filter(Question.category == category['id']).all()
      else:
        list_questions = Question.query.all()
    except: 
      abort(404)

    #In case the list of question is empty. 
    if not list_questions:
      abort(404)

    #To randomize our list. Not required since the order of results returned change for every query, but this adds a level of randomness. 
    random.shuffle(list_questions)

    for q in list_questions:
      if q.id not in previous_questions:
        #the front end is taking care of updating the previous_questions array
        return jsonify({
          'question': q.format(),
          'quiz_category': q.category,
          'success': True
        })

    #return None if all the questions of the category have been sent out. 
    return jsonify({
      'question': None,
      'quiz_category': category['id'],
      'success': True
    })

  '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''

  @app.errorhandler(400)
  def invalide_request(error):
    return jsonify({
      'success': False,
      'error': 400,
      'message': 'invalid request'
    }), 400
  
  @app.errorhandler(404)
  def not_found(error):
    return jsonify({
      'error': 404,
      'success': False,
      'message': 'resource not found'
    }), 404

  @app.errorhandler(422)
  def cant_process(error):
    return jsonify({
      'success': False, 
      'error': 422,
      'message': 'unable to be processed'
    }), 422

  return app

    