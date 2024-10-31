from celerity.ir.fish import Fish
from celerity.ir.school_constraint import SchoolConstraint
from celerity.config import console
from celerity.util import str_checksum
from celerity.delta.idelta import DeltaType, CollectionType
from celerity.updater.fish_updater import FishUpdater
from celerity.updater.updateable import Updateable

class School(Updateable):
	
	def _load(self):
		console.log(f"School fishs for school '{self.name}'", color="YEL")  # Log the school fishibutes
		for fish_name, fish_constraints in self.fish_script.items():
			a_fish = Fish(self.name, fish_name, fish_constraints)
			self.fish[a_fish.id] = a_fish
			if a_fish.school_constraint is not None:
				c = SchoolConstraint(a_fish)
				self._constraints[c.constraint_type] = c
		
	def __init__(self, name, fish_script):
		self.fish_script = fish_script
		self.checksum = str_checksum(str(fish_script))
		self.name = name
		self.fish = {}
		self._constraints = {}
		self.id = name

		self._load()
		super().__init__(CollectionType.SCHOOL)

	def fish_ids(self):
		return self.fish.keys()
	
	def get_fish_by_id(self, id: str):
		return self.fish.get(id)

	def constraints(self):
		return self._constraints
	
	def __and__(self, other_school) -> dict[str, FishUpdater]:
		old_fish_keys = set(self.fish.keys())
		new_fish_keys = set(other_school.fish.keys())
		created_fish = list(new_fish_keys - old_fish_keys)
		deleted_fish = list(old_fish_keys - new_fish_keys)
		fish_updater_collection: dict[str, FishUpdater] = {}
		for fish_id in created_fish:
			fish_updater: FishUpdater = FishUpdater(DeltaType.CREATION, other_school.fish.get(fish_id))
			fish_updater_collection[fish_id] = fish_updater
		for fish_id in deleted_fish:
			fish_updater: FishUpdater = FishUpdater(DeltaType.DELETION, self.fish.get(fish_id))
			fish_updater_collection[fish_id] = fish_updater
			
		# Must be an updated fish
		if self.checksum != other_school and deleted_fish == [] and created_fish == []:
			interesected_fish = list(old_fish_keys & new_fish_keys)
			for fish_id in interesected_fish:
				if self.fish.get(fish_id).checksum != other_school.fish.get(fish_id).checksum:
					fish_updater: FishUpdater = FishUpdater(DeltaType.UPDATION, self.fish.get(fish_id), other_school.fish.get(fish_id))
				fish_updater_collection[fish_id] = fish_updater
					
		return fish_updater_collection
