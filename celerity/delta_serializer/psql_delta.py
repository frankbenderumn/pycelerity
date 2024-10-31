from celerity.delta_serializer.idelta_serializer import IDeltaSerializer
from prizm.util.color import YEL
from celerity.serializers import serializers
from celerity.config import console
from celerity.util import reverse_dict
from celerity.ir.fish import Fish
from celerity.ir.congregation import Congregation
from celerity.delta.idelta import CollectionType

class PostgresDelta(IDeltaSerializer):
	
	def __init__(self, directories, ocean):
		super().__init__(directories, ocean)
	
	def create(self, ir_schools: dict[str, dict[str, dict[str, any]]]) -> str:
		congregation = Congregation(ir_schools) # needed because serialize takes a congregation
		delta_schema = serializers.get(self.ocean.format_type).serialize(CollectionType.CONGREGATION, congregation)
		return delta_schema
	
	def update(self, name: str, new_school: dict[str, dict[str, any]], old_school: dict[str, dict[str, any]], fish_deltas: dict[str, list[str]]) -> None:
		"""Note: Currently do not support alteration of currently constrained keys (pk and fk).
		Currently do not support changing types.
		This is likely worth creating an fish parser again, or rather using existing one.
		"""
		
		new_fishs = {}
		for fish_name, fish_validation in new_school.items():
			fish = Fish(fish_name, fish_validation)
			fish.parse()
			new_fishs[fish.name] = fish
			
		old_fishs = {}
		for fish_name, fish_validation in old_school.items():
			fish = Fish(fish_name, fish_validation)
			fish.parse()
			old_fishs[fish.name] = fish

		created_keys = list(set(new_school.keys()) - set(old_school.keys()))
		deleted_keys = list(set(old_school.keys()) - set(new_school.keys()))
		console.log("\tCreated Keys", color="YEL")
		console.log(f"\t\t{created_keys}")
		console.log("\tDeleted Keys", color="YEL")
		console.log(f"\t\t{deleted_keys}")
		constraints = []
		table_id = {}

		for created_key in created_keys:
			fish_str = serializers.get(self.data_manager.format_type).serialize_fish(created_key, new_school[created_key], table_id, constraints)
			fish_str = fish_str[1:] # remove tab
			fish_str = f"ALTER TABLE \"{name}\" ADD COLUMN {fish_str}"
			fish_str = fish_str[:-2] + ";\n"
			console.log("\t(Add) Altered Validations", color="YEL")
			console.log(f"\t\t{fish_str}")
			fish_deltas["creation"].append(fish_str)
		
		for deleted_key in deleted_keys:
			console.log("\t(Del) Altered Validations", color="YEL")
			fish_str = f"ALTER TABLE \"{name}\" DROP COLUMN \"{deleted_key.split(':')[0]}\";\n"
			console.log(f"\t\t{fish_str}")
			fish_deltas["deletion"].append(fish_str)
		
		intersected_keys = new_fishs.keys() & old_fishs.keys()
		updated_constraints = []
		updated_table_id = {}
		for key in intersected_keys:
			altered_constraint = new_fishs[key] & old_fishs[key]
			if altered_constraint is not None:
				fish_str = serializers.get(self.data_manager.format_type).serialize_fish(new_fishs[key].raw, new_fishs[key].validations, updated_table_id, updated_constraints)
				console.log("\t(Alt) Altered Validations", color="YEL")
				fish_str = f"ALTER TABLE \"{name}\" ALTER COLUMN \"{key}\" {altered_constraint};\n"
				console.log(f"\t\t{fish_str}")
				fish_deltas["updation"].append(fish_str)

		
	def delete(self, ir_schools: list[str]) -> str:
		"""
		Future work: May be worth adding 'DROP TABLE' serialization into serializers 
		and getting rid of this class entirely, therefore using only IDelta class because
		of serializers.get(self.data_manager.format_type)
		
		Args:
			ir_schools (dict[str, dict[str, dict[str, any]]]): Takes
				the dictionary of IR schools and serializes them to be
				dropped
				
		"""

		delta_drop_str = ""
		for ir_school_name in ir_schools:
			delta_drop_str += f"DROP TABLE IF EXISTS \"{ir_school_name}\";\n"

		console.log("Delta Deletion", color="YEL")
		console.log(delta_drop_str, color="MAG")

		return delta_drop_str

		pass
	