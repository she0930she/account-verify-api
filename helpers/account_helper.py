from password_strength import PasswordPolicy
from models.model import User
from config.extension import db
from config.extension import bcrypt
import re


# Constants
USERNAME_MIN_LEN = 3
USERNAME_MAX_LEN = 32
PASSWORD_MIN_LEN = 8
PASSWORD_MAX_LEN = 32
UPPERCASE_MIN_COUNT = 1
NUMBER_MIN_COUNT = 1
REGEX_PATTERN = r'^[a-zA-Z!@#$%^&*()_+={}\[\]:;"\'<>,.?\/\\|-]+$'


def is_username_valid(username: str) -> list:
    ans = []
    if username is None:
        ans.append(False)
        ans.append("username is None")
        return ans

    if (len(username) < USERNAME_MIN_LEN) or (len(username) > USERNAME_MAX_LEN):
        ans.append(False)
        ans.append("username must have a minimum length of 3 characters and a maximum length of 32 characters")
        return ans

    exist_user = User.query. \
        filter_by(username=username).first()
    if exist_user:
        ans.append(False)
        ans.append("The username already exist. please choose a different one.")
        return ans

    is_match_regex = re.fullmatch(REGEX_PATTERN, username)
    if not is_match_regex:
        ans.append(False)
        ans.append("The username needs to be english letters, uppercase, lowercase or special characters."
                   " Please correct username input.")
        return ans
    ans.append(True)
    ans.append("success")
    return ans

def is_password_valid(password: str) -> list:
    policy = PasswordPolicy.from_names(
        length=PASSWORD_MIN_LEN,  # min length: 8
        uppercase=UPPERCASE_MIN_COUNT,  # need min. 1 uppercase letters
        numbers=NUMBER_MIN_COUNT,  # need min. 1 digits
    )
    policy_violations = policy.test(password)
    ans = []  # ans contains: [Boolean, string]
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
    if len(password) > PASSWORD_MAX_LEN:
        ans.append(False)
        alert = f"Password exceeds maximum length of {PASSWORD_MAX_LEN} characters."
        ans.append(alert)
        return ans

    # create HashSet
    lowercase = {'a', 'b', 'c', 'd', 'e', 'f', 'g',
               'h', 'i', 'j', 'k', 'l', 'm', 'n',
               'o', 'p', 'q', 'r', 's', 't',
               'u', 'v', 'w', 'x', 'y', 'z'}
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

def createNewUser(username: str, password: str) -> User:
    pw_hash = bcrypt.generate_password_hash(password).decode("utf-8")

    new_user = User(
    username=username,
    password=pw_hash
    )
    commitToDB(new_user)
    return new_user

def commitToDB(obj) -> None:
    db.session.add(obj)
    db.session.commit()