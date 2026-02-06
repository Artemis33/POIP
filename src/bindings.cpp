// bindings.cpp — module Warehouse_cpp exposant WarehouseInstance sous le nom Python "WarehouseLoader"
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include "WarehouseLoader.hpp"

namespace py = pybind11;

PYBIND11_MODULE(Warehouse_cpp, m) {
    m.doc() = "Warehouse C++ bindings exposing WarehouseLoader";

    py::class_<WarehouseInstance>(m, "WarehouseLoader")
        .def(
            py::init<
                const std::vector<std::vector<int>>&,
                const std::vector<int>&,
                const std::vector<int>&,
                const std::vector<std::vector<int>>&,
                const std::vector<std::vector<int>>&,
                const std::map<std::string, double>&
            >(),
            py::arg("adjacency"),
            py::arg("rack_capacity"),
            py::arg("product_circuit"),
            py::arg("aisles_racks"),
            py::arg("orders"),
            py::arg("metadata")
        )
        .def("affichage", &WarehouseInstance::affichage);
        // .def_readwrite("adjacency", &WarehouseInstance::adjacency)
        // .def_readwrite("rack_capacity", &WarehouseInstance::rack_capacity)
        // .def_readwrite("product_circuit", &WarehouseInstance::product_circuit)
        // .def_readwrite("aisles_racks", &WarehouseInstance::aisles_racks)
        // .def_readwrite("orders", &WarehouseInstance::orders)
        // .def_readwrite("metadata", &WarehouseInstance::metadata);
}

/*
Compilation directe du module Warehouse_cpp:

(BigEnv) seb@MacBook-Air-de-Seb POIP % c++ -O3 -Wall -shared -std=c++17 -fPIC \
    src/WarehouseLoader.cpp src/bindings.cpp \
    -o lib/Warehouse_cpp.so \
    $(python -m pybind11 --includes) \
    -undefined dynamic_lookup

*/