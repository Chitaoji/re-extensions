"""
Contains typing classes.

NOTE: this module is not intended to be imported at runtime.

"""

from re import Match, Pattern, RegexFlag
from typing import Callable

import loggings

from .smart import SmartPattern

loggings.warning("this module is not intended to be imported at runtime")

PatternType = str | Pattern[str] | SmartPattern
MatchType = Match[str] | None
ReplType = str | Callable[[Match[str]], str]
FlagType = int | RegexFlag
