from setuptools import setup
from Cython.Build import cythonize

# Can be used if Cython Compilation instead of CPython of PyPy3 is used

setup(
    ext_modules=cythonize(["chess_engine.py"]),
)

