"""
This module contains user wrapper that stores registration data
for authenticate users in the console interface
"""


class UserWrapper:
    def __init__(self, nick, password):
        self.nick = nick
        self.password = password
        self.online = False

    def change_online_status(self):
        self.online = not self.online
