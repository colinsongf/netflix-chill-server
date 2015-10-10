import os

from flask import Flask, request
from flask.ext.sqlalchemy import SQLAlchemy

DB_URI = 'postgres://hbrvgdoavvrkzy:97AbqwFr_7XFVq1paXIOi0Xl_Y@ec2-54-225-201-25.compute-1.amazonaws.com:5432/d92htefnn65sr'

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = DB_URI

db = SQLAlchemy(app)

@app.route('/')
def index():
  return 'Netflix and Chill API'

@app.route('/sign-in', methods=['post'])
def sign_in():
  fb_username = request.args.get('fbun')
  fb_password = request.args.get('fbpw')
  nf_username = request.args.get('nfun')
  nf_password = request.args.get('nfpw')

if __name__ == "__main__":
  app.run()