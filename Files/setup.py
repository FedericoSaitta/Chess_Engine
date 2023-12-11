from setuptools import setup
from Cython.Build import cythonize

setup(
    ext_modules=cythonize(["chess_engine.py"]),
)

