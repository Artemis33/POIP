import pyomo.environ as pe 
import pyomo.opt as po
from pyomo.core import quicksum
from Resolution import Resolution

class SlottingMIP1(Resolution):
    def solve(self):
        instance = self.instance

        product_circuit = instance.product_circuit # fk
        rack_capacity = instance.rack_capacity     # Ci
        aisles_racks = instance.aisles_racks       # (racks par allée)
        aeration_rate = float(instance.metadata.get("aeration_rate", 0.0))
        
        num_products = int(instance.metadata.get("num_products", len(product_circuit)))
        R = len(aisles_racks)    # nb d'allées
        M = len(set(product_circuit)) # nb de familles
        Q = len(instance.orders)
        RBarre = R + 2 # {0} U R U {R+1}
        
        
        M1 = pe.ConcreteModel(name="MIP1")
        
        # Variables
        M1.x = pe.Var(range(num_products), range(R), name="x", bounds=(0,1), domain=pe.Binary) # x_kr
        M1.y = pe.Var(range(M), range(R), name="y", bounds=(0,1), domain=pe.Binary) # y_fr 
        M1.a = pe.Var(range(M), range(R), name="a", bounds=(0,1), domain=pe.Binary) # a_fr 
        M1.b = pe.Var(range(M), range(R), name="b", bounds=(0,1), domain=pe.Binary) # b_fr 
        M1.z = pe.Var(range(Q), range(R), name="z", bounds=(0,1), domain=pe.Binary) # z_ur
        M1.ztilde = pe.Var(range(Q), range(RBarre), range(RBarre), name="ztilde", bounds=(0,1), domain=pe.Binary) #z~_urs
        
        
        # Constraints
        
        # (2) : z_ur >= x_kr
        def const2(M1, u, k, r):
            if k not in instance.orders[u]:
                return pe.Constraint.Skip
            return M1.z[u,r] >= M1.x[k,r]
            
        M1.use_aisle = pe.Constraint(range(Q), range(num_products), range(R), rule=const2)

        # (3)
        def const3(M1, u, r, s):
            if r >= s:
                return pe.Constraint.Skip
            
			# z_u,r (start node)
            if r == 0:
				z_r = 1
			elif r == R + 1:
				return pe.Constraint.Skip
			else:
				z_r = M1.z[u, r]

			# z_u,s (end node)
			if s == R + 1:
				z_s = 1
			elif s == 0:
				return pe.Constraint.Skip
			else:
				z_s = M1.z[u, s]

			middle_sum = quicksum(
				M1.z[u, t] for t in range(r + 1, s) if t in range(R)
			)

			return M1.ztilde[u, r, s] >= z_r + z_s - 1 - middle_sum

		M1.transition = pe.Constraint(range(Q), range(RBarre), range(RBarre), rule=const3)


		# (4) : y_fr >= x_kr
		def const4(M1, k, r):
			f = product_circuit[k]
			return M1.y[f, r] >= M1.x[k, r]

		M1.family_activation = pe.Constraint(range(num_products), range(R), rule=const4)


		# (5) : sum(ztilde_u0s) = 1     start
		# (6) : sum(ztilde_urR+1) = 1   end
		def const5_6(M1, u):
			leave_start = quicksum(M1.ztilde[u, 0, s] for s in range(R)) == 1
			reach_end = quicksum(M1.ztilde[u, r, R + 1] for r in range(R)) == 1
			return [leave_start, reach_end]

		M1.start_end = pe.Constraint(range(Q), rule=const5_6)


		# (7) : in = out
		def const7(M1, u, s):
			if s == 0 or s == R + 1:
				return pe.Constraint.Skip

			incoming = quicksum(M1.ztilde[u, r, s] for r in range(RBarre) if r < s)
			outgoing = quicksum(M1.ztilde[u, s, r] for r in range(RBarre) if s < r)

			return incoming == outgoing

		M1.flow = pe.Constraint(range(Q), range(R), rule=const7)
  
  
		# (8) : sum(x_kr) = 1
		def const8(M1, k):
			return quicksum(M1.x[k, r] for r in range(R)) == 1

		M1.product_assignment = pe.Constraint(range(num_products), rule=const8)


		# (9) : cap + aeration/aisle
		def const9(M1, r):
			max_capacity = (1 - aeration_rate) * sum(rack_capacity[i] for i in aisles_racks[r])
			return quicksum(M1.x[k, r] for k in range(num_products)) <= max_capacity

		M1.capacity = pe.Constraint(range(R), rule=const9)


		# (10), (11) and (12) : middle, right and left
		def const10_11_12(M1, f, r):
			# Mid-contiguity
			sum_a = quicksum(M1.a[f, s] for s in range(r + 1))
			sum_b = quicksum(M1.b[f, s] for s in range(r))
			lower = M1.y[f, r] >= sum_a - sum_b

			# Right bound
			right = M1.y[f, r] <= 1 - sum_b

			# Left bound
			left = M1.y[f, r] <= 1 - sum_a

			return [lower, right, left]

		M1.y_contiguity = pe.Constraint(range(M), range(R), rule=const10_11_12)


		# (13) and (14) : start et end categories/families of products
		def const13_14(M1, f):
			one_start = quicksum(M1.a[f, r] for r in range(R)) == 1
			one_end = quicksum(M1.b[f, r] for r in range(R)) == 1
			
			return [one_start, one_end]

		M1.start_end_family = pe.Constraint(range(M), rule=const13_14)


		# (15) : sum afs <= sum bfs (start before end)
		def const15(M1, f, r):
			return quicksum(M1.a[f, s] for s in range(r + 1)) <= quicksum(M1.b[f, s] for s in range(r + 1))

		M1.start_before_end = pe.Constraint(range(M), range(R), rule=const15)


		# (16) : pas de chevauchement (no overlap)
		def const16(M1, f, g, r):
			if f == g:
				return pe.Constraint.Skip

			sum_a_g = quicksum(M1.a[g, s] for s in range(r))
			sum_b_g = quicksum(M1.b[g, s] for s in range(r + 1))
			return M1.a[f, r] <= 1 - sum_a_g + sum_b_g

		M1.no_overlap_families = pe.Constraint([(f, g, r) for f in range(M) for g in range(M) for r in range(R)],rule=const16)



		# Objective (min)
		def objective_rule(M1):
			total = 0
			for u in range(Q):
				# Dist inside aisles
				total += sum(instance.dist_a_b[r] * M1.z[u, r] for r in range(R))
				
				# Dist between aisles
				for r in range(RBarre):
					for s in range(r + 1, RBarre):
						total += instance.dist_ba[r, s] * M1.ztilde[u, r, s]
			return total

		M1.obj = pe.Objective(rule=objective_rule, sense=pe.minimize)

