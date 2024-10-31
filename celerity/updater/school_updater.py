from celerity.ir.school import School
from celerity.updater.fish_updater import FishUpdater
from celerity.config import console
from celerity.delta.idelta import DeltaType, CollectionType
from celerity.delta.delta_tree import DeltaTree
from celerity.delta.delta_school import DeltaSchool
from celerity.serializers import serializers

class SchoolUpdater:
	"""
	Updaters are responsible for staging updates before resolving and commiting them by checking
	for errorneous in between the update and resolution phase
	"""	

	def __init__(self, school_a: School, school_b: School):
		self.school_a = school_a
		self.school_b = school_b
		self.updaters = None
		self.delta_school = None
		self.delta_tree = DeltaTree(school_a.name, CollectionType.CONGREGATION)
		
	def update(self) -> int:
		console.log("\tUpdating School", color="YEL")
		# fish_updaters: dict[str, FishUpdater] = self.school_a & self.school_b
		self.delta_school = DeltaSchool("__root__", DeltaType.UPDATION, self.delta_tree, self.school_a, self.school_b)
		self.delta_tree.addNode("__root__", self.school_a.id, DeltaType.UPDATION, CollectionType.SCHOOL, self.delta_school)
		self.delta_school.update()
		console.log(self.delta_school.singles, color="YEL")
		console.log(self.delta_school.duals, color="MAG")

	# Would be neat to make some sort of tree structure with three node types single, dual, and set
	def resolve(self, format_type: str) -> None:
		# for updater_id, updater in self.updaters.items():
		# 	updater.resolve() # Project down operation
		
		# Need type identification

		resolution = self.delta_school.resolve()
		
		console.log(resolution)
		console.log("Delta Tree", color="YEL")

		self.delta_tree.dump()
		result = self.delta_tree.serialize("psql")

		console.log(result, color="BMAG")
		
		return result