import sys
sys.path.append("..")

from opcode import _nb_ops
from types import CodeType, FrameType
import dis
from dis import Instruction
import unittest
from utils import *

import logging



class Frame:
    def __init__(self, cobj: CodeType) -> None:
        self.locals = [None] * cobj.co_nlocals
        self.stack = []
        self.return_flag = False
        self.cobj = cobj
        self.instrustions = list(dis.get_instructions(cobj))
        self.PC = 0

    def exec(self):
        stack = self.stack
        locals = self.locals
        cobj = self.cobj

        inspect_code_object(cobj, print_dis=True)

        

        while True:
            #fetch 
            assert (self.PC < len(self.instrustions))
            instruction = self.instrustions[self.PC]
            self.PC += 1

            #decode
            instruction_impl = "_impl_" + instruction.opname
            if hasattr(self, instruction_impl):
                #execute
                getattr(self, instruction_impl)(instruction)
            else:
                logging.warning("Unknown instruction: {}".format(instruction))

            if self.return_flag:
                break

    def _impl_BINARY_OP(self, instruction : Instruction):
        stack = self.stack

        # 0: add, 1: ...，或者用instruction.argrepr也一样
        _, op_kind = _nb_ops[instruction.arg]


        
        match op_kind:
            case "+":
                assert (len(stack) >= 2)
                stack.append(stack.pop() + stack.pop())

            case _:
                logging.warning("Unknown binary op : {}", op_kind)
        
        logging.debug("BINARY_OP : {}, result = {}".format(op_kind, stack[-1]))

    """
    加载/ 写入指令
    """

    def _impl_LOAD_CONST(self, instruction: Instruction):
        index = instruction.arg
        argval = self.cobj.co_consts[index]
        self.stack.append(argval)

        logging.debug(f"LOAD_CONST : {argval}")


    def _impl_LOAD_FAST(self, instruction : Instruction):
        index = instruction.arg
        self.stack.append(self.locals[index])

        #for debug
        name = self.cobj.co_varnames[index]
        logging.debug(f"LOAD_NAME {index}({name})")

    def _impl_STORE_FAST(self, instruction : Instruction):
        assert (len(self.stack) >= 1)
        index = instruction.arg

        print(self.locals, index)
        self.locals[index] = self.stack.pop()
        
        #for debug
        name = self.cobj.co_varnames[index]
        logging.debug(f"STORE_NAME : {name}")


    """
    比较/跳转指令
    """

    def _impl_COMPARE_OP(self, instruction: Instruction):
        comparers = {
            '<': lambda x, y: x < y,
            '<=': lambda x, y: x <= y,
            '==': lambda x, y: x == y,
            '!=': lambda x, y: x != y,
            '>': lambda x, y: x > y,
            '>=': lambda x, y: x >= y,
            'in': lambda x, y: x in y,
            'not in': lambda x, y: x not in y,
            'is': lambda x, y: x is y,
            'is not': lambda x, y: x is not y,
        }
        opname = dis.cmp_op[instruction.arg]
        comparer = comparers[opname]
        rhs = self.stack.pop()
        lhs = self.stack.pop()
        result = comparer(lhs, rhs)
        self.stack.append(result)


    def _impl_POP_JUMP_FORWARD_IF_FALSE(self, instruction : Instruction):
        stack = self.stack
        flag = stack.pop()
        if False == flag:
            self.PC += instruction.arg
            logging.debug("POP_JUMP_FORWARD_IF_FALSE : {}, PC = {}".format(flag, self.PC))
        else:
            logging.debug(
                "POP_JUMP_FORWARD_IF_FALSE : {}, PC = {}".format(flag, self.PC))


    def _impl_RETURN_VALUE(self, instruction : Instruction):
        self.return_value = self.stack.pop()
        self.return_flag = True
        logging.debug(
            "RETURN_VALUE : {}".format(self.return_value))


    """
    不重要的指令
    """

    def _impl_RESUME(self, instruction : Instruction):
        logging.debug("RESUME, do not care")



####
# Test
####

def rich_poor():
    deposit = 1e4
    if deposit >= 1e5:
        kind_1 = "rich"
    else:
        kind_1 = "poor"

    deposit = 1e6
    if deposit >= 1e5:
        kind_2 = "rich"
    else:
        kind_2 = "poor"


def loop():
    sum = 0
    for i in range(10):
        sum += i
    

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


    def test_if(self):
        cobj = rich_poor.__code__
        
        frame = Frame(cobj)
        frame.exec()
        print(frame.locals)

        #locals[0] is deposit
        #locals[1] is kind_1
        #locals[2] is kind_2
        self.assertEqual(frame.locals[1], 'poor') 
        self.assertEqual(frame.locals[2], 'rich')


if __name__ == "__main__":
    unittest.main()