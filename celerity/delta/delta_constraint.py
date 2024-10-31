from celerity.delta.idelta import DeltaType, CollectionType
# from celerity.delta.delta_tree import DeltaTree
from celerity.ir.iconstraint import IConstraint
from celerity.config import console

class DeltaConstraint:
	def __init__(self, parent, delta_type: DeltaType, delta_tree, constraint_a: IConstraint, constraint_b: IConstraint = None):
		self.constraint_a = constraint_a
		self.constraint_b = constraint_b
		self.delta_type = delta_type
		self.delta_tree = delta_tree
		self.duals = {}
		self.singles = {}
		self.parent = parent
		self.terminal = True
		self.id = self.constraint_a.id

	def update(self):
		# This granularity may not be needed, because is leaf
		# if self.delta_type == DeltaType.CREATION:
		# 	self.delta_tree.addNode(self.parent, self.constraint_a.key, DeltaType.CREATION, CollectionType.CONSTRAINT, self.constraint_a, True)
		
		# elif self.delta_type == DeltaType.DELETION:
		# 	self.delta_tree.addNode(self.parent, self.constraint_a.key, DeltaType.DELETION, CollectionType.CONSTRAINT, self.constraint_a, True)
		
		# elif self.delta_type == DeltaType.UPDATION:
		# 	console.log(self.constraint_a.value, color="GRE")
		# 	console.log(self.constraint_b.value, color="YEL")
		# 	self.delta_tree.addNode(self.parent, self.constraint_a.key, DeltaType.UPDATION, CollectionType.CONSTRAINT, (self.constraint_a.value, self.constraint_b.value), True)
			
		# 	console.log(self.duals, color="BLU")
		pass

	def resolve(self):
		console.log("Constraint", color="CYA")
		console.log(self.singles)
		console.log(self.duals)
		return {"constraint-singles": self.singles, "constraint-duals": self.duals}