from celerity.delta.idelta import DeltaType, CollectionType, DeltaDimType
from celerity.config import console
from celerity.serializers import serializers
from celerity.delta.delta_node import DeltaNode

# TODO: add school-fish id to school-fish-constraint id to congre... etc.
# All keys need to be unique

# def alter_ocean():
# 	pass

# def alter_congregation():
# 	pass

# def alter_school():
# 	pass

# def alter_fish():
# 	pass

# def alter_constraint():
# 	pass

# delta_serializers = {
# 	CollectionType.OCEAN: alter_ocean,
# 	CollectionType.CONGREGATION: alter_congregation,
# 	CollectionType.SCHOOL: alter_school,
# 	CollectionType.FISH: alter_fish,
# 	CollectionType.CONSTRAINT: alter_constraint
# }

class DeltaTree:
	def _reverse_edges(self):
		# Original hash table
		# hash_table = {
		# 	"__root__": ['table', 'table'],
		# 	"table": ['addedattr', 'jose', 'wellthen', 'name', 'something', 'checkurslef', 'boolean'],
		# 	"wellthen": ['default', 'limit'],
		# 	"name": ['limit'],
		# 	"something": ['default'],
		# 	"checkurslef": ['default'],
		# 	"boolean": ['limit', 'default', 'type']
		# }

		# Iterate through the original hash table
		for key, values in self.edges.items():
			for value in values:
				# If the value is not already a key in the reversed table, initialize it
				if value not in self.reversed_edges:
					self.reversed_edges[value] = []
				# Append the current key to the list of keys for this value
				self.reversed_edges[value].append(key)

		# Print the reversed hash table
		print(self.reversed_edges)
	
	def _collectionize(self):
		for k, v in self.nodes.items():
			self.collection_map[k] = v.collection_type

	def _is_root_child(self, collection_type_new: CollectionType):	
		return self.root_scope.value + 1 == collection_type_new.value

	def __init__(self, name, collection_scope: CollectionType):
		self.root = DeltaNode("__root__", DeltaType.ROOT, collection_scope, None)
		self.root_scope = collection_scope
		self.name = name
		self.nodes = {}
		self.edges = {}
		self.leaves = {}
		self.nodes["__root__"] = self.root
		self.reversed_edges = {}
		self.collection_map = {}
		
	def addNode(self, parent, id, delta_type: DeltaType, collection_type: CollectionType, data, terminal = False):		
		delta_node = DeltaNode(data.id, delta_type, collection_type, data, terminal)
		self.nodes[data.id] = delta_node
			
		if self._is_root_child(collection_type):
			self.edges["__root__"] = [data.id] # Will likely not work with multiple tables

		else:
			console.log(self.edges)
			if self.edges.get(parent) is None:
				self.edges[parent] = [data.id]
			else:
				self.edges[parent].append(data.id)
				
			console.log(self.edges, color="RED")
	
	def dump(self):
		for node_id, node in self.nodes.items():
			console.log(f"Node Parent: {node_id}", color="YEL")
			console.log(node)
			node.dump()
		console.log("Edges", color="YEL")
		for k, v in self.edges.items():
			console.log(f"\t{k}: {v}")

	def traverse_level(self, result, chain, key, serializer):
		# chain.append((key, self.nodes.get(key).collection_type))
		root_children = sorted(self.edges.get(key))
		for child in root_children:
			console.log(f"{'\t' * (len(chain))}chain: {chain}", color="CYA")
			console.log(f"{'\t' * (len(chain))}children: {root_children}", color="YEL")
			node_obj = self.nodes.get(child)
			console.log(node_obj, color="RED")
			console.log(f"{'\t' * (len(chain) + 1)}node: {node_obj.id}", node_obj)
			node_obj.dump()
			if node_obj.terminal:
				console.log(f"Node {node_obj.id} is terminal", color="GRE")
				passed_chain = [(node_obj.id, node_obj.collection_type)]
				key = node_obj.id
				while self.reversed_edges.get(key) is not None: # cycle prevention will be needed in future
					parent = self.nodes.get(self.reversed_edges.get(key)[0]) # FIXME: This should not be a list
					passed_chain.append((parent.id, parent.collection_type))
					key = parent.id
				result.result_str += serializer.serialize_alter(node_obj, passed_chain)
				console.log(result.result_str, color="CYA")
			else:
				console.log(f"{node_obj.id} is not terminal")
				self.traverse_level(result, chain, child, serializer)

	def serialize(self, format_type):
		self.nodes = {key: self.nodes[key] for key in sorted(self.nodes)}
		self.edges = {key: self.edges[key] for key in sorted(self.edges)}

		with open("./test/data/log/delta_tree_serializer.txt", "a") as f:
			f.write(str(list(self.nodes.keys())) + "\n")		


		with open("./test/data/log/delta_tree_serializer.txt", "a") as f:
			f.write(str(list(self.edges.keys())) + "\n")		

		cursor_type = CollectionType(self.root_scope.value + 1)
		self._reverse_edges()
		self._collectionize()
		chain = []
		class StrRef:
			def __init__(self, result_str):
				self.result_str = result_str
		result = StrRef("")
		serializer = serializers.get(format_type)
		self.traverse_level(result, self.reversed_edges, "__root__", serializer)
		console.log(result.result_str, color="GRE")
		return result.result_str

					# node_children = self.edges.get(child)
					# console.log(f"\t\tchildren: {node_children}", color="YEL")
					# for node in node_children:
					# 	node_objs = self.nodes.get(node)
					# 	console.log(node_objs)

		# for k, schools in resolution.items(): # school level
		# 	console.log(f"School: {k}", color="YEL")
		# 	if k == "school-duals":
		# 		for fish in schools:
		# 			console.log(f"Fish: {k}", color="YEL")
		# 			if fish["fish-duals"] != []:
		# 				for constraint in fish["fish-duals"]:
		# 					console.log("constraint", color="YEL")
		# 					console.log(constraint)
		# 			elif fish["fish-singles"] != {}:
		# 				tfish = fish["fish-singles"]
		# 				for k, v in tfish.items():
		# 					console.log(v.data, color="GRE")
		# 					some_str = serializers.get(format_type).serialize_alter(v)
		# 					console.log(some_str, color="BLU")
		# 					pass							
		# 	elif k == "school-singles" != {}:
		# 		pass