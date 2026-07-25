import py_compile
import sys
try:
    py_compile.compile('main.py', doraise=True)
    print('py_compile: OK')
except Exception as e:
    print('py_compile: FAILED')
    print(e)
    sys.exit(2)
