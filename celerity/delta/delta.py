import os
import json

# 72 docstring

# 79 code

# In theory this file should not have any file reading
# File reading should be taken care of elsewhere (in the class), separation of concerns

from celerity.config import console
from prizm.util.file import path_exists
from prizm.util.color import BYEL, RED, MAG, BLU, YEL
from celerity.ir.ocean import Ocean
from celerity.util import str_checksum, file_checksum, get_branch
from celerity.delta_serializer.psql_delta import PostgresDelta
from celerity.ir.school import School
from celerity.updater.school_updater import SchoolUpdater
from celerity.updater.updater import Updater

def delta_creation(new_schools, old_schools, ocean, delta_serializer) -> str:
	# Creation logic
	creations = list(set(new_schools) - set(old_schools))
	console.log("\tDetected Creations", color="YEL")
	console.log(f"\t\t{creations}")
	delta_creations = ""
	if creations != []:
		# ocean.commit_metadata()
		console.log(f"\t{creations}")
		creation_tables = {}
		for school_name, school_attrs in ocean.congregation_b.schools_script.items():
			if school_name in creations:
				creation_tables[school_name] = school_attrs
		delta_creations = delta_serializer.create(creation_tables)
	return delta_creations
			
def delta_deletion(new_schools, old_schools, delta_serializer) -> str:
	# Deletion Logic
	deletions = list(set(old_schools) - set(new_schools))
	console.log("\tDetected Deletions", color="YEL")
	console.log(f"\t\t{deletions}")
	delta_deletions = ""
	if deletions != []:
		# ocean.commit_metadata()
		console.log(f"\t{deletions}")
		delta_deletions = delta_serializer.delete(deletions)
	return delta_deletions

def delta_alteration() -> str:
	pass

def delta_assemble(assembler: dict[str, any]) -> str:
	delta_str = ""
	delta_str += assembler["creation"]
	delta_str += assembler["deletion"]
	for deletes in assembler["constraint"]["deletion"]:
		delta_str += deletes
	for creates in assembler["constraint"]["creation"]:
		delta_str += creates
	for updates in assembler["constraint"]["updation"]:
		delta_str += updates

	return delta_str

def delta_transpile(ocean: Ocean) -> bool:
	"""
	Generates a delta representation of schema updates to be made.
		Main meta schema file named 'meta_schema.lock', while schema 
		file named 'schema.lock'
	 
	
	Args:
		directories (dict[str, str]): Dictionary containing the three 
			directories: input directory, output directory, and delta 
			directory
	"""
	ocean.changed = False

	""
	old_metadata_path = ocean.directories_a["output"] + "metadata.lock"
	old_schema_path = ocean.directories_a["output"] + "schema.lock"
	old_composite_path = ocean.directories_a["output"] + "composite.lock"
	
	if not os.path.exists(old_schema_path) or not os.path.exists(old_metadata_path):
		ocean.changed = True
		return ocean.changed
	
	with open(old_schema_path, "r") as f:
		old_schema = f.read()
		
	with open(old_metadata_path, "r") as f:
		old_metadata = json.load(f)
		
	with open(old_composite_path, "r") as f:
		old_composite = json.load(f)
		
	new_schema = ocean.serialized_congregation
	new_metadata = ocean.new_metadata().ir()
	

	# delta functionality only trigger if checksums of raw schema are different
	if str_checksum(str(old_schema)) != str_checksum(str(ocean.serialized_congregation)):
		# Consider use case where table is modified in a different file (entirely moved)

		assembler = {
			"creation": "",
			"deletion": "",
			"constraint": {
				"creation": {},
				"deletion": {},
				"alteration": {}
			}	
		}

		console.log("Schema checksum files are not the same", color="YEL")
		
		if ocean.format_type == "psql" or ocean.format_type == "postgres":
			delta_serializer = PostgresDelta(ocean.directories_a, ocean) # FIXME
		
		# Need to handle use case for Creation, Updation, Deletion, and Move
		
		# Creation can be verified by ascertaining the tables/schools found includes
		# more than the old schools
		
		# School comparison
		old_schools = ocean.old_metadata().school_names()
		console.log("\tOld schools", color="YEL")
		console.log(f"\t\t{old_schools}")
		new_schools = ocean.new_metadata().school_names()
		console.log("\tNew Schools", color="YEL")
		console.log(f"\t\t{new_schools}")
		
		ocean.commit_metadata()
		
		# Creation logic
		assembler["creation"] = delta_creation(new_schools, old_schools, ocean, delta_serializer)
			
		# Deletion Logic
		deletions = list(set(old_schools) - set(new_schools))
		assembler["deletion"] = delta_deletion(new_schools, old_schools, delta_serializer)

		# Use checksum to detect Update or Move function
		old_checksums = ocean.old_metadata().school_checksums
		new_checksums = ocean.new_metadata().school_checksums

		intersection_keys = old_checksums.keys() & new_checksums.keys()

		console.log("Old checksums", color="YEL")
		console.log(old_checksums)
		console.log("New checksums", color="YEL")
		console.log(new_checksums)
		console.log("Same schools", color="YEL")
		console.log(list(intersection_keys))

		################################################################
		# UPDATION LOGIC
		################################################################		

		# use self.path_index matching to identify move operation
		to_cross_reference = []
		for key in intersection_keys:
			if old_checksums[key] != new_checksums[key]:
				to_cross_reference.append(key)

		console.log("Cross Reference", color="YEL")
		console.log(to_cross_reference)

		updated_resolution = ""

		if to_cross_reference != []:
			
			# Move operation logic
			move_gate = False
			for cr in to_cross_reference:
				if new_metadata.get("path_index").get(cr) != old_metadata.get("path_index").get(cr):
					console.log("Move operation detected", color="BLU")

			if not move_gate:
				console.log("No move detected", color="GRE")

			schools_to_review = to_cross_reference

			composite_path = ocean.directories_a["rollback"] + old_metadata.get("id") + "/composite.lock"
			
			with open(composite_path, "r") as f:
				old_ir = json.load(f)
				
			old_ir = ocean.congregation_a.ir()
			new_ir = ocean.congregation_b.ir()
			
			console.log(old_ir, color="MAG")
			console.log(new_ir, color="RED")
			
			if old_ir != {} and new_ir != {}: # If either of these are empty, then this is a new schema
				for review in schools_to_review:					
					school_updater = Updater(School(review, old_ir.get(review)), School(review, new_ir.get(review)))
					school_updater.update()
					updated_resolution = school_updater.resolve(ocean.format_type)

		else:
			console.log("No alteration detected", color="GRE")

		delta_str = ""
		delta_str += assembler["deletion"]
		delta_str += assembler["creation"]
		for deletes in assembler["constraint"]["deletion"]:
			delta_str += deletes
		for creates in assembler["constraint"]["creation"]:
			delta_str += creates
		for updates in assembler["constraint"]["alteration"]:
			delta_str += updates

		ocean.serialized_delta = delta_str + updated_resolution

		ocean.changed = True # TODO: Pruneable ?
		
	else:

		ocean.changed = False # TODO: Pruneable ?
		
	return ocean.changed