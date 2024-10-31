from celerity.ir.school import School
from celerity.delta.delta_fish import DeltaFish
from celerity.delta.idelta import DeltaType, CollectionType
from celerity.delta.delta_tree import DeltaTree
from celerity.util import str_checksum
from celerity.config import console

class DeltaSchool:
	
	# Assumption that both schools have same name
	def __init__(self, parent, delta_type: DeltaType, delta_tree: DeltaTree, school_a: School, school_b: School = None):
		self.school_a = school_a
		self.school_b = school_b
		self.delta_type = delta_type
		self.singles: dict[str, tuple[DeltaType, School]] = {}
		self.duals: dict[str, tuple[DeltaType, DeltaFish]] = {}
		self.delta_tree = delta_tree
		self.parent = parent
		self.id = self.school_a.id
				
	def update(self):
		if self.delta_type == DeltaType.UPDATION:
			# Must be an updated fish
			old_fish_keys = set(self.school_a.fish_ids())
			new_fish_keys = set(self.school_b.fish_ids())
			created_fish = list(new_fish_keys - old_fish_keys)
			deleted_fish = list(old_fish_keys - new_fish_keys)
			intersected_fish = list(old_fish_keys & new_fish_keys)

			if self.school_a.checksum != self.school_b.checksum:
				for fish_id in intersected_fish:
					console.log(f"{self.school_a.get_fish_by_id(fish_id).raw}", color="MAG")
					console.log(f"{self.school_b.get_fish_by_id(fish_id).raw}", color="YEL")
					console.log(f"{self.school_a.get_fish_by_id(fish_id).constraints}", color="MAG")
					console.log(f"{self.school_b.get_fish_by_id(fish_id).constraints}", color="YEL")
					console.log(f"{self.school_a.get_fish_by_id(fish_id).checksum}", color="MAG")
					console.log(f"{self.school_b.get_fish_by_id(fish_id).checksum}", color="YEL")
					if self.school_a.get_fish_by_id(fish_id).checksum != self.school_b.get_fish_by_id(fish_id).checksum:
						fish_updater: DeltaFish = DeltaFish(self.school_a.id, DeltaType.UPDATION, self.delta_tree, self.school_a.get_fish_by_id(fish_id), self.school_b.get_fish_by_id(fish_id))
						fish_updater.update()
						self.delta_tree.addNode(self.school_a.id, fish_id, DeltaType.UPDATION, CollectionType.FISH, fish_updater, False)
				
			console.log("\t\tCreated Fish", color="BYEL")
			console.log(f"\t\t\t{created_fish}")
			console.log("\t\tDeleted Fish", color="BYEL")
			console.log(f"\t\t\t{deleted_fish}")
			console.log("\t\tUpdated Fish", color="BYEL")
			console.log(f"\t\t\t{intersected_fish}")
			
			for fish_id in created_fish:
				fish_updater = DeltaFish(self.school_a.id, DeltaType.CREATION, self.delta_tree, self.school_b.get_fish_by_id(fish_id))
				self.delta_tree.addNode(self.school_a.id, fish_id, DeltaType.CREATION, CollectionType.FISH, self.school_b.get_fish_by_id(fish_id), True)
			for fish_id in deleted_fish:
				fish_updater = DeltaFish(self.school_a.id, DeltaType.DELETION, self.delta_tree, self.school_a.get_fish_by_id(fish_id))
				self.delta_tree.addNode(self.school_a.id, fish_id, DeltaType.DELETION, CollectionType.FISH, self.school_a.get_fish_by_id(fish_id), True)
				
			for _, dual in self.duals.items():
				dual.update()
				
		elif self.delta_type == DeltaType.CREATION: # These lines of code may not be needed?
			self.delta_tree.addNode(self.parent, self.school_a.id, DeltaType.CREATION, CollectionType.SCHOOL, self.school_a, True)
			
		elif self.delta_type == DeltaType.DELETION: # These lines of code may not be needed?
			self.delta_tree.addNode(self.parent, self.school_a.id, DeltaType.DELETION, CollectionType.SCHOOL, self.school_a, True)
				
		else:
			console.log("Action other than UPDATION being taken", color="RED")
			
	def resolve(self):
		result = {"school-singles": self.singles}		
		
		duals = []
		for _, dual in self.duals.items():
			duals.append(dual.resolve())

		result["school-duals"] = duals
		
		result = self.delta_tree

		return result