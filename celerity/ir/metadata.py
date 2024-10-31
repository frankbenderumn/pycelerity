import time
import os
import json

from celerity.test.mocker import mock_timestamp
from celerity.util import reverse_dict, file_checksum, str_checksum
from celerity.config import console

def validated_property(attr_name=None):
    def decorator(func):
        private_name = f'_{attr_name or func.__name__}'

        @property
        def prop(self):
            return getattr(self, private_name, None)

        @prop.setter
        def prop(self, value):
            if value is None:
                raise ValueError(f"Trying to set {attr_name or func.__name__} to None")
            setattr(self, private_name, value)

        return prop

    return decorator

class Metadata:
	
	def load(self):
		"""
		Loads the metadata from the previous set of directories (old)
		"""
		if self.gate == "new":
			raise ValueError("Trying to override new metadata with the old metadata")

		path = self.directories.get("output") + "metadata.lock"
		if os.path.exists(path):
			if path is not None:
				with open(path, "r") as f:
					self._metadata = json.load(f)

			self.path_index = self._metadata.get("path_index")
			self.history = self._metadata.get("history")
			self.id = self._metadata.get("id")
			self._history.append(self.id)
			self._school_checksums = self._metadata.get("school_checksums")
			
		else:
			self.path_index = {}
			self.history = []
			if os.getenv("CELERITY_ENV") == "test":
				self.id = mock_timestamp()
			else:
				self.id = str(time.time() * 1000)
			self._school_checksums = {}
			# raise ValueError(f"Metadata path '{path}' does not exist!")

	def __init__(self, directories: dict[str, str], gate: str):
		self.gate = gate		

		self.directories = directories
		
		self._metadata = {}

		# Indices to help search and manipulate metadata
		# and detect move operation
		self._path_index: dict[str, str] = None
		self._school_index: dict[str, str] = None
		
		# For detecting updation
		self._school_checksums: dict[str, str] = {}
		
		# Metadata ID generation
		self._id = None
		self._history = []
		
		if self.gate == "new":
			if os.getenv("CELERITY_ENV") == "test":
				self._id = mock_timestamp()
			else:
				self._id = str(time.time() * 1000)
			
	@property # Use when validation desired
	def path_index(self):
		if self._path_index is None:
			raise ValueError("Path Index not set in metadata!")

		return self._path_index
	
	@validated_property("id")
	def id(self):
		return self._id

	def paths(self):
		return list(set(self._path_index.keys()))
	
	@property
	def history(self):
		return self._history

	@history.setter
	def history(self, history):
		self._history = history
		console.log(self._history)

	@property
	def school_index(self):
		return self._school_index
	
	def school_names(self):
		if not isinstance(self._school_index, dict):
			raise ValueError("Meta school index not of type dict")
		
		return list(self._school_index.keys())
	
	@path_index.setter
	def path_index(self, index):
		if index is None:
			raise ValueError("Setting Path index to None")		

		self._path_index = index
		self._school_index = reverse_dict(self._path_index)
		self._school_names = list(set(self._school_index.keys()))

	def ir(self):
		"""
		Note: Metada
		"""
		
		# Generate directory tree structure indices and checksums
		checksums = {}
		new_path_index = {}
		for path, val in self.path_index.items():
			checksums[os.path.abspath(path)] = file_checksum(path)
			new_path_index[os.path.abspath(path)] = val
		self.path_index = new_path_index
		
		# The Metadata object
		self._metadata = {
			"id": self._id,
			"path_index": self.path_index,
			"checksums": checksums,
			"schools": self.school_names(),
			"history": self.history,
			"school_index": self._school_index,
			"school_checksums": self.school_checksums
		}
		
		return self._metadata
	
	def __and__(self, old_metadata):
		self._history = old_metadata.history

	@property
	def school_checksums(self):
		return self._school_checksums

	@school_checksums.setter
	def school_checksums(self, schools_script):
		console.log(schools_script, color="RED")
		if schools_script == {} and schools_script is None:
			raise ValueError("Taking schools checksums of congregation that does not exist!")
		for school_name, school_fish in schools_script.items():
			self._school_checksums[school_name] = str_checksum(str(school_fish))
		console.log(self._school_checksums, color="RED")