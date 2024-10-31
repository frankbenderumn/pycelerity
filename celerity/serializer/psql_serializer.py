from celerity.serializer.iserializer import ISerializer
from celerity.config import console
from celerity.ir.fish import Fish
from celerity.ir.school import School
from celerity.ir.congregation import Congregation
from celerity.ir.school_constraint import SchoolConstraint
from celerity.delta.idelta import CollectionType, DeltaType
from celerity.delta.delta_node import DeltaNode
from celerity.ir.iconstraint import IConstraint
from celerity.delta.delta_constraint import DeltaConstraint

class PostgresSerializer(ISerializer):

	def __init__(self):
		# Mapping of custom data types to PostgreSQL data types
		type_map = {
			"INT": "INTEGER",
			"FLOAT": "DECIMAL",
			"INTEGER": "INTEGER",
			"DOUBLE": "DECIMAL",
			"DECIMAL": "DECIMAL",
			"BOOL": "BOOLEAN"
		}
		super().__init__(type_map)

	def data_type(self, fish: Fish):
		"""
		Maps a given fishibute type to PostgreSQL data types based on predefined mappings.

		Args:
			fish (Fish): The fishibute object containing type information.

		Returns:
			str: The corresponding PostgreSQL data type.
		
		Raises:
			ValueError: If the type cannot be mapped, or if a string type is missing a limit.
		"""
		pg_type = fish.type  # Get the fishibute type
		# constraints = fish.validations  # Get the validation rules # FIXME
		
		if pg_type == "str":
			limit = fish.constraints.get("limit")  # Check for a specified length limit # FIXME
			if limit.value is not None:
				return f"VARCHAR({limit.value})"  # Return the VARCHAR type with the specified limit
			else:
				raise ValueError("\033[1;31mString type needs a limit validation specified\033[0m")
		else:
			# Try to map the type to a PostgreSQL compatible type
			try:
				result = self.type_map[pg_type.upper()]
			except:
				# Raise an error if mapping fails
				raise ValueError(f"\033[1;31mType '{pg_type.upper()}' can't be mapped in postgres\033[0m")
			return result  # Return the mapped PostgreSQL type

	def school_constraints(self, constraint: SchoolConstraint):
		
		fish_str = ""
		fish = constraint.fish
		
		# Serialize fish name according to potential alias
		fish_name = fish.name
		if fish.alias:
			fish_name = fish.alias

		# Process fishibute based on its constraints
		if constraint.constraint_type != "poly": # can not combine alias with polymorphic
			fish_type = self.data_type(fish)  # Get the mapped PostgreSQL type

		# Handle primary key
		if constraint.constraint_type == "pk" and constraint.auto == True:
			fish_str += f"\t{fish_name} SERIAL PRIMARY KEY,\n"  # Define as SERIAL and PRIMARY KEY

		# Handle foreign key fishibutes
		elif constraint.constraint_type == "fk":
			if fish.alias is None:
				fish_name = f"{fish.name}_{fish.reference}" 
			fish_str += f"\t{fish_name} {fish_type}"  # Define the fishibute type
			fish_str = self.serialize_fish_constraints(fish_str, fish)  # Apply validations # FIXME
			fish_str += f"\tFOREIGN KEY ({fish_name}) REFERENCES \"{fish.name}\"({fish.reference}) ON DELETE CASCADE,\n" #FIXME

		elif constraint.constraint_type == "poly":
			# Handle polymorphic associations
			fish_str += f"\t{fish.name}_type VARCHAR(50) NOT NULL,\n"
			fish_str += f"\t{fish.name}_id INTEGER NOT NULL,\n"
			fish_str += f"\tUNIQUE ({fish.name}_id, {fish.name}_type),\n"
			
		elif fish.school_constraint.constraint_type == "idx": # TODO: Need to implement
			pass
		elif fish.school_constraint.constraint_type == "cpk": # TODO: Need to implement
			pass
		
		return fish_str
	
	def serialize_fish_constraints(self, fish_str: str, fish: Fish):
		"""
		Adds validation constraints to the fishibute string for PostgreSQL based on special properties.

		Args:
			fish_str (str): The base SQL fishibute string to modify.
			fish (Fish): The fishibute object containing validation information.

		Returns:
			str: The modified SQL fishibute string with validations applied.
		"""
		
		# NOTE: It would appear that fish.special is a word rather than a symbol 
		# likely from fish.parse() functionality
		if fish.special is not None and fish.special != "":
			console.log(f"Fish constraint detected on '{fish.name}' ", color="MAG")
			console.log(fish.special)
		
		# Apply special constraints based on fishibute properties
		if fish.special == "unique":
			fish_str += " UNIQUE NOT NULL"  # Add UNIQUE constraint
		elif fish.special == "optional":
			fish_str += " NULL"  # Allow NULL values
		elif fish.special == "reqopt": # should be something like uniqopt instead
			fish_str += " UNIQUE NULL"  # Allow NULL values and enforce uniqueness
		else:
			fish_str += " NOT NULL"  # Disallow NULL values by default
		
		# Check for other validations specified in the fishibute
		add_check = None
		for v_name, constraint in fish.constraints.items():
			if v_name == "regex":
				if constraint.value == "email":
					# Add a CHECK constraint for email validation
					add_check = f"\tCHECK ({fish.name} ~* '^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\\\.[a-z|A-Z]{{2,}}$'),\n"
			elif v_name == "default":
				if fish.type == "str":
					fish_str += f" DEFAULT '" + str(constraint.value) + "'"
				else:
					fish_str += f" DEFAULT " + str(constraint.value)

		fish_str += ",\n"  # End the fishibute definition with a comma
		
		if add_check is not None:
			fish_str += add_check
		
		return fish_str  # Return the modified fishibute string
	
	def serialize_fish(self, fish: Fish):
		fish_str = ""  # Initialize the string for this fishibute's SQL definition

		# If does not possess a constraint
		if fish.school_constraint is None:
			# Serialize fish name according to potential alias
			fish_name = fish.name
			if fish.alias:
				fish_name = fish.alias
			
			fish_type = self.data_type(fish)

			# Handle regular fishibutes
			fish_str += f"\t{fish_name} {fish_type}"  # Define the fishibute type
			fish_str = self.serialize_fish_constraints(fish_str, fish)  # Apply validations # FIXME

		return fish_str  # Append the fishibute string to the result

	def serialize_school(self, school: School):
		"""
		Serializes a school schema into a PostgreSQL CREATE TABLE statement.

		Args:
			school_name (str): The name of the school being serialized.
			school_fishs (dict): A dictionary of fishibutes for the school.

		Returns:
			str: The complete CREATE TABLE SQL statement.

		Raises:
			ValueError: If the school does not have a primary key.
		"""
		result_str = ""  # Initialize the result string for the SQL statement
		result_str += f"CREATE TABLE IF NOT EXISTS \"{school.name}\" (\n"  # Start the CREATE TABLE statement
		
		constraints = school.constraints()

		# Iterate through each fishibute in the school
		for fish_name, fish in school.fish.items():
			fish_str = self.serialize_fish(fish) # could change to self.fish(fish)
			result_str += fish_str  # Append the fishibute string to the result

		# Append all foreign key constraints to the result
		console.log(constraints, color="CYA")
		for constraint_type, constraint in constraints.items():
			result_str += self.school_constraints(constraint)

		# Remove the trailing comma and newline, and close the CREATE TABLE statement
		result_str = result_str[:-2]
		result_str += "\n);\n"
		
		# Raise an error if no primary key was defined for the school
		if constraints.get("pk") is None:
			raise ValueError(f"\033[1;31mSchool '{school.name}' does not have a primary key!\033[0m")
		
		return result_str  # Return the complete CREATE TABLE statement

	def serialize_congregation(self, congregation: Congregation) -> str:
		"""
		Serializes all schools in the global `schools` dictionary into CREATE TABLE statements.

		Args:
			sorted_schools (dict): A dictionary of schools to serialize.

		Returns:
			str: A string containing all CREATE TABLE statements.
		"""
		
		result_str = ""  # Initialize the result string
		for school_name, school in congregation.schools.items():
			result_str += self.serialize_school(school)  # Serialize each school

		return result_str # Return the complete string of CREATE TABLE statements
	
	# TODO: These two are to be determined
	# def serialize_alter_ocean(self, ocean: Ocean) -> str:
	# 	return ""

	def serialize_alter_congregation(self, delta_type: DeltaType, congregation: Congregation) -> str:
		return ""

	def serialize_alter_school(self, delta_type: DeltaType, school: School) -> str:
		serialized_str = ""
		if delta_type == DeltaType.CREATION:
			serialized_str = self.serialize_school(school)
		elif delta_type == DeltaType.UPDATION:
			serialized_str = f"ALTER TABLE {school.name}..."
		elif delta_type == DeltaType.DELETION:
			serialized_str = f"DROP TABLE {school.name} IF NOT EXISTS;\n"
		return serialized_str

	def serialize_alter_fish(self, delta_type: DeltaType, fish: Fish) -> str:
		serialized_str = ""
		if delta_type == DeltaType.CREATION:
			serialized_str = self.serialize_fish(fish)
			serialized_str = serialized_str[:-2]
			serialized_str = f"ALTER TABLE \"{fish.parent}\" ADD COLUMN {serialized_str[1:]};\n"
		elif delta_type == DeltaType.UPDATION:
			serialized_str = f"ALTER TABLE \"{fish.name}..."
		elif delta_type == DeltaType.DELETION:
			serialized_str = f"ALTER TABLE \"{fish.parent}\" DROP COLUMN \"{fish.name}\";\n"
		return serialized_str
	
	def serialize_addendum(self, constraint):
		key = constraint.constraint_a.key
		constraint_type = constraint.constraint_a.type
		if constraint.constraint_b is None:
			val = constraint.constraint_a.value
		else:
			val = constraint.constraint_b.value
			constraint_type = constraint.constraint_b.type
		console.log(key, color="BLU")
		console.log(val, color="MAG")
		console.log(constraint_type, color="YEL")
		console.log("---------------------------")
		if key == "limit":
			return f"SET DATA TYPE VARCHAR({val})"
		elif key == "default":
			if constraint_type == "str":
				return f"SET DEFAULT '{val}'"
			else:
				return f"SET DEFAULT {val}"
		elif key == "type":
			return f"SET DATA TYPE {self.type_map[val.upper()]}"
		elif key == "unique":
			print("TODO... postgres_serializer:serialize_addendum:259")
			return "TODO... postgres_serializer:serialize_addendum:259"
		elif key == "nullable":
			pass
			return "TODO"

	def serialize_alter_constraint(self, delta_type: DeltaType, constraint: DeltaConstraint, chain: list[str] = None) -> str:
		# TODO: Implement name change feature "=>"		

		console.log(chain, color="BLU")
		school = "|null|"
		fish = "|null|"
		for el in chain:
			if el[1] == CollectionType.FISH:
				fish = el[0]
			elif el[1] == CollectionType.SCHOOL:
				school = el[0]

		constraint_addendum = f"SET {constraint.constraint_a.key}"
		constraint_addendum = self.serialize_addendum(constraint)

		if delta_type == DeltaType.CREATION:
			if constraint.constraint_a.key == "unique":
				serialized_str = f"ALTER TABLE \"{school}\" ALTER COLUMN \"{fish}\" {constraint_addendum};\n"
			else:
				serialized_str = f"ALTER TABLE \"{school}\" ALTER COLUMN \"{fish}\" {constraint_addendum};\n"
		elif delta_type == DeltaType.DELETION:
			serialized_str = f"ALTER TABLE \"{school}\" ALTER COLUMN \"{fish}\" DROP CONSTRAINT {constraint.constraint_a.key};\n"
		elif delta_type == DeltaType.UPDATION:
			# May need specific rules here for constraint
			serialized_str = f"ALTER TABLE \"{school}\" ALTER COLUMN \"{fish}\" {constraint_addendum};\n"
		return serialized_str

	def serialize_alter(self, node: DeltaNode, chain) -> str:
		serialized_str = ""
		if node.collection_type == CollectionType.OCEAN:
			# serialized_str = self.alter_ocean() # NOTE: ignore until refactor/UML complete
			pass
		elif node.collection_type == CollectionType.CONGREGATION:
			serialized_str = self.serialize_alter_congregation(node.delta_type, node.data)
		elif node.collection_type == CollectionType.SCHOOL:
			serialized_str = self.serialize_alter_school(node.delta_type, node.data)
		elif node.collection_type == CollectionType.FISH:
			serialized_str = self.serialize_alter_fish(node.delta_type, node.data)
		elif node.collection_type == CollectionType.CONSTRAINT:
			serialized_str = self.serialize_alter_constraint(node.delta_type, node.data, chain)
		return serialized_str

	def serialize(self, collection_type: CollectionType, data: any) -> str:
		serialized = ""
		if collection_type == CollectionType.CONGREGATION:
			serialized = self.serialize_congregation(data)
		elif collection_type == CollectionType.SCHOOL:
			console.log("Meh", color="MAG")
			serialized = self.serialize_school(data)
		elif collection_type == CollectionType.FISH:
			console.log("Meh", color="MAG")
			serialized = self.serialize_fish(data)
		elif collection_type == CollectionType.CONSTRAINT: # Aggregation, Not composition (strong containtment/black diamond)
			console.log("Meh", color="RED")
			# serialized = self.serialize_fish_constraint(data)
		return serialized
			