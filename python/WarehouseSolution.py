"""Classe Solution"""
from WarehouseLoader import *
import random

class WarehouseSolution:
	"""
	A class used to represent the Parallel Scheduling Solution

	Attributes
	----------
	_name : str
		a string that holds the name of the instance solved
	_value : int 
		an integer that holds the value of the solution
	_compoMachine : list[int]
		a list with the position of each product

	Methods
	-------
	__init__(self, name_instance: str, name_algorithm: str)
		Initializes the ParallelSchedulingSolution with the provided name and algorithm.
	save_solution(self)
		Saves the solution
	read_solution(self, file_name)
		Reads a solution in the provided file with the name file_name
	__str__(self)
		Displays the solution
	"""
	
	def __init__(self, name_instance: str, name_algorithm: str):
		self._instance = name_instance
		self._algorithm = name_algorithm
		self._id = f"{random.randint(0, 999):03d}"
		
		self._value = -1
		self._nb_product = -1
		self._positions = []

	def save_solution(self):
		file_name = f"../solutions/{self._instance}_{self._algorithm}_{self._id}.sol"
		if self is None:
			print("No solution provided")
			return None
		else:
			n = len(self._positions)
			with open(file_name, 'w') as file:
				file.write(str(n) + '\n')
				for product in self._positions:
					file.write(str(product) + '\n')
	
	def read_solution(self, instance: str, algo: str, id: str):
		file_name = f"../solutions/{instance}_{algo}_{id}.sol"
		self._positions = []
		try:
			with open(file_name, 'r') as file:
				line = file.readline()
				self._nb_product = int(line)
				for _ in range(self._nb_product):
					rack = file.readline()
					if rack:
						rack = int(rack.strip())
						self._positions.append(rack)
			self._id = id
			self._instance = instance
			self._algorithm = algo

		except Exception as e:
			print(f"An error occurred while reading the file: {e}")

	def __str__(self):
		csv = ''
		csv += f"Instance's name: {self._instance}\t" + f"Number of products: {self._nb_product}\n" 
		for i in range(len(self._positions)):
			csv += f"product #{i+1}\t" + f"in rack #{int(self._positions[i])+1} \n"
		return (csv)