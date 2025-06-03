"""
Contains typing classes.

NOTE: this module is not intended to be imported at runtime.

"""

from typing import TYPE_CHECKING

import loggings

if TYPE_CHECKING:
    from re import Match, Pattern, RegexFlag

    from .src._typing import FlagType, MatchType, PatternType, ReplType

loggings.warning("this module is not intended to be imported at runtime")
