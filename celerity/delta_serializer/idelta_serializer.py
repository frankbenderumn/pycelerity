from abc import ABC, abstractmethod
from celerity.ir.ocean import Ocean

class IDeltaSerializer(ABC):
	
	def __init__(self, directories: dict[str, str], ocean: Ocean):
		self.directories = directories
		self.ocean: Ocean = ocean
	
	@abstractmethod
	def create(self, ir_schools: dict[str, dict[str, dict[str, any]]]):
		pass
	
	@abstractmethod
	def update(self, name: str, new_school: dict[str, dict[str, any]], old_school: dict[str, dict[str, any]], attr_deltas: dict[str, list[str]]):
		pass

	@abstractmethod
	def delete(self, ir_schools: list[str]):
		pass

	def persist():
		pass