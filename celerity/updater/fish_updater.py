from celerity.ir.fish import Fish
from celerity.delta.idelta import DeltaType
from celerity.updater.constraint_updater import ConstraintUpdater
from celerity.config import console

class FishUpdater:
	
	def __init__(self, delta_type: DeltaType, fish_a: Fish, fish_b: Fish = None):
		self.delta_type = delta_type
		self.fish_a = fish_a
		self.fish_b = fish_b
		self.updaters = None

	def update(self) -> None:
		constraint_updaters: dict[str, ConstraintUpdater] = self.fish_a & self.fish_b
		self.updaters = constraint_updaters
		for updater_id, updater in self.updaters.items():
			updater.update()
		# take the updaters and form delta

	def resolve(self) -> None:
		console.log("hi")
		console.log(self.updaters)
		for updater_id, updater in self.updaters.items():
			updater.resolve()
	
	def dump(self) -> None:
		console.log("Old Fish")
		self.fish_a.dump()
		console.log("New Fish")
		self.fish_b.dump()
