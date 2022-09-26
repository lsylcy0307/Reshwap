import random
import string
import time

from datetime import datetime
from pytz import timezone

def generate_user_id():
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(8))

fmt = "%Y-%m-%d %H:%M:%S"
def time_now():
    return datetime.now(timezone('US/Eastern')).strftime(fmt)

def generate_random_id():
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10))