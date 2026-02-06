#pragma once

#include <vector>
#include <string>
#include <iostream>
#include <map>

using namespace std;

// Représentation C++ d'une instance d'entrepôt, alignée sur la version Python.
class WarehouseInstance {
public:
	vector<vector<int>> adjacency;        // matrice n x n
	vector<int> rack_capacity;                 // capacité par rack
	vector<int> product_circuit;               // circuit par produit
	vector<vector<int>> aisles_racks;     // racks par allée
	vector<vector<int>> orders;           // commandes (produits)
	map<string, double> metadata;         // méta-données

	WarehouseInstance(
		const vector<vector<int>>& adjacency,
		const vector<int>& rack_capacity,
		const vector<int>& product_circuit,
		const vector<vector<int>>& aisles_racks,
		const vector<vector<int>>& orders,
		const map<string, double>& metadata
	);

	// Affichage synthétique de l'instance (console)
	void affichage() const;
};


