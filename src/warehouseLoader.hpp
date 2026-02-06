#include<vector>
#include<string>
#include<iostream>
#include<fstream>

using namespace std;

class WarehouseData {
	public:
		vector<vector<int>> _adjacency;
		vector<int>         _rack_capacity;
		vector<vector<int>> _aisles_racks;
		vector<vector<int>> _orders;
		vector<float>       _metadata;

		WarehouseData(string warehouse_dir);
}
