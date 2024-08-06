from datetime import datetime, timedelta
from models.model import LoginAttempt

# Constants
WAIT_PERIOD = 1
def count_failed_attempt(exist_user) -> int:
    one_minute_ago = datetime.utcnow() - timedelta(minutes=WAIT_PERIOD)
    recent_attempts = LoginAttempt.query.filter_by(username=exist_user.username).filter(
        LoginAttempt.timestamp >= one_minute_ago).all()
    failed_attempts = [attempt for attempt in recent_attempts if not attempt.success_login]

    return len(failed_attempts)