from flask import Flask, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
from os import environ
from password_strength import PasswordPolicy
from flask_bcrypt import Bcrypt
from datetime import datetime, timedelta



app = Flask(__name__)


# database config
app.config['SQLALCHEMY_DATABASE_URI'] = environ.get('DB_URL')
db = SQLAlchemy(app)

# encrypt password & add salt
bcrypt = Bcrypt(app)

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


with app.app_context():
  db.create_all()


def is_username_valid(username: str) -> list:
  MIN_LEN = 3
  MAX_LEN = 32
  ans = []
  if username is None:
    ans.append(False)
    ans.append("username is None")
    return ans

  if len(username) < MIN_LEN or len(username) > MAX_LEN:
    ans.append(False)
    ans.append("username must have a minimum length of 3 characters and a maximum length of 32 characters")
    return ans
  exist_user = User.query. \
    filter_by(username=username).first()
  if exist_user:
    ans.append(False)
    ans.append("The username already exist. please choose a different one.")
    return ans
  ans.append(True)
  ans.append("success")
  return ans


def is_password_valid(password: str) -> list:
  MIN_LEN = 8
  MAX_LEN = 32
  policy = PasswordPolicy.from_names(
    length=MIN_LEN,  # min length: 8
    uppercase=1,  # need min. 1 uppercase letters
    numbers=1,  # need min. 1 digits
  )
  policy_violations = policy.test(password)
  ans = []
  if password is None:
    ans.append(False)
    ans.append("password is None")
    return ans

  if policy_violations:
    ans.append(False)
    alert = "you must apply the below password policy: "
    for rule in policy_violations:
      alert += str(rule)
    ans.append(alert)
    return ans

  # Check maximum length
  if len(password) > MAX_LEN:
    ans.append(False)
    alert = f"Password exceeds maximum length of {MAX_LEN} characters."
    ans.append(alert)
    return ans

  lowercase = ['a', 'b', 'c', 'd', 'e', 'f', 'g',
               'h', 'i', 'j', 'k', 'l', 'm', 'n',
               'o', 'p', 'q', 'r', 's', 't',
               'u', 'v', 'w', 'x', 'y', 'z']
  for char in password:
    if char in lowercase:
      ans.append(True)
      alert = "Password is valid."
      ans.append(alert)
      return ans

  ans.append(False)
  alert = "Password needs at least one lowercase letter."
  ans.append(alert)
  return ans


def commitToDB(obj) -> None:
  db.session.add(obj)
  db.session.commit()

def createNewUser(username: str, password: str) -> User:
  pw_hash = bcrypt.generate_password_hash(password).decode('utf-8')

  new_user = User(
    username=username,
    password=pw_hash
  )
  commitToDB(new_user)
  return new_user


def count_failed_attempt():
    pass


#create a test route
@app.route('/testhealth', methods=['GET'])
def test():
  return make_response(jsonify({'message': 'test route'}), 200)


# create a user
@app.route('/createuser', methods=['POST'])
def register():
    '''
    create an account contains username and password
    :return:
    '''
    try:
        data = request.get_json()
        if data is None:
            return make_response(jsonify({"reason": "Invalid JSON or wrong Content-Type"}, {'success': False}), 400)

        # check incorrect key in payload
        if ('username' or 'password') not in data:
            return make_response(jsonify({"reason": "Missing 'username' key or Missing 'password' key in JSON data"}, {'success': False}), 400)

        username = data['username']
        password = data['password']
        is_valid_username = is_username_valid(username)
        if not is_valid_username[0]:
            return make_response(jsonify({'reason': is_valid_username[1]}, {'success': False}), 400)

        is_valid_password = is_password_valid(password)
        if is_valid_password[0] is False:
          return make_response(jsonify({'reason': is_valid_password[1]}, {'success': False}), 400)

        new_user = createNewUser(username=data['username'], password=data['password'])

        return make_response(
            jsonify(
              {'message': 'user created'},
              {'success': True},
              {"username": new_user.username,
               "password": new_user.password,
                "account_created": new_user.account_created}), 201)
    except:
        return make_response(jsonify({'error': 'error during create-user'}), 500)


@ app.route('/v1/login', methods=['GET','POST'])
def login_user():
    '''
    verify an account for username and password
    :return:
    '''
    try:
        # TODO: if payload model is wrong?
        data = request.get_json()
        if data is None:
          return make_response(jsonify({"reason": "Invalid JSON or wrong Content-Type"},
                         {'success': False}), 400)

        # check incorrect key in payload
        if ('username' or 'password') not in data:
          return make_response(jsonify({"reason": "Missing 'username' key or Missing 'password' key in JSON data"},
                         {'success': False}), 400)

        username = data['username']
        password = data['password']

        exist_user = User.query.filter_by(username=username).first()
        if not exist_user:
            return make_response(jsonify({'reason': 'Invalid username'}, {'success': False}), 401)

        # Check recent failed attempts
        one_minute_ago = datetime.utcnow() - timedelta(minutes=1)
        recent_attempts = LoginAttempt.query.filter_by(username=exist_user.username).filter(
            LoginAttempt.timestamp >= one_minute_ago).all()
        failed_attempts = [attempt for attempt in recent_attempts if not attempt.success_login]

        if len(failed_attempts) >= 5:
            return make_response(jsonify({'reason':
                'Too many failed login attempts. '
                'Please wait a minute before trying again.'},
                {'success': False}), 429)

        # verify password
        is_password_correct = bcrypt.check_password_hash(exist_user.password, password)
        if not is_password_correct:
          new_attempt = LoginAttempt(username=exist_user.username, success_login=False)
          commitToDB(new_attempt)
          return make_response(jsonify({'reason': 'Invalid password'}, {'success': False}), 401)

        new_attempt = LoginAttempt(username=exist_user.username, success_login=True)
        commitToDB(new_attempt)
        return make_response(jsonify({'reason': 'Login successful'}, {'success': True}), 200)
    except:
        return make_response(jsonify({'error': 'error during user login'}), 500)


# get all users
@app.route('/get/table/users', methods=['GET'])
def get_users():
  '''
  test use,
  for checking all userTable records
  :return:
  '''
  try:
    allUsers = User.query.all()
    output = []
    for user in allUsers:
        userDict = {}
        userDict["username"] = user.username
        userDict["password"] = user.password
        userDict["account_created"] = user.account_created
        output.append(userDict)
    return make_response(jsonify({"all users": output}, {"success": True}), 200)
  except :
    return make_response(jsonify({'message': 'error getting users'}), 500)


@app.route('/get/table/loginAttemptTable', methods=['GET'])
def get_login_attempt_table():
    '''
    test use,
    for checking all loginAttemptTable records
    :return:
    '''
    loginAttempts = LoginAttempt.query.all()
    output = []
    for one_attempt in loginAttempts:
        login_attempt_dict = {}
        login_attempt_dict["username"] = one_attempt.username
        login_attempt_dict["timestamp"] = one_attempt.timestamp
        login_attempt_dict["success_login"] = one_attempt.success_login
        output.append(login_attempt_dict)
    return make_response(jsonify({"all attempts": output}, {"success": True}), 200)




@app.route('/delete/table/userTable', methods=['DELETE'])
def delete_user_table():
    '''
    test use,
    for dropping userTable, and create a new userTable instance
    :return:
    '''
    try:
        with app.app_context():
            User.__table__.drop(db.engine)
            db.create_all()
        return make_response(jsonify({'message': 'User table dropped!'}), 200)
    except:
        return make_response(jsonify({'error': 'error drop user table'}), 500)
    # with app.app_context():
    #     User.__table__.drop(db.engine)
    #     db.create_all()
    # return make_response(jsonify({'message': 'User table dropped!'}), 200)



@app.route('/delete/table/loginAttemptTable', methods=['DELETE'])
def delete_login_attempt_table():
    '''
    test use,
    for dropping loginAttemptTable, and create a new loginAttemptTable instance
    :return:
    '''
    try:
        with app.app_context():
            LoginAttempt.__table__.drop(db.engine)
            db.create_all()
        return make_response(jsonify({'message': 'LoginAttempt table dropped!'}), 200)
    except:
        return make_response(jsonify({'error': 'error drop loginAttempt table'}), 500)
    # with app.app_context():
    #     LoginAttempt.__table__.drop(db.engine)
    #     db.create_all()
    # return make_response(jsonify({'message': 'LoginAttempt table dropped!'}), 200)


@app.route('/get/clean/loginAttemptTable', methods=['GET'])
def clean_unused_loginAttempTable_record():
    '''
    not implementing this
    but could regularly clean history loginAttemptTable records
    :return:
    '''
    pass



