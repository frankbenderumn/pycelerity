from celerity.delta.idelta import CollectionType, DeltaType
from celerity.config import console
from celerity.delta.delta_school import DeltaSchool
from celerity.delta.delta_tree import DeltaTree
from celerity.delta.delta_map import delta_map
from celerity.updater.updateable import Updateable
		
class Updater:
	
	def __init__(self, updateable_a: Updateable, updateable_b: Updateable):
		if updateable_a.collection_type != updateable_b.collection_type:		
			raise TypeError(f"Updateables in updater must be matching types! Received: {updateable_a.collection_type} and {updateable_b.collection_type}, respectively!")
		collection_type = updateable_a.collection_type
		if collection_type.value != 0:
			collection_type = CollectionType(collection_type.value - 1)
		self.updateable_a = updateable_a
		self.updateable_b = updateable_b
		self.collection_type = self.updateable_a.collection_type
		self.delta_tree = DeltaTree(updateable_a.name, collection_type) # Collection One higher than the one being updated
		self.delta_collection = None
	
	def update(self) -> int:
		self.delta_collection = delta_map[self.updateable_a.collection_type]("__root__", DeltaType.UPDATION, self.delta_tree, self.updateable_a, self.updateable_b)
		self.delta_tree.addNode("__root__", self.updateable_a.id, DeltaType.UPDATION, self.updateable_a.collection_type, self.delta_collection)
		self.delta_collection.update()

	def resolve(self, format_type: str) -> None:
		resolution = self.delta_collection.resolve()
		
		console.log("Delta Tree", color="YEL")
		self.delta_tree.dump()
		
		result = self.delta_tree.serialize("psql")
		console.log(result, color="BMAG")
		
		return result