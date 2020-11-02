import jsonpickle
from config import *

class Account:
    def __init__(self, vk=None, bal=INITIAL_BALANCE):
        self.vk = vk
        self.bal = bal

    def __str__(self):
        return jsonpickle.encode(self, indent=4)

    def deposit(self, val):
        self.bal += val

    def withdraw(self, val):
        if val <= self.bal:
            self.bal -= val
            return True
        return False
