import sys
sys.path.append("..")

from opcode import _nb_ops
from types import CodeType, FrameType, FunctionType
import dis
from dis import Instruction
import unittest
from utils import *

import logging

# class Function:
#     argcount: int  # /* #arguments, except *args */
#     posonly_argcount: int  # /* #positional only arguments */
#     kwonly_argcount: int  # /* #keyword only arguments */
#     nlocals: int  # /* #local variables */
#     stacksize: int # / *  # entries needed for evaluation stack */
#     flags: int  #

def popn(s: list, n):
    assert(len(s) >= n)
    ret = []
    for _ in range(n):
        ret.append(s.pop())
    return tuple(ret)
    

class Frame:
    def __init__(self, cobj: CodeType) -> None:
        self.locals = {}
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
        logging.debug("LOAD_CONST : {}".format(argval))
        self.stack.append(argval)

    def _impl_LOAD_NAME(self, instruction : Instruction):
        index = instruction.arg
        name = self.cobj.co_names[index]
        logging.debug("LOAD_NAME : {}".format(name))
        self.stack.append(self.locals[name])

    def _impl_STORE_NAME(self, instruction : Instruction):
        assert (len(self.stack >= 1))
        index = instruction.arg
        name = self.cobj.co_names[index]
        logging.debug("STORE_NAME : {}".format(name))
        self.locals[name] = self.stack.pop()

    """
    定义函数
    """

    def _impl_MAKE_FUNCTION(self, instruction: Instruction):
        stack = self.stack
        flags = instruction.arg
        match flags:
            case 0x0: 
                cobj = stack.pop()
                fobj = FunctionType(cobj, {})
            case _:
                raise NotImplementedError("这种格式的MAKE_FUNCTION还没有实现")
        
        stack.append(fobj)

    """
    函数调用
    """

    def _impl_PUSH_NULL(self, instruction: Instruction):
        logging.debug("PUSH_NULL ")
        self.stack.append(None)

    def _impl_PRECALL(self, instruction: Instruction):
        logging.debug("PRECALL : #argv = {}".format(instruction.arg))

    def _impl_CALL(self, instruction: Instruction):
        stack = self.stack
        argc = instruction.arg
        argv = popn(stack, argc)
        func = stack.pop()
        self = stack.pop()
        if self == None:
            logging.debug("CALL a function : #argv = {}".format(argc))
            ret = func(*argv)
            stack.append(ret)
        else:
            raise NotImplementedError("call method not 实现")
        



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
        logging.debug(
            "COMPARE_OP : {}, result = {}".format(opname, result))
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



    """
        不清楚实现的指令
    """

    def _impl_RETURN_VALUE(self, instruction : Instruction):
        print("RETURN_VALUE, 还不知道怎么实现，如何在C语言中返回多个？返回一个tuple? 上一级的frame_obj如何接受，存在哪里？")
        self.return_value = self.stack.pop()
        self.return_flag = True
        logging.debug(
            "RETURN_VALUE : {}".format(self.return_value))


    """
    不重要的指令
    """

    def _impl_RESUME(self, instruction : Instruction):
        logging.debug("RESUME, do not care")


class TestAdd(unittest.TestCase):

    def setUp(self) -> None:
        logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.DEBUG)
        return super().setUp()

    @unittest.skip("test")
    def test_add(self):
        # source_code = "a = 1; b = 2; c = a + b"
        source_code = "a = 1; b = a + 1; c = a + b + 100"
        
        cobj = compile(source_code, "<unknown>", "exec")

        frame = Frame(cobj)
        frame.exec()

        self.assertEqual(frame.locals["a"], 1)
        self.assertEqual(frame.locals["b"], 2)
        self.assertEqual(frame.locals["c"], 103)


    @unittest.skip("test")
    def test_if(self):
        with open("if.py") as f:
            source_code = f.read()
        cobj = compile(source_code, "if.py", "exec")
        
        frame = Frame(cobj)
        frame.exec()
        self.assertEqual(frame.locals["kind_1"], 'poor')
        self.assertEqual(frame.locals["kind_2"], 'rich')


    # @unittest.skip("test")
    def test_call(self):
        test_file = "call.py"
        with open(test_file) as f:
            source_code = f.read()
        cobj = compile(source_code, test_file, "exec")

        frame = Frame(cobj)
        frame.exec()
        self.assertEqual(frame.locals["kind_1"], 'poor')
        self.assertEqual(frame.locals["kind_2"], 'rich')


if __name__ == "__main__":
    unittest.main()