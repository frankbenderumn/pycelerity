import os
import json

from celerity.ir.school import School
from celerity.config import console
from celerity.updater.updateable import Updateable
from celerity.delta.idelta import CollectionType

class Congregation(Updateable):

	def _load(self, schools_script): # HACK
		if schools_script != {}:
			for school_name, school in schools_script.items():
				s = School(school_name, school)
				self.schools[school_name] = s
				
	def load(self, directories: str, gate: str = "old"): # HACK # FIXME
		old_composite_path = directories["output"] + "composite.lock"
		if os.path.exists(old_composite_path):
			with open(old_composite_path, "r") as f:
				json_data = json.load(f)	
			for school_name, school in json_data.items():
				s = School(school_name, school)
				self.schools[school_name] = s
			self.schools_script = json_data

	def __init__(self, schools_script={}):
		self.schools_script = schools_script
		self.name: str = "schema"
		self.schools: dict[str, School] = {}
		self._load(schools_script)
		super().__init__(CollectionType.CONGREGATION)
		
	def ir(self):
		return self.schools_script