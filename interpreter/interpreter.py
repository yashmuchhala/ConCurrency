PUSH = "PUSH"
ADD = "ADD"
SUB = "SUB"
MUL = "MUL"
DIV = "DIV"
JMP = "JMP"
GRT = "GRT"
LST = "LST"
EQL = "EQL"
END = "END"


class Interpreter:
    def __init__(self, code):
        self.code = code
        self.stack = []
        self.prog_ctr = 0

    def eval(self):
        def push(val):
            self.stack.append(val)

        def pop():
            return self.stack.pop(len(self.stack) - 1)

        while self.prog_ctr < len(self.code):
            opcode = self.code[self.prog_ctr]
            if opcode == PUSH:
                self.prog_ctr += 1
                operand = self.code[self.prog_ctr]
                push(operand)
            elif opcode == ADD:
                op1 = pop()
                op2 = pop()
                push(op1 + op2)
            elif opcode == SUB:
                op1 = pop()
                op2 = pop()
                push(op1 - op2)
            elif opcode == MUL:
                op1 = pop()
                op2 = pop()
                push(op1 * op2)
            elif opcode == DIV:
                op1 = pop()
                op2 = pop()
                push(op1 / op2)
            elif opcode == END:
                break
            self.prog_ctr += 1

        assert len(self.stack) == 1
        return self.stack[0]


if __name__ == '__main__':
    int = Interpreter([PUSH, 1, PUSH, 2, SUB, END])
    print(int.eval())
