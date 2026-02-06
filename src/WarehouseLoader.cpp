#include"warehouseLoader.hpp"

WarehouseData::WarehouseData(string warehouse_dir):_warehouse_dir(warehouse_dir) {
	ifstream inf(filename);
	if (!inf){
		cerr << "Error opening file " << filename << " -- abort " << endl; 
		abort();
	}
}