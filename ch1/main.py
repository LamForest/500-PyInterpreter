import sys
sys.path.append("..")

from opcode import _nb_ops
from types import CodeType, FrameType
import dis
import unittest
from utils import *

import logging


#Frame is FrameObject
class Frame:
    def __init__(self, cobj: CodeType) -> None:
        """
        cobj: CodeObject
        """
        self.locals = [None] * cobj.co_nlocals #local 变量
        self.stack = [] #计算栈
        self.return_flag = False #跳出循环的flag，遇到RETURN_VALUE时设为True
        self.cobj = cobj
        self.PC = 0

    def exec(self):
        stack = self.stack
        locals = self.locals
        cobj = self.cobj
        

        inspect_code_object(cobj, print_dis=True)

        instructions = list(dis.get_instructions(cobj))

        while True:

            self.instruction = instructions[self.PC]
            self.PC += 1

            instruction_impl = "_impl_" + self.instruction.opname
            if hasattr(self, instruction_impl):
                getattr(self, instruction_impl)()
            else:
                logging.warning("Unknown instruction: {}".format(self.instruction ))

            if self.return_flag:
                break

    def _impl_BINARY_OP(self):
        stack = self.stack

        # 0: add, 1: ...，或者用instruction.argrepr也一样
        _, op_kind = _nb_ops[self.instruction.arg]


        
        match op_kind:
            case "+":
                assert (len(stack) >= 2)
                stack.append(stack.pop() + stack.pop())

            case _:
                logging.warning("Unknown binary op : {}", op_kind)
        
        logging.debug("BINARY_OP {}, result = {}".format(op_kind, stack[-1]))

    def _impl_LOAD_CONST(self):
        index = self.instruction.arg
        argval = self.cobj.co_consts[index]
        self.stack.append(argval)

        logging.debug(f"LOAD_CONST ({index}): {argval}")

    def _impl_LOAD_FAST(self):
        index = self.instruction.arg
        self.stack.append(self.locals[index])

        #for debug
        name = self.cobj.co_varnames[index]
        logging.debug(f"LOAD_FAST {index} ({name})")


    def _impl_STORE_FAST(self):
        assert (len(self.stack) >= 1)
        index = self.instruction.arg
        self.locals[index] = self.stack.pop()

        #for debug
        name = self.cobj.co_varnames[index]
        logging.debug(f"STORE_FAST {index} ({name})")


    def _impl_RETURN_VALUE(self):
        self.return_value = self.stack.pop()
        self.return_flag = True

    """
    不重要的指令
    """

    def _impl_RESUME(self):
        logging.debug("RESUME, do not care")



def add():
    a = 1
    b = a + 1
    c = a + b + 100

class TestAdd(unittest.TestCase):

    def setUp(self) -> None:
        logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.DEBUG)
        return super().setUp()

    def test_add(self):
        # source_code = "a = 1; b = 2; c = a + b"

        cobj = add.__code__

        frame = Frame(cobj)
        frame.exec()

        self.assertEqual(frame.locals[0], 1)
        self.assertEqual(frame.locals[1], 2)
        self.assertEqual(frame.locals[2], 103)

if __name__ == "__main__":
    a = TestAdd()
    a.test_add()