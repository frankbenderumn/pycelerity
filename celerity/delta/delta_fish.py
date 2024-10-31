from celerity.delta.idelta import DeltaType, CollectionType
from celerity.delta.delta_tree import DeltaTree
from celerity.ir.fish import Fish
from celerity.delta.delta_constraint import DeltaConstraint
from celerity.config import console

class DeltaFish:
	def __init__(self, parent, delta_type: DeltaType, delta_tree: DeltaTree, fish_a: Fish, fish_b: Fish = None):
		self.delta_type = delta_type
		self.fish_a = fish_a
		self.fish_b = fish_b
		self.delta_tree = delta_tree
		self.duals: dict[str, tuple[DeltaType, Fish]] = {}
		self.singles: dict[str, tuple[DeltaType, DeltaConstraint]] = {}
		self.parent = parent
		self.id = self.fish_a.id
		
	def update(self):			
		if self.delta_type == DeltaType.UPDATION:
			old_constraint_keys = set(self.fish_a.constraints.keys())
			new_constraint_keys = set(self.fish_b.constraints.keys())
			created_constraint = list(new_constraint_keys - old_constraint_keys)
			deleted_constraint = list(old_constraint_keys - new_constraint_keys)
			console.log([s.value for s in list(self.fish_a.constraints.values())], color="MAG")
			console.log(f"Created constraints: {created_constraint}", color="MAG")
			console.log(f"Deleted constraints: {deleted_constraint}", color="MAG")
			
		# Must be an updated fish
			if self.fish_a.constraints != self.fish_b.constraints:
				intersected_fish = list(old_constraint_keys & new_constraint_keys)
				if "type" in intersected_fish:
					# Remove the element
					intersected_fish.remove("type")
					# Insert it at the beginning
					intersected_fish.insert(0, "type")
				console.log("INTERSECTED FISH ===========================================")
				console.log(intersected_fish)
				for constraint_id in intersected_fish:
					if self.fish_a.constraints.get(constraint_id).value != self.fish_b.constraints.get(constraint_id).value:
						console.log(self.fish_a.constraints.get(constraint_id).value, color="BLU")
						console.log(self.fish_b.constraints.get(constraint_id).value, color="GRE")
						fish_constraint: DeltaConstraint = DeltaConstraint(self.fish_a.id, DeltaType.UPDATION, self.delta_tree, self.fish_a.constraints.get(constraint_id), self.fish_b.constraints.get(constraint_id))
						fish_constraint.update()
						self.delta_tree.addNode(self.fish_a.id, constraint_id, DeltaType.UPDATION, CollectionType.CONSTRAINT, fish_constraint, True) # This needs to be true (?) # FIXME
				

			for constraint_id in created_constraint:
				console.log(constraint_id, color="YEL")
				fish_constraint = DeltaConstraint(self.fish_a.id, DeltaType.CREATION, self.delta_tree, self.fish_b.constraints.get(constraint_id))
				self.delta_tree.addNode(self.fish_a.id, constraint_id, DeltaType.CREATION, CollectionType.CONSTRAINT, fish_constraint, True)
			for constraint_id in deleted_constraint:
				fish_constraint = DeltaConstraint(self.fish_a.id, DeltaType.DELETION, self.delta_tree, self.fish_a.constraints.get(constraint_id))
				self.delta_tree.addNode(self.fish_a.id, constraint_id, DeltaType.DELETION, CollectionType.CONSTRAINT, fish_constraint, True)
			
			for _, dual in self.duals.items():
				dual.update()
				
		elif self.delta_type == DeltaType.CREATION:
			self.delta_tree.addNode(self.fish_a.id, DeltaType.CREATION, CollectionType.FISH, self.fish_a, True)

		elif self.delta_type == DeltaType.DELETION:
			self.delta_tree.addNode(self.fish_a.id, DeltaType.DELETION, CollectionType.FISH, self.fish_a, True)
				
	def resolve(self):
		# for _, single in self.singles.items():
		# 	single.resolve()
		result = {"fish-singles": self.singles}
			
		duals = []
		for _, dual in self.duals.items():
			duals.append(dual.resolve())
			
		result["fish-duals"] = duals
		
		return result

