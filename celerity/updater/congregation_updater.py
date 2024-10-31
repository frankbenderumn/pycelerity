from celerity.ir.congregation import Congregation
# from celerity.delta.delta_congregation import DeltaCongregation

class CongregationUpdater:
	def __init__(self, congregation_a: Congregation, congregation_b: Congregation):
		self.congregation_a = congregation_a
		self.congregation_b = congregation_b