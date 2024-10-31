from celerity.updater.updateable import Updateable
from celerity.delta.idelta import CollectionType

class IConstraint(Updateable):

	def __init__(self, key, value, parent, constraint_type = None):
		self.parent = parent
		self.id = parent + "-" + key
		self.key = key
		self.value = value
		self.type = constraint_type
		super().__init__(CollectionType.CONSTRAINT)