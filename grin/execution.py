#!/usr/bin/env python3

class ProgramState:
    """
    Keeps track of the program's state
    - token_lines is the program itself in grin tokens
    - ip is where the execution currently is
    - vars stores variables
    - goto_labels is a dictionary that should enable the goto functionality to work.
    - return_stack is list designed like a stack to keep track of return values
    - output stores list of values being printed
    - input_func enables the ability to test INNUM and INSTR
    """
    def __init__(self, token_lines, input_func=input):
        self.token_lines = token_lines
        self.ip = 0
        self.vars = {}
        self.goto_labels = {}
        self.return_stack = []
        self.output = []
        self.input_func = input_func
