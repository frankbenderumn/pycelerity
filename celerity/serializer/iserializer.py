from abc import ABC, abstractmethod
from celerity.ir.fish import Fish
from celerity.ir.school import School
from celerity.ir.congregation import Congregation

class ISerializer(ABC):
	
	def __init__(self, type_map=None):
		if type_map is None:
			raise TypeError("\033[1;31mError: \033[0mNo type map provided for schema")
		self.type_map = type_map
	
	@abstractmethod
	def data_type(self, attr: Fish):
		"""Serializes the datatype to the required format
		
		Args:
			attr (Attr): Attribute module to house attribute state information
		"""
		pass
		
	@abstractmethod
	def serialize_fish_constraints(self, fish_str: str, fish: Fish):
		"""
		Appends any extra validations in attribute to the serialized attribute string attr_str
		
		Args:
			fish_str (str): The partially serialized attribute string
			fish (Fish): Attribute module to house attribute state information
		"""
		pass
	
	@abstractmethod
	def serialize_fish(self, fish_name: str, fish: Fish):
		"""
		Primary serialization function aimed at serializing all collections
		
		Args:
			school_name (str): Name of the collection/school/table to serialize
			school_attrs (dict): A series of constraints to limit data in school

		"""
		pass

	@abstractmethod
	def serialize_school(self, school_name: str, school: School):
		"""
		Primary serialization function aimed at serializing all collections
		
		Args:
			school_name (str): Name of the collection/school/table to serialize
			school_attrs (dict): A series of constraints to limit data in school

		"""
		pass
		
	@abstractmethod
	def serialize_congregation(self, congregation: Congregation) -> str:
		"""
		Speciic to serializing a table/collection/hub
		
		meta_schema (MetaSchema): A compositional class containing the 
			sorted tables to be serialized
		"""
		pass