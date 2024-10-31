from celerity.delta.idelta import CollectionType

class Updateable:
	def __init__(self, collection_type: CollectionType):
		self.collection_type = collection_type