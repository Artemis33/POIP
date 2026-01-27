"""Solution Class"""
from WarehouseLoader import *
import random

class WarehouseSolution:
	"""
	Represent a warehouse slotting solution.

	Attributes
	----------
	_instance : str
		Name of the solved instance.
	_algorithm : str
		Name of the algorithm used to solve the instance.
	_id : str
		Identifier of the solution.

	_value : int 
		Number of products.
	_nb_product : int
		Total cost of the solution.
	_positions : list[int]
		Rack position for each product.

	Methods
	-------
	__init__(self, name_instance: str, name_algorithm: str)
		Initialize the solution with instance name and algorithm.
	save_solution(self)
		Save the solution to a file.
	read_solution(self, instance: str, algo: str, id: str)
		Read a solution from the provided file {instance}_{algo}_{id}.sol.
	__str__(self)
		Return a human-readable representation of the solution.
	"""

	
	def __init__(self, name_instance: str, name_algorithm: str) -> None:
		"""
		Initializes the WarehouseSolution with the provided instance name \
			and algorithm name.

		Parameters
		----------
		name_instance : str
			Name of the instance
		name_algorithm : str
			Name of the algorithm
		"""
		self._instance = name_instance
		self._algorithm = name_algorithm
		self._id = f"{random.randint(0, 999):03d}"
		
		self._value = -1
		self._nb_product = -1
		self._positions = []

	def save_solution(self) -> None:
		"""
		Save the solution in a file named {instance}_{algorithm}_{id}.sol
		"""
		file_name = f"../solutions/{self._instance}_{self._algorithm}_"+\
					f"{self._id}.sol"
		if self._positions:
			n = len(self._positions)
			with open(file_name, 'w') as file:
				file.write(str(n) + '\n')
				for product in self._positions:
					file.write(str(product) + '\n')
		else: print("No solution provided"); return None
	
	def read_solution(self, instance: str, algo: str, id: str) -> None:
		"""
		Read a solution from a file named {instance}_{algo}_{id}.sol
		
		Parameters
		----------
		instance : str
			Name of the instance
		algo : str
			Name of the algorithm
		id : str
			Identifier of the solution file
		"""
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

	def __str__(self) -> str:
		"""
		String representation of the solution
		"""
		csv = ''
		csv += f"Instance's name: {self._instance}\t" + \
				f"Number of products: {self._nb_product}\n" 
		for i in range(len(self._positions)):
			csv += f"product #{i+1}\t" + \
					f"in rack #{int(self._positions[i])+1} \n"
		return (csv)