import pytest

from celerity.celerity import Celerity
from celerity.util import dir_is_empty, remove_dir


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
		"input": f"./test/data/creation/{case}/a/input/",
		"output": f"./test/data/creation/{case}/a/output/",
		"rollback": f"./test/data/creation/{case}/a/rollback/"
	}

	post_directories = {
		"input": f"./test/data/creation/{case}/z/input/",
		"output": f"./test/data/creation/{case}/z/output/",
		"rollback": f"./test/data/creation/{case}/z/rollback/"
	}

	format_type = "psql"

	celerity = Celerity(directories, format_type)
	celerity.set_phase("z", post_directories)

	yield celerity
	
	def cleanup():
		# Cleanup code here
		remove_dir(directories["rollback"])
		remove_dir(directories["output"])

	request.addfinalizer(cleanup)

@pytest.mark.parametrize('fixture', ['case1'], indirect=True)
def test_psql_directory_verification(fixture, assert_with_msg):
	celerity = fixture
	
	directories = {
		"input": f"./test/data/creation/case1/a/input/",
		"output": f"./test/data/creation/case1/a/output/",
		"rollback": f"./test/data/creation/case1/a/rollback/"
	}

	assert dir_is_empty(directories["rollback"]) == True
	assert dir_is_empty(directories["output"]) == True
	assert dir_is_empty(directories["input"]) == False

	celerity.migrate()
	
	assert dir_is_empty(directories["rollback"]) == False
	assert dir_is_empty(directories["output"]) == False	

	assert_with_msg(celerity.run_test("schema") == True, "Generated schemas do not match")
	
	celerity.destroy()
	
	assert dir_is_empty(directories["rollback"]) == True
	assert dir_is_empty(directories["output"]) == True
	assert dir_is_empty(directories["input"]) == False

@pytest.mark.parametrize('fixture', ['case2'], indirect=True)
def test_psql_multiple_school(fixture, assert_with_msg):
	celerity = fixture	
	celerity.migrate()
	assert_with_msg(celerity.run_test("schema") == True, "Generated schemas do not match")

@pytest.mark.parametrize('fixture', ['case3'], indirect=True)
def test_psql_optional_fish(fixture, assert_with_msg):
	celerity = fixture
	celerity.migrate()
	assert_with_msg(celerity.run_test("schema") == True, "Generated schemas do not match")

@pytest.mark.parametrize('fixture', ['case4'], indirect=True)
def test_psql_unique_fish(fixture, assert_with_msg):
	celerity = fixture
	celerity.migrate()
	assert_with_msg(celerity.run_test("schema") == True, "Generated schemas do not match")

@pytest.mark.parametrize('fixture', ['case5'], indirect=True)
def test_psql_unique_and_optional_fish(fixture, assert_with_msg):
	celerity = fixture
	celerity.migrate()
	assert_with_msg(celerity.run_test("schema") == True, "Generated schemas do not match")

@pytest.mark.parametrize('fixture', ['case6'], indirect=True)
def test_psql_alias_fish(fixture, assert_with_msg):
	celerity = fixture
	celerity.migrate()
	assert_with_msg(celerity.run_test("schema") == True, "Generated schemas do not match")

@pytest.mark.parametrize('fixture', ['case7'], indirect=True)
def test_psql_foreign_key_alias(fixture, assert_with_msg):
	celerity = fixture
	celerity.migrate()
	assert_with_msg(celerity.run_test("schema") == True, "Generated schemas do not match")

@pytest.mark.parametrize('fixture', ['case8'], indirect=True)
def test_psql_polymorphic_school(fixture, assert_with_msg):
	celerity = fixture
	celerity.migrate()
	assert_with_msg(celerity.run_test("schema") == True, "Generated schemas do not match")
	
@pytest.mark.parametrize('fixture', ['case9'], indirect=True)
def test_psql_multiple_input_files(fixture, assert_with_msg):
	celerity = fixture
	celerity.migrate()
	assert_with_msg(celerity.run_test("schema") == True, "Generated schemas do not match")

@pytest.mark.parametrize('fixture', ['case10'], indirect=True)
def test_psql_attr_validation(fixture, assert_with_msg):
	celerity = fixture
	celerity.migrate()
	assert_with_msg(celerity.run_test("schema") == True, "Generated schemas do not match")
