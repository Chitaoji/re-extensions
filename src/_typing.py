"""
Contains typing classes.

NOTE: this module is private. All functions and objects are available in the main
`re_extensions` namespace - use that instead.

"""

import logging
from typing import TYPE_CHECKING, Callable, Union

if TYPE_CHECKING:
    from re import Match, Pattern, RegexFlag

    from .core import SmartMatch, SmartPattern

logging.warning(
    "importing from '._typing' - this module is not intended for direct import, "
    "therefore unexpected errors may occur"
)

PatternType = Union[str, "Pattern[str]", "SmartPattern[str]"]
MatchType = Union["Match[str]", "SmartMatch[str]", None]
ReplType = Union[str, Callable[["Match[str]"], str]]
FlagType = Union[int, "RegexFlag"]
