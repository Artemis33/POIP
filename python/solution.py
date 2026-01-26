"""Classe Solution"""
from warehouse_loader import *

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
	__init__(self, name)
		Initializes the ParallelSchedulingSolution with the provided name.
	save_solution(self, file_name)
		Saves the solution in the provided file with the name file_name
	read_solution(self, file_name)
		Reads a solution in the provided file with the name file_name
	__str__(self)
		Displays the solution
	"""
	
	def __init__(self, name):
		self._name = name
		self._value = 0
		self._positions = []

	def save_solution(self, file_name):
		if self is None:
			print("No solution provided")
			return None
		else:
			n = len(self._positions)
			with open(file_name, 'w') as file:
				file.write(str(n) + '\n')
				for product in self._positions:
					file.write(str(product) + '\n')
	
	def read_solution(self, file_name):
		try:
			with open(file_name, 'r') as file:
				line = file.readline()
				self._value = int(line)
				while(line!=""):
					line = file.readline()
					if line:
						product = line.strip()
						self._positions.append(product)

		except Exception as e:
			print(f"An error occurred while reading the file: {e}")

	def __str__(self):
		csv = ''
		csv += f"Instance's name: {self._name}\t" + f"Number of products: {self._value}\n" 
		for i in range(len(self._positions)):
			csv += f"product #{i+1}\t" + f"in rack #{int(self._positions[i])+1} \n"
		return (csv)