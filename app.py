from config.extension import db
from flask import request, jsonify, make_response
from helpers.account_helper import is_password_valid, is_username_valid, createNewUser, commitToDB
from models.model import User, LoginAttempt
import traceback
from helpers.login_helper import count_failed_attempt
from config.extension import app, bcrypt


# constants
MAX_FAILED_COUNT = 5
USERNAME = "username"
PASSWORD = "password"


#create a test route
@app.route("/testhealth", methods=["GET"])
def test():
    '''
    test endpoint health state
    :return:
    '''
    return make_response(jsonify({'message': 'test route'}, {"success": True}), 200)


# create a user
@app.route("/createuser", methods=["POST"])
def register():
    '''
    create an account contains username and password
    :return:
    '''
    try:
        data = request.get_json()
        if data is None:
            return make_response(jsonify(
                {"reason": "Invalid JSON or wrong Content-Type"},
                {"success": False}), 400)

        # check incorrect key in payload
        if (USERNAME or PASSWORD) not in data:
            return make_response(jsonify(
                {"reason": "Missing 'username' key or Missing 'password' key in JSON data"},
                {"success": False}), 400)

        username = data[USERNAME]
        password = data[PASSWORD]
        is_valid_username = is_username_valid(username)
        if not is_valid_username[0]:
            return make_response(jsonify({"reason": is_valid_username[1]}, {"success": False}), 400)

        is_valid_password = is_password_valid(password)
        if not is_valid_password[0]:
          return make_response(jsonify({"reason": is_valid_password[1]}, {"success": False}), 400)

        new_user = createNewUser(username=data[USERNAME], password=data[PASSWORD])

        return make_response(
            jsonify(
              {"message": "user created"},
              {"success": True},
              {"username": new_user.username,
               "password": new_user.password,
               "account_created": new_user.account_created}), 201)
    except:
        return make_response(jsonify(
            {"error": "error during create-user"},
            {"error": traceback.format_exc()}), 500)


@ app.route("/v1/login", methods=["GET","POST"])
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
                         {"success": False}), 400)

        # check incorrect key in payload
        if (USERNAME or PASSWORD) not in data:
          return make_response(jsonify(
                {"reason": "Missing 'username' key or Missing 'password' key in JSON data"},
                {"success": False}), 400)

        username = data[USERNAME]
        password = data[PASSWORD]

        # check username in db
        exist_user = User.query.filter_by(username=username).first()
        if not exist_user:
            return make_response(jsonify(
                {"reason": "no such username"}, {"success": False}), 401)

        # Check recent failed attempts
        number_failed_attempt = count_failed_attempt(exist_user)
        if number_failed_attempt >= MAX_FAILED_COUNT:
            return make_response(jsonify(
                {
                "reason": "Too many failed login attempts. "
                        "Please wait a minute before trying again."},
                {"success": False}), 429)

        # verify password
        is_password_correct = bcrypt.check_password_hash(exist_user.password, password)
        if not is_password_correct:
            # write in db for login failed state
            new_attempt = LoginAttempt(username=exist_user.username, success_login=False)
            commitToDB(new_attempt)
            return make_response(jsonify({"reason": "Invalid password"}, {"success": False}), 401)

        new_attempt = LoginAttempt(username=exist_user.username, success_login=True)
        commitToDB(new_attempt)
        return make_response(jsonify({"reason": "Login successful"}, {"success": True}), 200)
    except:
        return make_response(jsonify(
            {"error": "error during user login"},
            {"error": traceback.format_exc()}), 500)


# get all users
@app.route("/get/table/users", methods=["GET"])
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
            user_dict = {}
            user_dict[USERNAME] = user.username
            user_dict[PASSWORD] = user.password
            user_dict["account_created"] = user.account_created
            output.append(user_dict)
        return make_response(jsonify({"all users": output}, {"success": True}), 200)
    except :
        return make_response(jsonify(
            {"message": "error getting users"},
            {"error": traceback.format_exc()}), 500)


@app.route("/get/table/loginAttemptTable", methods=["GET"])
def get_login_attempt_table():
    '''
    test use,
    for checking all loginAttemptTable records
    :return:
    '''
    try:
        loginAttempts = LoginAttempt.query.all()
        output = []
        for one_attempt in loginAttempts:
            login_attempt_dict = {}
            login_attempt_dict[USERNAME] = one_attempt.username
            login_attempt_dict["timestamp"] = one_attempt.timestamp
            login_attempt_dict["success_login"] = one_attempt.success_login
            output.append(login_attempt_dict)
        return make_response(jsonify({"all attempts": output}, {"success": True}), 200)
    except:
        return make_response(jsonify(
            {"message": "error getting all loginAttemptTable"},
            {"error": traceback.format_exc()}), 500)



@app.route("/delete/table/userTable", methods=["DELETE"])
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
        return make_response(jsonify({"message": "User table dropped!"}), 200)
    except:
        return make_response(jsonify(
            {"error": "error drop user table"},
            {"error": traceback.format_exc()}), 500)




@app.route("/delete/table/loginAttemptTable", methods=["DELETE"])
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
        return make_response(jsonify({"message": "LoginAttempt table dropped!"}), 200)
    except:
        return make_response(jsonify(
            {"error": "error drop loginAttempt table"},
            {"error": traceback.format_exc()}), 500)



@app.route("/get/clean/loginAttemptTable", methods=["GET"])
def clean_unused_loginAttempTable_record():
    '''
    TODO: Optional. Not required.
    Could regularly clean history loginAttemptTable records.
    :return:
    '''
    pass



