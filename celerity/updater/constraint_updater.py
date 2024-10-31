from celerity.ir.iconstraint import IConstraint
from celerity.config import console
from celerity.delta.idelta import DeltaType
# diadromous

class ConstraintUpdater:
	
	def __init__(self, delta_type: DeltaType, constraint_a: IConstraint, constraint_b: IConstraint):
		self.constaint_a = constraint_a
		self.constaint_b = constraint_b
		self.updaters = None
		self.leaf = True # Delta Query/Embedding Tree design
	
	def update(self):
		console.log("Type check on constraints", color="YEL")
		console.log(self.constraint_a.constraint_type)
		console.log(self.constraint_b.constraint_type)
		pass
	
	def resolve(self):
		pass