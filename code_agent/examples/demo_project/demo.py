"""
Demo module for SmartCoder.
"""

# TODO refine greeting
def greet(name=[]):  # mutable default (intentional issue)
    print("hello,", name)
    return True

def add(a, b):
    return a + b

class Greeter:
    def say(self, who):
        print("hi", who)
