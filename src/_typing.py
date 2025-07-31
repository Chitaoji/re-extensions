"""
Contains typing classes.

NOTE: this module is not intended to be imported at runtime.

"""

from typing import TYPE_CHECKING, Callable, Union

import loggings

if TYPE_CHECKING:
    from re import Match, Pattern, RegexFlag

    from .smart import SmartMatch, SmartPattern

loggings.warning("this module is not intended to be imported at runtime")

PatternType = Union[str, "Pattern[str]", "SmartPattern[str]"]
MatchType = Union["Match[str]", "SmartMatch[str]", None]
ReplType = Union[str, Callable[["Match[str]"], str]]
FlagType = Union[int, "RegexFlag"]
