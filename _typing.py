"""
Contains typing classes.

NOTE: this module is private. All functions and objects are available in the main
`re_extensions` namespace - use that instead.

"""

import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from re import Match, Pattern, RegexFlag

    from .src._typing import FlagType, MatchType, PatternType, ReplType

logging.warning(
    "importing from '._typing' - this module is not intended for direct import, "
    "therefore unexpected errors may occur"
)
