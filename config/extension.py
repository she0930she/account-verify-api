from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from os import environ

# init flask app
app = Flask(__name__)

# init ORM
db = SQLAlchemy()

# encrypt password & add salt
bcrypt = Bcrypt(app)


# database config
app.config['SQLALCHEMY_DATABASE_URI'] = environ.get('DB_URL')
db.init_app(app)

with app.app_context():
    db.create_all()