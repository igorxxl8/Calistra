from random import randint
from datetime import datetime


class User:
    def __init__(self, nick):
        self.uid = _make_uid()
        self.nick = nick


def _make_uid():
    now = datetime.today()
    time_t = datetime.timetuple(now)
    uid = ''.join(
        [
            str(time_t.tm_year),
            str(time_t.tm_mon),
            str(time_t.tm_mday),
            str(time_t.tm_hour),
            str(time_t.tm_min),
            str(time_t.tm_sec),
            str(randint(0, 1000))
        ]
    )
    return int(uid)
