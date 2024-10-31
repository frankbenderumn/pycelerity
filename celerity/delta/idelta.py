from enum import Enum
from celerity.config import console

class DeltaType(Enum):
	CREATION = 0
	UPDATION = 1
	DELETION = 2
	ROOT = 3
	
class CollectionType(Enum):
	OCEAN = 0
	CONGREGATION = 1
	SCHOOL = 2
	FISH = 3
	CONSTRAINT = 4
	
class DeltaDimType(Enum):
	SINGLE = 0
	DUAL = 1
	SET = 2
	ROOT = 3
