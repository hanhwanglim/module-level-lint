

"""This is a file that has no linting errors"""


from __future__ import division


__all__ = ["divide"]


import random
from pprint import pprint


def divide(a, b):
    return a / b


pprint(divide(random.randint(10, 20), random.randint(1, 10)))
