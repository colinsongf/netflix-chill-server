import os
import json
import datetime
from math import sin, cos, tan, asin, acos, atan, sqrt, atan2

from flask import Flask, jsonify
import flask
from flask.ext.sqlalchemy import SQLAlchemy

from splinter import Browser

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ["DATABASE_URL"]
# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://hbrvgdoavvrkzy:97AbqwFr_7XFVq1paXIOi0Xl_Y@ec2-54-225-201-25.compute-1.amazonaws.com:5432/d92htefnn65sr'

# BEGIN BACKEND DATABASE IMPLEMENTATION

db = SQLAlchemy(app)

class User(db.Model):
  __tablename__ = 'users'
  id = db.Column(db.Integer(), nullable=False, primary_key=True, unique=True, autoincrement=True)
  netflix_username = db.Column(db.String(80), unique=True)
  netflix_password = db.Column(db.String(80))

  def __init__(self, username, password):
    self.netflix_username = username
    self.netflix_password = password

def add_user(nf_un, nf_pw):
  new_user = User(nf_un, nf_pw)
  db.session.add(new_user)
  db.session.flush()
  db.session.commit()
  print 'User added successfully.'
  return new_user.id

def get_user_by_username(nf_un):
  if len(User.query.filter_by(netflix_username=nf_un).all()) == 0:
    return None
  else:
    return User.query.filter_by(netflix_username=nf_un).all()[0]

def get_user_by_id(id):
  if len(User.query.filter_by(id=id).all()) == 0:
    return None
  else:
    return User.query.filter_by(id=id).all()[0]

def user_exists(nf_un):
  return (len(User.query.filter_by(netflix_username=nf_un).all()) != 0)

def user_id_exists(id):
  return (len(User.query.filter_by(id=id).all()) != 0)

class ChillRequest(db.Model):
  __tablename__ = 'chill_requests'
  id = db.Column(db.Integer(), nullable=False, primary_key=True, unique=True, autoincrement=True)
  #id = db.Column(db.Integer, primary_key=True)
  user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
  genre = db.Column(db.String(20))
  program_type = db.Column(db.Boolean())
  date = db.Column(db.Date())
  time_of_day = db.Column(db.String(20))
  latitude = db.Column(db.Float())
  longitude = db.Column(db.Float())

  def __init__(self, user_id, genre, program_type, date, time_of_day, latitude, longitude):
    self.user_id = user_id
    self.genre = genre
    self.program_type = program_type
    self.date = date
    self.time_of_day = time_of_day
    self.latitude = latitude
    self.longitude = longitude

def add_chill_request(user_id, genre, program_type, date, time_of_day, latitude, longitude):
  new_request = ChillRequest(user_id, genre, program_type, date, time_of_day, latitude, longitude)
  db.session.add(new_request)
  db.session.flush()
  db.session.commit()
  print 'Chill Request added successfully.'
  return new_request.id

def get_chill_request_by_id(cr_id):
  requests = ChillRequest.query.filter_by(id=cr_id).all()
  if len(requests) == 0:
    return None
  else:
    return requests[0].id

def get_chill_requests_by_user_id(user_id):
  return ChillRequest.query.filter_by(user_id=user_id).all()

def get_chill_request_matches(chill_request):
  MATCHES_LIMIT = 3
  matches = ChillRequest.query.filter(
    ChillRequest.user_id != chill_request.user_id,
    ChillRequest.date == chill_request.date,
    ChillRequest.time_of_day == chill_request.time_of_day).all()
  if len(matches) < MATCHES_LIMIT:
    top_matches = matches
  else:
    top_matches = matches[0:MATCHES_LIMIT]
    for match in matches:
      score = evaluate_compatibility(chill_request, match)
      for top_match in top_matches:
        if score > evaluate_compatibility(chill_request, top_match):
          top_matches.remove(top_match)
          top_matches.append(match)
  result = []
  index = 0
  for match in top_matches:
    result.append({})
    match_entry = result[index]
    user = get_user_by_id(match.user_id)
    match_entry['email'] = user.netflix_username
    match_entry['priority'] = evaluate_compatibility(match, chill_request)
    index += 1
  final_result = {}
  index = 0
  for match in top_matches:
    final_result[match.user_id] = result[index]
    index += 1
  return final_result

def get_chill_request_dict(request):
  result = {}
  result['user_id'] = str(request.user_id)
  result['type'] = request.program_type
  result['time'] = request.time_of_day
  result['genre'] = request.genre
  result['day'] = index_to_dow(request.date.weekday())
  return result

def evaluate_compatibility(cr1, cr2):
  score = 1
  if cr1.genre != cr2.genre:
    score *= .5
  if cr1.program_type != cr2.program_type:
    score *= .5
  DISTANCE_MAGIC_NUMBER = 1.07
  distance_score = DISTANCE_MAGIC_NUMBER ** -(calculate_distance(cr1, cr2))
  score *= distance_score
  return score

def calculate_distance(cr1, cr2):
  dlon = abs(cr2.longitude - cr1.longitude) 
  dlat = abs(cr2.latitude - cr1.latitude)
  a = (sin(dlat/2))**2 + cos(cr1.latitude) * cos(cr2.latitude) * (sin(dlon/2))**2 
  c = 2 * atan2(sqrt(a), sqrt(1-a))
  EARTH_RADIUS_MI = 3959
  EARTH_RADIUS_KM= 6371
  return EARTH_RADIUS_MI * c

def chill_request_exists(cr_id):
  return (len(ChillRequest.query.filter_by(id=cr_id).all()) != 0)

def verify_netflix_credentials(nf_un, nf_pw):
  """
  Super hacky patch.
  """
  return True
  """
  FIX THIS
  """
  BROWSER_DRIVER = 'django'
  NETLFIX_LOGIN_URL = 'https://www.netflix.com/Login?locale=en-US'
  NETFLIX_SUCCESS_URL = 'http://www.netflix.com/browse'
  EMAIL_FIELD_ID = 'email'
  PASSWORD_FIELD_ID = 'password'
  SIGN_IN_BUTTON_ID = 'login-form-contBtn'
  with Browser(BROWSER_DRIVER) as browser: 
    browser.visit(NETLFIX_LOGIN_URL)
    browser.fill(EMAIL_FIELD_ID, nf_un)
    browser.fill(PASSWORD_FIELD_ID, nf_pw)
    browser.find_by_id(SIGN_IN_BUTTON_ID).click()
    if browser.url == NETFLIX_SUCCESS_URL:
      print 'Netflix login valid.'
      return True
    else:
      print 'Netflix login invalid.'
      return False

def get_viewing_activity(user_id):
  NETFLIX_VIEWING_ACTIVITY_URL = 'https://www.netflix.com/WiViewingActivity'

# BEGIN API HELPER METHODS

# Takes in a string denoting a day of the week, and returns a date object representing
# the next occurence of that date
def process_date_from_string(date_string):
  today = datetime.date.today()
  current_weekday = today.weekday()
  target_weekday = get_weekday_int_from_string(date_string)
  day_delta = target_weekday-current_weekday
  if target_weekday < current_weekday:
    day_delta += 7
  delta = datetime.timedelta(days=target_weekday-current_weekday)
  return today + delta

# Returns a Python standard integer representing day of the week. Monday is 0. Sunday is 6.
def get_weekday_int_from_string(s):
  days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
  if s not in days:
    raise ValueError('Day of week does not match any predefined names.')
  return days.index(s)

# BEGIN API

@app.route('/')
def index():
  return 'Netflix and Chill API'

@app.route('/sign-in', methods=['POST'])
def sign_in():
  request_data = json.loads(flask.request.data)
  # Error checking here
  nf_un = request_data['nf_un']
  nf_pw = request_data['nf_pw']
  ERROR = -1
  # Case 1: User exists
  if user_exists(nf_un):
    if not nf_pw == get_user_by_username(nf_un).netflix_password:
      return create_user_id_response(ERROR)
    return create_user_id_response(get_user_by_username(nf_un).id)
  # Case 2: User doesn't exist, but has valid credentials
  if verify_netflix_credentials(nf_un, nf_pw):
    print 'Adding user.'
    add_user(nf_un, nf_pw)
    print 'Created user with id:', get_user_by_username(nf_un).id
    return create_user_id_response(get_user_by_username(nf_un).id)
  # Case 3: User doesn't exist, and has invalid credentials
  else:
    return create_user_id_response(ERROR)

@app.route('/create-chill-request', methods=['POST'])
def create_chill_request():
  ERROR = -1
  request_data = json.loads(flask.request.data)
  user_id = request_data['uid']
  genre = request_data['genre']
  program_type = request_data['type']
  date = process_date_from_string(request_data['day'])
  time = request_data['time']
  try:
    latitude = float(request_data['latitude'])
    longitude = float(request_data['longitude'])
  except ValueError:
    'Coordinates are invalid. Please enter in floating point form: 1.234'
    return create_chill_id_response(ERROR)

  response = add_chill_request(user_id, genre, program_type, date, time, latitude, longitude)
  return create_chill_id_response(response)

@app.route('/verify-user-exists', methods=['POST'])
def verify_id_exists():
  user_id = int(json.loads(flask.request.data)['uid'])
  print 'User exists:', user_id_exists(user_id)
  return create_verify_user_response(user_id_exists(user_id))

@app.route('/get-chill-matches', methods=['POST'])
def get_chill_matches():
  result = {}
  str_user_id = json.loads(flask.request.data)['uid']
  try:
    int_user_id = int(str_user_id)
  except ValueError:
    return 'Invalid user ID.'
  if not user_id_exists(int_user_id):
    return 'User ID not found.'
  for chill_request in get_chill_requests_by_user_id(int_user_id):
    result[str(chill_request.id)] = {}
    result[str(chill_request.id)] = get_chill_request_dict(chill_request)
    result[str(chill_request.id)]['priority'] = 1 # TODO: Assign priority based on chronological ordering.
    result[str(chill_request.id)]['matches'] = get_chill_request_matches(chill_request)
  return create_chill_matches_response(result)

def create_user_id_response(user_id):
  return jsonify(**{'user_id': user_id})

def create_chill_id_response(chill_id):
  return jsonify(**{'chill_request_id': chill_id})

def create_verify_user_response(user_exists):
  return jsonify(**{'user_exists': user_exists})

def create_chill_matches_response(chill_matches):
  return jsonify(**chill_matches)

# MISCELLANEOUS

def index_to_dow(index):
  days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
  return days[index]

def dow_to_index(dow):
  days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
  return days.index(dow)

# BEGIN SETUP CODE

if __name__ == "__main__":
  app.run()

  #app.run()