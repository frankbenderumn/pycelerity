from celerity.delta.idelta import DeltaType, CollectionType, DeltaDimType
from celerity.config import console

class DeltaNode:
	def __init__(self, id, delta_type: DeltaType, collection_type: CollectionType, data, terminal = False):
		self.data = data
		self.delta_type = delta_type
		if self.delta_type in [DeltaType.CREATION, DeltaType.DELETION]:
			self.delta_dim_type = DeltaDimType.SINGLE
		elif self.delta_type == DeltaType.UPDATION:
			self.delta_dim_type = DeltaDimType.DUAL
		self.collection_type = collection_type
		self.id = id
		self.terminal = terminal
		
	def update(self):
		return self.data.update()
	
	def resolve(self):
		return self.data.resolve()
	
	def dump(self):
		console.log(f"\t {self.id} {self.delta_type}, {self.collection_type}, {self.data} {self.terminal}")
