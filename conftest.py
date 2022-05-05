
"""
Test argument configuration

Use the --genesis flag to specify what kind of genesis file we are testing.
The default is 'fresh'.
"""


def pytest_addoption(parser):
    """
    Add the --genesis flag
    """
    parser.addoption('--genesis', action='store', default='fresh')


def pytest_generate_tests(metafunc):
    """
    Pass the value from the --genesis flag to all
    the tests that use the "genesis_option" argument.
    """
    # This is called for every test. Only get/set command line arguments
    # if the argument is specified in the list of test "fixturenames".
    option_value = metafunc.config.option.genesis
    if 'genesis_option' in metafunc.fixturenames and option_value is not None:
        metafunc.parametrize('genesis_option', [option_value])
