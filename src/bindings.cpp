// bindings.cpp
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include "mylib.cpp"  // inclut le fichier cpp qui contient la logique
#include <pybind11/numpy.h>

namespace py = pybind11;

PYBIND11_MODULE(mylib, m) {
    m.doc() = "Example C++ library for Python";

    m.def("greet", &greet, "Greet someone by name");
    m.def("add", &add, py::arg("a"), py::arg("b"));
    m.def("print_numpy_array", &print_numpy_array, "Print numpy array contents");
}


/*
Compilation avec la commande suivante:

(BigEnv) seb@MacBook-Air-de-Seb POIP % c++ -O3 -Wall -shared -std=c++17 -fPIC \
    src/bindings.cpp \
    -o lib/mylib.so \
    $(python -m pybind11 --includes) \
    -undefined dynamic_lookup

*/