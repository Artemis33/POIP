#include <string>
#include <pybind11/numpy.h>
#include <iostream>

void print_numpy_array(pybind11::array_t<double> arr) {
    auto buf = arr.request();
    double* ptr = (double*) buf.ptr;
    for (ssize_t i = 0; i < buf.size; i++) {
        std::cout << ptr[i] << " ";
    }
    std::cout << "\n";
}

std::string greet(const std::string& name) {
    return "Hello, " + name + "!";
}

int add(int a, int b) {
    return a + b;
}