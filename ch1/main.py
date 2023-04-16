import sys
sys.path.append("..")

from opcode import _nb_ops
from types import CodeType, FrameType
import dis
import unittest
from utils import *

import logging



class Frame:
    def __init__(self, cobj: CodeType) -> None:
        self.locals = {}
        self.stack = []
        self.return_flag = False
        self.cobj = cobj

    def exec(self):
        stack = self.stack
        locals = self.locals
        cobj = self.cobj

        inspect_code_object(cobj, print_dis=True)

        instrustions = dis.get_instructions(cobj)

        for instruction in instrustions:
            self.instruction = instruction
            instruction_handler = "_impl_" + instruction.opname
            if hasattr(self, instruction_handler):
                getattr(self, instruction_handler)()
            else:
                logging.warning("Unknown instruction: {}".format(instruction))

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
        
        logging.debug("BINARY_OP : {}, result = {}".format(op_kind, stack[-1]))

    def _impl_LOAD_CONST(self):
        index = self.instruction.arg
        argval = self.cobj.co_consts[index]
        logging.debug("LOAD_CONST : {}".format(argval))
        self.stack.append(argval)

    def _impl_LOAD_NAME(self):
        index = self.instruction.arg
        name = self.cobj.co_names[index]
        self.stack.append(self.locals[name])

    def _impl_STORE_NAME(self):
        assert (len(self.stack >= 1))
        index = self.instruction.arg
        name = self.cobj.co_names[index]
        self.locals[name] = self.stack.pop()

    """
        不清楚实现的指令
    """

    def _impl_RETURN_VALUE(self):
        print("RETURN_VALUE, 还不知道怎么实现，如何在C语言中返回多个？返回一个tuple? 上一级的frame_obj如何接受，存在哪里？")
        self.return_value = self.stack.pop()
        self.return_flag = True

    """
    不重要的指令
    """

    def _impl_RESUME(self):
        logging.debug("RESUME, do not care")


class TestAdd(unittest.TestCase):

    def setUp(self) -> None:
        logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.DEBUG)
        return super().setUp()

    def test_add(self):
        # source_code = "a = 1; b = 2; c = a + b"
        source_code = "a = 1; b = a + 1; c = a + b + 100"
        cobj = compile(source_code, "<file>", "exec")

        frame = Frame(cobj)
        frame.exec()

        self.assertEqual(frame.locals["a"], 1)
        self.assertEqual(frame.locals["b"], 2)
        self.assertEqual(frame.locals["c"], 103)
