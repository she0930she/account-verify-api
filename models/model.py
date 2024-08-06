from config.extension import db
from datetime import datetime

class User(db.Model):
  __tablename__ = 'userTable'

  id = db.Column(db.Integer, primary_key=True)
  username = db.Column(db.String(32), unique=True, nullable=False)
  password = db.Column(db.String(120), nullable=False)
  account_created = db.Column(db.DateTime, default=datetime.utcnow)

  def json(self):
      return {
        'id': self.id,
        'username': self.username,
        'password': self.password,
        'account_created': self.account_created}

class LoginAttempt(db.Model):
  __tablename__ = 'loginAttemptTable'

  id = db.Column(db.Integer, primary_key=True)
  username = db.Column(db.String(32), nullable=False)
  timestamp = db.Column(db.DateTime, default=datetime.utcnow)
  success_login = db.Column(db.Boolean, default=False)

  def json(self):
      return {
        'id': self.id,
        'username': self.username,
        'timestamp': self.timestamp,
        'success_login': self.success_login}
