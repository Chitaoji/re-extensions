"""
Namespace for smart operations.

NOTE: this module is not included in the main `re_extensions` namespace - run
`from re_extensions import smart` to use this module.

"""

__all__ = []

# pylint: disable=unused-import
from .core import SmartMatch as Match
from .core import SmartPattern as Pattern
from .core import line_findall, line_finditer, lsplit, rsplit
from .core import smart_findall as findall
from .core import smart_finditer as finditer
from .core import smart_fullmatch as fullmatch
from .core import smart_match as match
from .core import smart_search as search
from .core import smart_split as split
from .core import smart_sub as sub
from .core import smart_subn as subn
