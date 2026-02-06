#include "WarehouseLoader.hpp"
#include <numeric>

// using namespace std;

WarehouseInstance::WarehouseInstance(
	const vector<vector<int>>& adjacency,
	const vector<int>& rack_capacity,
	const vector<int>& product_circuit,
	const vector<vector<int>>& aisles_racks,
	const vector<vector<int>>& orders,
	const map<string, double>& metadata
): adjacency(adjacency),
   rack_capacity(rack_capacity),
   product_circuit(product_circuit),
   aisles_racks(aisles_racks),
   orders(orders),
   metadata(metadata) {}

void WarehouseInstance::affichage() const {
	const auto total_capacity = accumulate(rack_capacity.begin(), rack_capacity.end(), 0);
	cout << "WarehouseInstance("
			  << "num_racks=" << rack_capacity.size() << ", "
			  << "capacity=" << total_capacity << ", "
			  << "num_products=" << product_circuit.size() << ", "
			  << "num_orders=" << orders.size() << ")\n";

	if (!metadata.empty()) {
		cout << "Metadata:" << endl;
		for (const auto& kv : metadata) {
			cout << "  - " << kv.first << ": " << kv.second << endl;
		}
	}
}


