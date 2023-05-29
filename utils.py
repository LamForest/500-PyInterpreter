from types import CodeType
import dis


def inspect_code_object(cobj: CodeType, print_dis=False):
    print("\n\n=========== inspect code objects ===========")
    print('co_names:', cobj.co_names)
    print('co_consts:', cobj.co_consts)
    print('co_stacksize:', cobj.co_stacksize)
    print('co_code', cobj.co_code)
    print('co_varnames', cobj.co_varnames)
    print('co_nlocals', cobj.co_nlocals)
    print('co_argcount', cobj.co_argcount)
    print('co_kwonlyargcount', cobj.co_kwonlyargcount)
    
    print("\n=========== Instructions ===========")
    if print_dis:
        print("\nInstructions:")
        dis.dis(cobj)
    print("=========== inspect code objects ===========\n\n")
