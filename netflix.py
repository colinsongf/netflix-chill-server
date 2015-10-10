import os

from flask import Flask, request
from flask.ext.sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://hbrvgdoavvrkzy:97AbqwFr_7XFVq1paXIOi0Xl_Y@ec2-54-225-201-25.compute-1.amazonaws.com:5432/d92htefnn65sr'

db = SQLAlchemy(app)

class User(db.Model):
  user_id = db.Column(db.Integer, primary_key=True)
  netflix_username = db.Column(db.String(80), unique=True)
  netflix_password = db.Column(db.String(80))

  def __init__(self, nf_un, nf_pw):
    self.netflix_username = nf_un
    self.netflix_password = nf_pw

  def __repr__(self):
      return '<User %r>' % self.username

@app.route('/')
def index():
  return 'Netflix and Chill API'

@app.route('/sign-in', methods=['post'])
def sign_in():
  nf_un = request.args.get('nfun') 
  nf_pw = request.args.get('nfpw'))
  if user_exists(nf_un, nf_pw):
    return get_user_id(fb_credentials[0], nf_credentials[0])
  else:
    # create user
    pass

def user_exists(nf_un, fb_un):
  return (User.query().filter_by(netflix_username=nf_un, facebook_username=fb_un).count() != 0)

def get_user_id(nf_un, fb_un):
  result User.query().filter_by(netflix_username=nf_un, facebook_username=fb_un).add_column('user_id')
  print result

def add_user():
  pass

if __name__ == "__main__":
  app.run()