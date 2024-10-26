from sys import modules as _modules
from DependencyLibrary.library import depends_on_test, depends_on_suite, LIBRARY_NAME
from DependencyLibrary.solver import DependencySolver

__all__ = ['depends_on_test', 'depends_on_suite', 'DependencySolver']

ROBOT_LISTENER_API_VERSION = 3
ROBOT_LIBRARY_LISTENER = _modules[LIBRARY_NAME]
