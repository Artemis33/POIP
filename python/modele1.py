import pyomo.environ as pe 
import pyomo.opt as po
from pyomo.core import quicksum
from Resolution import Resolution

class SlottingMIP1(Resolution):
    def solve(self):
        instance = self.instance

        product_circuit = instance.product_circuit
        rack_capacity = instance.rack_capacity
        aisles_racks = instance.aisles_racks
        aeration_rate = float(instance.metadata.get("aeration_rate", 0.0))
        num_products = int(instance.metadata.get("num_products", \
                                                 len(product_circuit)))
		R = len(aisles_racks)
		m = len(product_circuit)
		
		M1 = pe.ConcreteModel(name="MIP1")

		# Variables 
		M1.x = pe.Var(range(num_products), range(R), name="x", bounds=(0,1), domain=pe.Binary) # x_kr
		M1.y = pe.Var(range(m), range(R), name="y", bounds=(0,1), domain=pe.Binary) # y_fr 
		M1.a = pe.Var(range(m), range(R), name="a", bounds=(0,1), domain=pe.Binary) # a_fr 
		M1.b = pe.Var(range(m), range(R), name="b", bounds=(0,1), domain=pe.Binary) # b_fr 
		# M1.z 




