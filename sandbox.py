from RestrictedPython import safe_builtins, compile_restricted
import multiprocessing

_SAFE_MODULES = frozenset(("math"))


def _safe_import(name, *args, **kwargs):
    if name not in _SAFE_MODULES:
        raise Exception(f"Don't you even think about {name!r}")
    return __import__(name, *args, **kwargs)


def execute_user_code(user_code, user_func, *args, **kwargs):
    my_globals = {
        "__builtins__": {
            **safe_builtins,
            "__import__": _safe_import,
        },
    }

    try:
        byte_code = compile_restricted(
            user_code, filename="<user_code>", mode="exec")
    except SyntaxError:
        raise

    try:
        exec(byte_code, my_globals)
        return my_globals[user_func](*args, **kwargs)
    except BaseException:
        raise

user_code = """
# from tms_data_interface import SQLQueryInterface

def return_num(n: int):
    # seq = SQLQueryInterface()
    return n
"""

print(execute_user_code(user_code, "return_num", 45))

if __name__ == '__main__':
    p = multiprocessing.Process(target=execute_user_code, args=(user_code, "return_num", 2))
    p.start()

    p.join(10)

    if p.is_alive():
        print("Time limit exceeded!")

        p.terminate()

        p.join()