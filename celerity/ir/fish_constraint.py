# Attribute constraint types are as follows:
# (limit)
# (default)
# (optional | ?)
# (unique | *)
# (alias | =)
# (optional and unique | +)
# (reqex)

from celerity.ir.iconstraint import IConstraint

class FishConstraint(IConstraint):
	
	def __init__(self, key, value, parent, constraint_type = None):
		super().__init__(key, value, parent, constraint_type)
