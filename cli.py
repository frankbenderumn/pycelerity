import os
import sys

from celerity.config import console
from celerity.celerity import Celerity

if __name__ == "__main__":
	
	argc: int = len(sys.argv)
	
	if argc < 2:
		raise ValueError(
			"\n\n\033[1;31mError: \033[0mAt least one " +
			"argument required. Use celerity help for more options!"
		)

	console.terminal = bool(os.getenv("CELERITY_CONSOLE"))
	
	directories: dict[str, str] = {
		"input": os.getenv("DB_MIGRATION"),
		"output": os.getenv("DB_SCHEMA"),
		"rollback": os.getenv("CELERITY_ROLLBACK_DIR")
	}

	format_type = os.getenv("CELERITY_DB_TYPE")

	celerity = Celerity(directories, format_type)

	command: str = sys.argv[1]
	
	if command == "help":
		
		print("\033[1;36m============================================\033[0m")
		print("\033[1;36m              Celerity CLI")
		print("\033[1;36m============================================\033[0m")
		print("migrate:")
		print("destroy:")
		print("recover:")
		print("rollback:")
		print("commit: TODO")
		print("commits: TODO")

	elif command == "migrate":
		
		celerity.migrate()

	elif command == "destroy":
		
		to_destroy = input(
			"Are you sure? This action is " +
			"\033[1;31mIrreversible\033[0m and will destroy all " +
			"schools. [y/n]: "
		)
		if to_destroy.lower() == "y":
			celerity.destroy()

	elif command == "recover":
		
		celerity.recover()
				
	elif command == "rollback":

		pass

	else:
		
		raise ValueError(
			"\n\n\033[1;31mError: \033[0mInvalid " +
			f"command '{command}' provided!"
		)
	