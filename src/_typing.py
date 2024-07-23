"""
Contains typing classes.

NOTE: this module is private. All functions and objects are available in the main
`re_extensions` namespace - use that instead.

"""

import logging
from typing import TYPE_CHECKING, Tuple, TypeVar, Union

if TYPE_CHECKING:
    from re import Pattern

logging.warning(
    "importing from '._typing' - this module is not intended for direct import, "
    "therefore unexpected errors may occur"
)
SpanNGroup = Tuple[Tuple[int, int], str]
LineSpanNGroup = Tuple[int, Tuple[int, int], str]
PatternStr = Union[str, "Pattern[str]"]
PatternStrVar = TypeVar("PatternStrVar", str, "Pattern[str]")
