import os
import json
import time
import stat

from celerity.config import console
from celerity.util import file_checksum, reverse_dict, topological_sort, copy_directory
from celerity.ir.school import School
from celerity.serializers import serializers
from celerity.ir.congregation import Congregation
from celerity.test.mocker import mock_timestamp
from celerity.ir.metadata import Metadata
from celerity.delta.idelta import CollectionType

class Ocean:
	
	def _load(self):
		"""
		Loads and sorts the tables in an Intermediate Representation (IR) format (python dictionary).

		Args:
			directories[str, str]: The schema representation as a dictionary, where keys are table names and values are attribute dictionaries.

		Returns:
			tuple[dict[str, any], dict[str, any]]: A tuple with a dictionary of the path index and a dictionary consisting of the sorted IR tables.
		"""

		input_dir = self.directories_b["input"]
		
		deps: dict[str, any] = {} # To map tables to their foreign key dependencies

		# Turns all json objects to python dicts and sanity checks
		# an object is not added twice i.e. user then user again
		tables: dict[str, any] = {}
		path_index: dict[str, any] = {}
		
		files: list[str] = os.listdir(input_dir)
		
		console.log("Files to be considered for IR", color="YEL")
		for basename in files:
			path_index[input_dir + basename] = []
			with open(input_dir + basename, "r") as f:
				console.log("\t" + input_dir + basename)
				try:
					partial_schema = json.load(f)
				except:
					raise IOError(f"\033[1;31mError: \033[0mInvalid JSON provided in file: {input_dir + basename}")
				# Will likely Need more sanity checks on valid json
				if partial_schema == {}:
					continue
				elif partial_schema.values() == {}:
					console.log('Schema has no values', color="GRE")
					continue
				for table_name, table in partial_schema.items():
					if table_name in list(tables.keys()):
						raise ValueError(f"\033[1;31mError: \033[0mTable Name '{table_name}' is already present in schema")
					tables[table_name] = table
					path_index[input_dir + basename].append(table_name)

		console.log(tables, color="GRE")
		# Iterate through each table in the schema and determine ordering
		for table_name, table_attrs in tables.items():

			# Check each attribute in the table
			for attr in table_attrs.keys(): 

				# Foreign key attributes are prefixed with '@'
				if attr[0] == "@":  
					# constrained = True  # Mark that this table has a foreign key
					parent = attr.split("->")[0][1:]  # Extract the parent table name from the foreign key definition
					deps[table_name] = parent  # Record the dependency
					break  # Stop checking attributes for this table

		# Log the discovered dependency graph
		console.log("Dependency Graph", color="YEL")
		console.log(f"\t{deps}")
		
		sorted_deps = topological_sort(deps)
		console.log(f"Sorted deps", color="YEL")
		console.log(f"\t{sorted_deps}")
		
		# Makes sure to add tables that have no relation and are entirely 
			# standalone
		all_names = [name for name in list(tables.keys())]
		diff_names = list(set(all_names) - set(sorted_deps))
		sorted_deps.extend(sorted(diff_names)) # strangely these need to be sorted

		sorted_tables = {key: tables[key] for key in sorted_deps if key in tables}
		
		self.congregation_b = Congregation(sorted_tables)
		self._new_metadata.path_index = path_index
		self.new_metadata().school_checksums = sorted_tables

		if console.terminal:
			self.dump()


	def __init__(self, directories_a: dict[str, str], format_type: str, directories_b: dict[str, str] = None): # should add rollback directory to here
		"""
		Args:
			previous_directories (dict[str, str]): the directories from which the previous ocean data is loaded
			output_directories (dict[str, str]): [TEST] the directories where the altered ocean data will reside
		"""
		# NOTE: Should make this class have a old and current representation
		# for atomicity
		
		self.format_type = format_type
		self.changed: bool = False
		self.serialized_delta: str = ""
		

		#######
		# Important Code. Manages the previous and current states, 
		# to allow for successful atomicity and delta updates
		#######
		# Binds directories for chaining, replication, and/or testing purposes
		self.directories_a: dict[str, str] = directories_a
		self.directories_b: dict[str, str] = directories_a
		
		self._old_metadata = Metadata(self.directories_a, "old")
		self._old_metadata.load()
		
		self._new_metadata = self._old_metadata
		
		if directories_b is not None:
			self.directories_b = directories_b
			self._new_metadata = Metadata(self.directories_b, "new")


		# Code related to hierarchical compositions
		# Serialized oceans to compare for delta operations
		self.serialized_ocean_a: str = None
		self.serialized_ocean_b: str = None

		# Intermediate representation of schools
		self.congregation_a: Congregation = Congregation()
		self.congregation_a.load(self.directories_a, "old")

		self.congregation_b: Congregation = None
		
		# Loads data from the new directory
		console.log(f"{'-' * 100}LOADING OCEAN{'-' * 100}", color="BMAG")
		self._load()
		console.log(f"{'=' * 100}OCEAN LOADED{'=' * 100}", color="BGRE")
		
	def serialize(self):
		self.serialized_congregation = serializers.get(self.format_type).serialize(CollectionType.CONGREGATION, self.congregation_b) # NOTE: Should be serialized to congregation likely
		console.log("Serialized Congregation\n===========================================", color="MAG")
		console.log(self.serialized_congregation)

	def persist(self):
		
		# Used for testing or outputing to a separate directory
		new_dirs = self.directories_b

		console.log("Delta", color="YEL")
		console.log(self.serialized_delta)
		
		console.log("PERSIST DIRECTORIES", color="BRED")
		console.log(new_dirs)

		old_schema_path = self.directories_a["output"] + "schema.lock"
		
		if os.path.exists(old_schema_path):
			with open(old_schema_path, "r") as f:
				old_schema = f.read()
		else:
			old_schema = self.serialized_congregation

		self.compiled_schema = self.serialized_congregation
		
		console.log("old schema", color="YEL")
		console.log(old_schema)

		# Persisting rollback information
		os.makedirs(new_dirs["rollback"] + self._new_metadata.id + "/", exist_ok=True)

		with open(new_dirs["rollback"] + self._new_metadata.id + "/delta.lock", "w") as f:
			f.write(self.serialized_delta)
		
		with open(new_dirs["rollback"] + self._new_metadata.id + "/schema.lock", "w") as f:
			f.write(old_schema + self.serialized_delta)
			
		with open(new_dirs["rollback"] + self._new_metadata.id + "/original.lock", "w") as f:
			f.write(old_schema)
		
		output_schema_path = new_dirs["output"] + "schema.lock"
		output_metadata_path = new_dirs["output"] + "metadata.lock"
		output_composite_path = new_dirs["output"] + "composite.lock"
		
		console.log("Metadata", color="YEL")
		console.log(f"\t{self._new_metadata.ir()}")
		# Make the file writable
		if os.path.exists(output_schema_path):
			os.chmod(output_schema_path, stat.S_IREAD | stat.S_IWRITE)

		if os.path.exists(output_metadata_path):
			os.chmod(output_metadata_path, stat.S_IREAD | stat.S_IWRITE)

		if os.path.exists(output_composite_path):
			os.chmod(output_composite_path, stat.S_IREAD | stat.S_IWRITE)

		with open(output_schema_path, "w") as f:
			f.write(old_schema + self.serialized_delta)
		
		with open(output_metadata_path, "w") as f:
			json.dump(self._new_metadata.ir(), f, indent=4)
			
		with open(output_composite_path, "w") as f:
			json.dump(self.congregation_b.schools_script, f, indent=4)
			
		# Make the file read-only
		os.chmod(output_schema_path, stat.S_IREAD)
		os.chmod(output_metadata_path, stat.S_IREAD)
		os.chmod(output_composite_path, stat.S_IREAD)
		
		if self.changed:
			
			console.log("DELTA CHANGE DETECTED")
		
			# Save previous states in rollback directory
			rollback_dir = new_dirs["rollback"] + self._new_metadata.id + "/"
			rollback_input_dir = rollback_dir + "/input/"
			os.makedirs(rollback_dir, exist_ok=True)
			os.makedirs(rollback_input_dir, exist_ok=True)
			
			previous_rollback_dir = self.directories_a["rollback"]
			copy_directory(previous_rollback_dir, new_dirs["rollback"])
			
			files = os.listdir(self.directories_a["input"])
			for basename in files:
				with open(self.directories_a["input"] + basename, "r") as f:
					byte_str = f.read()
					
				with open(rollback_dir + "input/" + basename, "w") as f:
					f.write(byte_str)

			files_b = os.listdir(self.directories_b["input"])
			for basename in files_b:
				with open(self.directories_b["input"] + basename, "r") as f:
					byte_str = f.read()
					
				with open(rollback_dir + "input/" + basename, "w") as f:
					f.write(byte_str)

			with open(rollback_dir + "metadata.lock", "w") as f:
				json.dump(self._new_metadata.ir(), f, indent=4)
				
			with open(rollback_dir + "composite.lock", "w") as f:
				json.dump(self.congregation_b.schools_script, f, indent=4)
				
		else:
			console.log("CHANGE NOT DETECTED")

	def acid(self):
		pass
	
	def old_metadata(self):
		return self._old_metadata
	
	def new_metadata(self):
		return self._new_metadata
	
	def commit_metadata(self):
		why = self._new_metadata & self._old_metadata
	
	def dump(self):
		console.log("Schema IR", color="YEL")
		for school_name, school in self.congregation_b.schools_script.items():
			console.log(f"\t{school_name}", color="CYA")
			for attr, validations in school.items():
				console.log(f"\t\t{attr:<16} -- {str(validations):<16}")
		console.log("Path Index: TODO ocean.dump()", color="YEL")