import os
import json
from celerity.config import console
from celerity.delta.delta import delta_transpile
from celerity.ir.ocean import Ocean

def transpile(directories: dict[str, str], format_type="psql", directories_b: dict[str, str] = None) -> int:
	"""
	Primary transpilation function to convert directories to an 
		intermediate representation (IR), then serialize IR into a 
		schema for the provided database type.
		
	Args:
		directories (dict[str, str]): Dictionary containing the three 
			directories: input directory, output directory, and delta 
			directory
			
	Return:
		int: returns 0 if successful
	"""
	ocean: Ocean = Ocean(directories, format_type, directories_b)
		
	try:
		
		console.log(f"{'-' * 100}SERIALIZING OCEAN{'-' * 100}", color="BMAG")
		ocean.serialize()
		console.log(f"{'=' * 100}OCEAN SERIALIZED{'=' * 100}", color="BGRE")
	
	except Exception as e:
		raise ValueError(f"\033[1;31mError: \033[0mFailed to serialize IR" +
			f" tables. \033[1;34mInfo: \033[0m{e}")
		
	console.log(f"{'-' * 100}LOADING DELTA{'-' * 100}", color="BMAG")
	if delta_transpile(ocean):
		console.log(f"{'=' * 100}DELTA RAN{'=' * 100}", color="BGRE")

		console.log(f"{'-' * 100}PERSISTING OCEAN{'-' * 100}", color="BMAG")
		ocean.persist()
		console.log(f"{'=' * 100}OCEAN PERSISTED{'=' * 100}", color="BGRE")

	else:
		console.log(f"{'=' * 100}DELTA RAN{'=' * 100}", color="BGRE")
		console.log("Schema staying the same", color="GRE")
	
	console.log(f"{'=' * 100}Terminated Gracefully{'=' * 100}", color="BGRE")
	return 0