import os

from celerity.config import console

mock_timestamp_path = "./test/data/mock_timestamps"

def mock_timestamp():
	if os.path.getsize(mock_timestamp_path) == 0:
		raise ValueError("Mock timestamp file size empty. Not enough timestamps mocked!")

	with open(mock_timestamp_path, "r") as f:
		lines = f.readlines()
		timestamp = lines[0][:-1]
		console.log("Mock Timestamp", color="BMAG")
		console.log(timestamp)
		lines = lines[1:]
	
	lines_str =  ""
	for line in lines:
		lines_str += line
	with open(mock_timestamp_path, "w") as f:
		f.write(lines_str)
		
	return timestamp
	
def reset_mock_timestamp(number: int):
	line_list=[]
	for i in range(1000, 1000 + number):
		line_list.append(f"{float(i)}\n")
	lines = ""
	for line in line_list:
		lines += line
	with open(mock_timestamp_path, "w") as f:
		f.write(lines)