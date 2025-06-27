from enum import Enum
from types import MethodType
from typing import List, NamedTuple, Tuple, Union


class ContainerKind(Enum):
    UNKNOWN = 0
    FILE = 1  # Mathics3 files
    STREAM = 2  # input stream
    STRING = 3  # String fully
    PYTHON = 4  # Python implemented builtin funciton


class Container(NamedTuple):
    kind: ContainerKind
    name: str


class SourceRange(NamedTuple):
    start: int  # starting offset in bytes
    end: int  # offset
    container: int


SourceTextPosition: Union[SourceRange, MethodType]


class SourceTextLocations(NamedTuple):
    positions: List[Union[SourceRange, MethodType]] = []


# True if we want to keep track of positiosn as we scan an parse.
# This can be useful in debugging. It can also add a lot memory in
# saving position information.
TRACK_LOCATIONS: bool = True

# List of all Mathics3 files seen. We use the index in the list as a short
# representation of the file path.
# For example:
#   ["mathics/autoload/rules/Bessel.m", "mathics/autoload/rules/Element.m", ... ]
MATHICS3_PATHS: List[str] = []
