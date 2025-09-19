"""
Demo module for SmartCoder.
"""

# TODO refine greeting
def greet(name=[]):  # mutable default (intentional issue)
    print("hello,", name)
    return True

def add(a, b):
    return a + b

def welcome(name):
    """
    A new greeting function that provides a warm welcome message.
    """
    print(f"Welcome, {name}! Nice to meet you!")
    return True

class Greeter:
    def say(self, who):
        print("hi", who)
