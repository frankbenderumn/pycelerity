from celerity.config import console
from celerity.ir.fish import Fish
from celerity.ir.iconstraint import IConstraint

# School constraint types include:
# (PK | !) primary key, (FK | @<school>-><school_id>) foreign key, (CPK | &) composite foreign key, 
# (IDX | %) index, and (POLY | #) polymorphic

# FK can have cascade attribute

class SchoolConstraint(IConstraint):
	
	def __init__(self, fish: Fish):
		if fish.school_constraint is None:
			raise ValueError("\033[1;31mError:\033[0m School constraint with type 'None' being forced!")
		self.constraint_type = fish.school_constraint
		self.auto = True # Default behavior is SERIAL PRIMARY KEY
		self.fish = fish
		
	def dump(self):
		console.log("School Constraint Present")
		console.log(f"Type: {self.constraint_type}")
	