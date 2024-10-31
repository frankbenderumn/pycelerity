import pytest

from celerity.celerity import Celerity
from celerity.util import dir_is_empty, remove_dir
from celerity.test.mocker import reset_mock_timestamp
from celerity.config import console

@pytest.fixture
def assert_with_msg():
	def _assert(condition, message):
		if not condition:
			print(f"Assertion failed: {message}")
		assert condition  # This will raise the assertion error if the condition is False
	return _assert

@pytest.fixture
def fixture(request, scope='module'):
	case = request.param
	
	# Setup code
	directories = {
		"input": f"./test/data/updation/{case}/sim/a/input/",
		"output": f"./test/data/updation/{case}/sim/a/output/",
		"rollback": f"./test/data/updation/{case}/sim/a/rollback/"
	}

	remove_dir(directories["rollback"])
	remove_dir(directories["output"])

	mid_directories = {
		"input": f"./test/data/updation/{case}/sim/b/input/",
		"output": f"./test/data/updation/{case}/sim/b/output/",
		"rollback": f"./test/data/updation/{case}/sim/b/rollback/"
	}

	post_directories = {
		"input": f"./test/data/updation/{case}/sim/z/input/",
		"output": f"./test/data/updation/{case}/sim/z/output/",
		"rollback": f"./test/data/updation/{case}/sim/z/rollback/"
	}

	format_type = "psql"

	celerity = Celerity(directories, format_type)
	celerity.set_phase("b", mid_directories)
	celerity.set_phase("z", post_directories)

	yield celerity
	
	def cleanup():
		pass

	request.addfinalizer(cleanup)

# This test is broken
# @pytest.mark.parametrize('fixture', ['case2'], indirect=True)
# def test_verify_metadata_phase_chain(fixture, assert_with_msg):
# 	reset_mock_timestamp(1000)
# 	celerity = fixture
# 	celerity.migrate()
# 	a, z = celerity.run_test("metadata")
# 	if a != z:
# 		pytest.fail(f"Assertion Error: \nActual:\n{a}\n\nExpected:\n{z}")
		
@pytest.mark.parametrize('fixture', ['case3'], indirect=True)
def test_verify_multiple_metadata_phase_chain(fixture, assert_with_msg):
	console.terminal = True	

	reset_mock_timestamp(1000)
	celerity = fixture
	celerity.generate_sim("./test/data/updation/case3/", ["a", "b", "c", "d", "e", "z"])
	celerity.migrate()
	
	celerity.migrate("a", "b")
	y, z = celerity.run_test("metadata", "a", "b", mockstamp="case3")
	if y != z:
		pytest.fail(f"Assertion Error: \nActual:\n{y}\n\nExpected:\n{z}")

	celerity.migrate("b", "c")
	y, z = celerity.run_test("metadata", "b", "c", mockstamp="case3")
	if y != z:
		pytest.fail(f"Assertion Error: \nActual:\n{y}\n\nExpected:\n{z}")

	celerity.migrate("c", "d")
	y, z = celerity.run_test("metadata", "b", "c", mockstamp="case3")
	if y != z:
		pytest.fail(f"Assertion Error: \nActual:\n{y}\n\nExpected:\n{z}")

	celerity.migrate("d", "e")
	y, z = celerity.run_test("metadata", "d", "e", mockstamp="case3")
	if y != z:
		pytest.fail(f"Assertion Error: \nActual:\n{y}\n\nExpected:\n{z}")

	celerity.migrate("e", "z")
	y, z = celerity.run_test("metadata", "e", "z", mockstamp="case3")
	if y != z:
		pytest.fail(f"Assertion Error: \nActual:\n{y}\n\nExpected:\n{z}")

	assert celerity.run_test("schema", "a", "b", mockstamp="case3") == True
	assert celerity.run_test("schema", "b", "c", mockstamp="case3") == True
	assert celerity.run_test("schema", "c", "d", mockstamp="case3") == True
	assert celerity.run_test("schema", "d", "e", mockstamp="case3") == True
	assert celerity.run_test("schema", "e", "z", mockstamp="case3") == True

@pytest.mark.parametrize('fixture', ['case4'], indirect=True)
def test_table_creation_phase_chain(fixture, assert_with_msg):
	reset_mock_timestamp(1000)
	celerity = fixture
	celerity.generate_sim("./test/data/updation/case4/", ["a", "b", "z"])
	celerity.migrate()
	celerity.migrate("a", "b")
	assert celerity.run_test("schema", "a", "b", mockstamp="case4") == True
	celerity.migrate("b", "z")
	assert celerity.run_test("schema", "b", "z", mockstamp="case4") == True

@pytest.mark.parametrize('fixture', ['case5'], indirect=True)
def test_table_update_phase_chain(fixture, assert_with_msg):
	reset_mock_timestamp(1000)
	celerity = fixture
	celerity.generate_sim("./test/data/updation/case5/", ["a", "b", "z"])
	celerity.migrate()
	celerity.migrate("a", "b")
	assert celerity.run_test("schema", "a", "b", mockstamp="case5") == True
	# celerity.migrate("b", "z")
	# assert celerity.run_test("schema", "b", "z", mockstamp="case5") == True

# @pytest.mark.parametrize('fixture', ['case6'], indirect=True)
# def test_table_update_no_phase(fixture, assert_with_msg):
# 	assert True == True
# 	reset_mock_timestamp(1000)
# 	celerity = fixture
# 	celerity.generate_sim("./test/data/updation/case6/", ["a", "b", "z"])
# 	celerity.migrate()
	# celerity.migrate("a", "b")
	# assert celerity.run_test("schema", "a", "b", mockstamp="case5") == True
	# celerity.migrate("b", "z")
	# assert celerity.run_test("schema", "b", "z", mockstamp="case5") == True
	