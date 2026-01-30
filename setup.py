from setuptools import setup, Extension
from pybind11.setup_helpers import Pybind11Extension, build_ext

ext_modules = [
    Pybind11Extension(
        "mylib",                          # nom du module
        ["src/mylib.cpp", "src/bindings.cpp"],  # fichiers sources
        extra_compile_args=["-O3"],       # optimisation
    ),
]

setup(
    name="mylib",
    ext_modules=ext_modules,
    cmdclass={"build_ext": build_ext},
)
