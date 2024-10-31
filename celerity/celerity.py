"""
Author: Frank Bender
Email: fjbender2@gmail.com
Date: October 9th, 2024
"""

import os
import stat

from celerity.transpile import transpile
from celerity.util import remove_dir, get_branch
from celerity.config import console
from celerity.ir.ocean import Ocean
from celerity.delta.delta import delta_transpile

class Celerity:
	"""
	Main class interface to manage data manipulation, storage, drivers,
	and transpilations.
	
	Attributes:
		directories (dict[str, str]): Paths where files and schemas 
			will be loaded and stored.
			
		format_type (str): Specific database to transpile and store 
			for, e.g., PostgreSQL, MongoDB, etc.
	"""
		
	def _verify_dirs(self, directories: dict[str, str]):
		# List of required keys that must be present in the directories 
		# dictionary
		required_keys = ["input", "output", "rollback"]
		for key in required_keys:
			if directories.get(key) is None:
				raise ValueError(f"\n\n\033[1;31mError: Directory path"
					+ " '{key}' not provided. This is required!\033[0m"
				)
		
		# Create necessary directories if they don't already exist
		for directory in directories.values():
			os.makedirs(os.path.dirname(directory), exist_ok=True)

	def __init__(self, directories: dict[str, str], format_type: str, phase: str = "a"):
		"""
		Initializes the Celerity class with specified directories and 
			format type.

		Parameters:
			directories (dict[str, str]): A dictionary containing paths 
				for input, output, and rollback directories.
				
			format_type (str): The target database format for 
				transpilation.

			_test_directories (dict[str, str]): A dictionary of paths 
				to data for comaprison to verify correctness
				
		Raises:
			ValueError: If any required directory path 
				('input', 'output', 'rollback') is not provided.

		Creates the necessary directories if they do not exist.
		"""
		self._verify_dirs(directories)
		self.directories = directories # Can probably delete
		self.format_type = format_type
		self._test_directories = None
		self.phases = {phase: self.directories}

	def migrate(self, start_phase="a", end_phase=None):
		"""
		Transpiles data from the input directory to the specified format type.

		Raises:
			ValueError: If there is a problem during the transpilation process.
		"""
		if self.phases.get(start_phase) is None:
			raise ValueError(f"Cannot transpile for phase '{start_phase}'.")

		if end_phase is not None:
			if self.phases.get(end_phase) is None:
				raise ValueError(f"Cannot transpile for phase '{end_phase}'.")

			if transpile(self.phases.get(start_phase), self.format_type, self.phases.get(end_phase)):
				raise ValueError(f"Problem transpiling for format_type '{self.format_type}'.")
		else:
			if transpile(self.phases.get(start_phase), self.format_type):
				raise ValueError(f"Problem transpiling for format_type '{self.format_type}'.")			

	def destroy(self, flag=None):
		"""
		Prompts the user for confirmation to destroy all data in the rollback 
		and output directories.

		If confirmed, removes the contents of the rollback and output directories.

		Parameters:
			flag (optional): Additional flag for conditional destruction (not used).
		"""

		# Remove the rollback and output directories
		remove_dir(self.directories["rollback"])
		remove_dir(self.directories["output"])
	
	def recover(self, commit=None):
		"""
		Recovers the latest schema and metadata from the rollback directory 
		and writes them back to the output directory.

		The method sets the permissions for the lock files to allow reading 
		and writing, then restores the files from the recovery directory.

		Parameters:
			commit (optional): An optional commit parameter (not used).
		"""
		recovery_dir = get_branch(self.directories["rollback"])  # Get the path for recovery
		output_dir = self.directories["output"]  # Output directory path
		
		# Paths for lock files in the output directory
		output_schema_path = output_dir + "schema.lock"
		output_metadata_path = output_dir + "metadata.lock"
		output_composite_path = output_dir + "composite.lock"

		# Change permissions to allow read and write access
		os.chmod(output_schema_path, stat.S_IREAD | stat.S_IWRITE)
		os.chmod(output_metadata_path, stat.S_IREAD | stat.S_IWRITE)
		os.chmod(output_composite_path, stat.S_IREAD | stat.S_IWRITE)
		
		# Read and write the schema lock file
		with open(recovery_dir + "schema.lock", "r") as f:
			delta_schema = f.read()  # Read schema data

		with open(output_schema_path, "w") as f:
			f.write(delta_schema)  # Write to output schema lock file
			
		# Read and write the metadata lock file
		with open(recovery_dir + "metadata.lock", "r") as f:
			delta_metadata = f.read()  # Read metadata data
			
		with open(output_metadata_path, "w") as f:
			f.write(delta_metadata)  # Write to output metadata lock file
			
		# Read and write the composite lock file
		with open(recovery_dir + "composite.lock", "r") as f:
			delta_composite = f.read()  # Read composite data
			
		with open(output_composite_path, "w") as f:
			f.write(delta_composite)  # Write to output composite lock file

		# Restore permissions to read-only for the lock files
		os.chmod(output_schema_path, stat.S_IREAD)
		os.chmod(output_metadata_path, stat.S_IREAD)
		os.chmod(output_composite_path, stat.S_IREAD)

	def commit(self):
		"""
		Placeholder for the commit method.
		
		This method is intended to handle committing changes, but is currently not implemented.
		"""
		pass
	
	def commits(self):
		"""
		Placeholder for the commits method.
		
		This method is intended to handle multiple commits or related functionality, but is currently not implemented.
		"""
		pass
		
	def set_phase(self, phase_label: str, phase_directories):
		self._verify_dirs(phase_directories)
		self.phases[phase_label] = phase_directories
		
	def generate_phase(self, directory, phase: str):
		phase_dir = {
			"input": directory + f"{phase}/input/",
			"output": directory + f"{phase}/output/",	
			"rollback": directory + f"{phase}/rollback/"	
		}
		self.set_phase(phase, phase_dir)
		
	def generate_sim(self, directory, phases):
		sim_directory = directory + "sim/"
		truth_directory = directory + "truth/"
		for phase in phases:
			self.generate_phase(sim_directory, phase)
			self._verify_dirs(
				{
					"input": truth_directory + f"{phase}/input/",
					"output": truth_directory + f"{phase}/output/",	
					"rollback": truth_directory + f"{phase}/rollback/"	
				}
			)
	
	def run_test(self, gate: str = "", start_phase: str = "a", end_phase: str = "z", mockstamp: str = None) -> bool:
		if self.phases.get(end_phase) is None:
			raise ValueError("Test directories are not set")

		output_a = self.phases[start_phase]["output"]
		output_b = self.phases[end_phase]["output"]
		
		if mockstamp is not None:
			output_a = f"./test/data/updation/{mockstamp}/sim/{end_phase}/output/"
			output_b = f"./test/data/updation/{mockstamp}/truth/{end_phase}/output/"
		
		if gate == "schema":
			with open(output_a + "schema.lock", "r") as f:
				pre_schema = f.read()
			with open(output_b + "schema.lock", "r") as f:
				post_schema = f.read()
			return pre_schema == post_schema
	
		elif gate == "composite":
			with open(output_a + "metadata.lock", "r") as f:
				pre_schema = f.read()
			with open(output_b + "metadata.lock", "r") as f:
				post_schema = f.read()
			return pre_schema == post_schema
		
		elif gate == "metadata":
			with open(output_a + "metadata.lock", "r") as f:
				pre_schema = f.read()
			with open(output_b + "metadata.lock", "r") as f:
				post_schema = f.read()
			return pre_schema, post_schema			
			
		elif gate == "rollback":
			console.log("May be tricky to test currenty with timestamps being generated")

	def delta_test(self, start_phase: str = "a", delta_phase: str = "b"):
		# ocean: Ocean = Ocean(self.phases.get(start_phase), self.format_type)
		ocean2: Ocean = Ocean(self.phases.get(delta_phase), self.format_type)
			
		try:
			# ocean.serialize()
			ocean2.serialize()
		
		except Exception as e:
			raise ValueError(f"\033[1;31mError: \033[0mFailed to serialize IR" +
				f" tables. \033[1;34mInfo: \033[0m{e}")
		
		if delta_transpile(self.phases.get(start_phase), ocean2):
			console.log("Test delta change detected", color="GRE");
		else:
			pass

		return False

	def inject(self):
		# conn = Postgres()

		# conn.inject("schema.lock")

		# tables = conn.tables()
		# console.log(tables, color="BLU")

		# attrs = conn.attrs("user")
		# console.log(tables, color="RED")
		pass
