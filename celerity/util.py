import uuid
import os
import hashlib
import shutil
from collections import defaultdict, deque
from celerity.config import console

def copy_directory(source, destination):
    try:
        shutil.copytree(source, destination, dirs_exist_ok=True)
        print(f"Successfully copied '{source}' to '{destination}'")
    except Exception as e:
    	console.log("Error occurred while copying directory", color="RED")

def dir_is_empty(directory):
	return not os.listdir(directory)

def str_checksum(string: str) -> str:
	# Create a SHA-256 hash object
	hash_object = hashlib.sha256()
	
	# Update the hash object with the bytes of the string
	hash_object.update(string.encode('utf-8'))
	
	# Return the hexadecimal representation of the hash
	return hash_object.hexdigest()

def file_checksum(file_path: str) -> str:
	"""Create a SHA256 checksum of a file."""
	sha256_hash = hashlib.sha256()
	with open(file_path, "rb") as f:
		for byte_block in iter(lambda: f.read(4096), b""):
			sha256_hash.update(byte_block)
	return sha256_hash.hexdigest()

def files_are_different(file1: str, file2: str) -> bool:
	"""Check if two files have different contents."""
	return file_checksum(file1) != file_checksum(file2)

def generate_uuid():
	return uuid.uuid4()


def remove_dir(directory: str, keep_base: bool = True):
	# Check if the directory exists
	if os.path.exists(directory):
		# Remove all contents of the directory
		for item in os.listdir(directory):
			item_path = os.path.join(directory, item)
			try:
				if os.path.isfile(item_path):
					os.remove(item_path)  # Remove files
				elif os.path.isdir(item_path):
					# Recursively remove contents of the directory
					remove_dir(item_path, keep_base=True)  # Keep base for recursion
					os.rmdir(item_path)  # Remove the now-empty directory
			except Exception as e:
				print(f"Error removing {item_path}: {e}")
		
		# If keep_base is False, remove the base directory itself
		if not keep_base:
			try:
				os.rmdir(directory)
			except Exception as e:
				print(f"Error removing base directory {directory}: {e}")
				
def reverse_dict(original_dict: dict[str, str]) -> dict[str, str]:
	# Create a new dictionary to hold the reversed pairs
	reversed_dict = {}

	# Iterate through the original dictionary
	for key, values in original_dict.items():
		for value in values:
			# Check if the value already exists in the new dictionary
			if value not in reversed_dict:
				reversed_dict[value] = []  # Initialize with an empty list
			reversed_dict[value].append(key)  # Append the original key
			
	return reversed_dict

def get_branch(directory: str):
	files = os.listdir(directory)
	max_stamp = -1
	for f in files:
		if float(f) > max_stamp:
			max_stamp = float(f)

	return directory + str(max_stamp) + "/"

def topological_sort(dependencies: dict[str, str]) -> list[str]:
	"""
	A directed acyclic graph containing the constraint relationships amongst collections.
	
	Args:
		dependencies (dict[str, str]): the dictionary containing the dependency relationships.
		
	Return:
		list[str]: list containing the sorted collection names
	"""	

	# Build the graph and calculate indegrees
	graph = defaultdict(list)
	indegree = defaultdict(int)

	for child, parent in dependencies.items():
		graph[parent].append(child)  # Create a directed edge from parent to child
		indegree[child] += 1         # Count incoming edges for children
		if parent not in indegree:   # Ensure parents are also included
			indegree[parent] = 0

	# Initialize queue with nodes having no incoming edges (parents)
	zero_indegree = deque([node for node in indegree if indegree[node] == 0])

	sorted_order = []

	while zero_indegree:
		node = zero_indegree.popleft()
		sorted_order.append(node)

		# Decrease the indegree of each child
		for child in graph[node]:
			indegree[child] -= 1
			if indegree[child] == 0:
				zero_indegree.append(child)

	# Check for cycles
	if len(sorted_order) != len(indegree):
		raise ValueError("The dependency graph has at least one cycle.")

	return sorted_order

def next_char(char, increment=1):
	# Check if the input is a single character
	if len(char) != 1:
		raise ValueError("Input must be a single character.")
	
	# Increment the character by converting to ASCII and back
	new_char = chr(ord(char) + increment)
	return new_char