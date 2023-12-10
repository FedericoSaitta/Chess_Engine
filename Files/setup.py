from setuptools import setup
from Cython.Build import cythonize

setup(
    ext_modules=cythonize(["chess_main.py", "chess_engine.py", "perft_test.py"]),
)