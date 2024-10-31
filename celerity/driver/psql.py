import os
import psycopg2
import datetime
from psycopg2 import sql, Error
from prizm.util.color import BLU, RED, YEL, GRE, BMAG
from prizm.util.file import path_exists
from celerity.config import console

# Database connection parameters retrieved from environment variables
db_params = {
	'dbname': os.getenv("DB_NAME"),
	'user': os.getenv("DB_USER"),
	'password': os.getenv("DB_PASSWORD"),
	'host': os.getenv("DB_HOST"),
	'port': os.getenv("DB_PORT")
}

class Postgres:
	"""
	A class to manage PostgreSQL database operations.

	Attributes:
		conn (psycopg2.connection): The connection object to the PostgreSQL database.
		cursor (psycopg2.cursor): The cursor object for executing SQL commands.
	"""

	def __init__(self, db_params=db_params) -> None:
		"""
		Initializes the Postgres class and establishes a database connection.

		Args:
			db_params (dict): Database connection parameters.
		
		Raises:
			ValueError: If the connection to the database fails.
		"""
		console.log(db_params, color="BLU")
		try:
			self.conn = psycopg2.connect(**db_params)
			self.cursor = self.conn.cursor()
			self.cursor.execute("SELECT version();")
			record = self.cursor.fetchone()
			console.log(f"You are connected to - {record}", color="GRE")
			console.log(self.conn.get_dsn_parameters(), "\n")
		except Exception:
			raise ValueError("Failed to connect")

	def close(self) -> None:
		"""Closes the database cursor and connection."""
		self.cursor.close()
		self.conn.close()

	def inject(self, base_path: str) -> None:
		"""
		Executes a schema file on the database.

		Args:
			base_path (str): The path to the schema file to be executed.

		Raises:
			ValueError: If the schema file is not found.
		"""
		try:
			schema = os.getenv("DB_SCHEMA") + base_path
			console.log("SCHEMA", color="YEL")
			console.log(schema)
			if not os.path.exists(schema):
				raise ValueError("Schema file not found!")
			with open(schema, "r") as f:
				byte_str = f.read()
			self.cursor.execute(byte_str)
			self.conn.commit()
			console.log("Schema loaded successfully!.", color="GRE")
		except Exception as e:
			console.log(f"Error: {e}", color="RED")

	def insert(self, table: str, record: dict[str, any]) -> None:
		"""
		Inserts a record into a specified table.

		Args:
			table (str): The name of the table to insert into.
			record (dict): A dictionary representing the record to be inserted.
		"""
		columns = ', '.join(record.keys())
		values = ', '.join(['%s'] * len(record))  # Placeholder for parameterized query
		sql_query = f"INSERT INTO {table} ({columns}) VALUES ({values})"
		
		try:
			self.cursor.execute(sql_query, list(record.values()))  # Execute with parameters
			self.conn.commit()  # Commit the transaction
			console.log("Record inserted successfully.", color="GRE")
		except Exception as e:
			console.log(f"Error inserting record: {e}", color="RED")
			self.conn.rollback()  # Rollback in case of error

	def all(self, table: str) -> list[dict[str, any]]:
		"""
		Fetches all records from a specified table.

		Args:
			table (str): The name of the table to fetch records from.

		Returns:
			list[dict[str, any]]: A list of dictionaries representing the records.
		"""
		sql_query = f"SELECT * FROM {table};"
		self.cursor.execute(sql_query)
		
		columns = [desc[0] for desc in self.cursor.description]  # Get column names
		records = self.cursor.fetchall()  # Fetch all records

		# Convert to a list of dictionaries
		results = [dict(zip(columns, record)) for record in records]

		return results

	def tables(self) -> list[str]:
		"""
		Retrieves a list of user tables in the database.

		Returns:
			list[str]: A list of table names.
		"""
		self.cursor.execute("SELECT schemaname, relname FROM pg_stat_user_tables;")
		vals = self.cursor.fetchall()
		tables = [val[1] for val in vals]  # Collect table names
		console.log("TABLES", color="YEL")
		for table in tables:
			console.log(f"\t{table}")
		return tables

	def update(self, json: dict[str, any], condition: str, condition_val: str) -> None:
		"""
		Updates records in specified tables based on a condition.

		Args:
			json (dict): A dictionary where keys are table names and values are dictionaries of column-value pairs.
			condition (str): The column name for the WHERE clause.
			condition_val (str): The value to match against the condition.

		"""
		with self.conn.cursor() as cursor:
			for table, record in json.items():
				attrs = record.keys()
				set_clause = ", ".join([f"{attr} = %s" for attr in attrs])
				values = list(record.values())
				table_name = sql.Identifier(table)

				update_query = sql.SQL("""
					UPDATE {} SET {}
					WHERE {} = %s
				""").format(
					table_name,
					sql.SQL(set_clause),
					sql.Identifier(condition)
				)
				
				try:
					print("\033[1;34mUpdate Query is:", update_query, "\033[0m")
					console.log("Update Query", color="YEL")
					console.log(f"{update_query}")
					cursor.execute(update_query, values + [condition_val])
					self.conn.commit()  # Commit the transaction
					console.log(f"Update on '{table}' successful", color="GRE")

				except Exception as e:
					self.conn.rollback()  # Rollback in case of error
					raise ValueError(f"\033[1;31mFailed to update record in table '{table}'\033[0m")

	def exec(self, query: str) -> None:
		"""
		Executes a raw SQL query.

		Args:
			query (str): The SQL query to be executed.

		Raises:
			IOError: If the execution of the query fails.
		"""
		try:
			self.cursor.execute(query)
			self.conn.commit()
		except Exception:
			raise IOError("Failed to execute query")

	def attrs(self, table_name: str) -> list[str]:
		"""
		Retrieves the column names for a specified table.

		Args:
			table_name (str): The name of the table.

		Returns:
			list[str]: A list of column names.
		"""
		self.cursor.execute(f"""
			SELECT column_name 
			FROM information_schema.columns 
			WHERE table_schema = 'public' AND table_name='{table_name}'
		""")
		column_names = [row[0] for row in self.cursor.fetchall()]
		console.log("Column Names", color="YEL")
		console.log(column_names)
		return column_names
	
	def find_by(self, table_: str, attr_: str, val: any) -> list[dict[str, any]]:
		"""
		Finds records in a specified table where a given attribute matches a value.

		Args:
			table_ (str): The name of the table to search in.
			attr_ (str): The attribute (column) to match against.
			val (any): The value to match.

		Returns:
			list[dict[str, any]]: A list of dictionaries representing the matching records.
		"""
		table = sql.Identifier(table_)
		attr = sql.Identifier(attr_)
		query = sql.SQL("SELECT * FROM {} WHERE {} = %s").format(table, attr)
		self.cursor.execute(query, (val,))
		result = self.cursor.fetchall()
		
		# Convert results to a list of dictionaries
		columns = [desc[0] for desc in self.cursor.description]
		records = [dict(zip(columns, record)) for record in result]
		
		return records
