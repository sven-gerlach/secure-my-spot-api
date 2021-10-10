"""
This module includes custom error classes
"""


class ValidationError(Exception):
    def __init__(self, msg):
        self.msg = msg
