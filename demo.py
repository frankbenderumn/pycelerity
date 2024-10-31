from celerity.celerity import Celerity

if __name__ == "__main__":
	
	directories = {
		"input": "./data/demo/input/",
		"output": "./data/demo/output/",
		"rollback": "./data/demo/rollback/"
	}

	celerity = Celerity(directories, format_type="psql")
	
	celerity.migrate()