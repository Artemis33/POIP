from setuptools import setup
from pybind11.setup_helpers import Pybind11Extension, build_ext

# Extension pour le module Warehouse_cpp (bindings sur WarehouseInstance)
ext_modules = [
    Pybind11Extension(
        "Warehouse_cpp",
        ["src/WarehouseLoader.cpp", "src/bindings.cpp"],
        extra_compile_args=["-O3", "-std=c++17"],
    ),
]

setup(
    name="Warehouse_cpp",
    version="0.1.0",
    ext_modules=ext_modules,
    cmdclass={"build_ext": build_ext},
)
