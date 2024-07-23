"""
# re-extensions
Extensions for the `re` package.

## See Also
### Github repository
* https://github.com/Chitaoji/re-extensions/

### PyPI project
* https://pypi.org/project/re-extensions/

## License
This project falls under the BSD 3-Clause License.

"""

from typing import List

from . import core
from .__version__ import __version__
from .core import *

__all__: List[str] = []
__all__.extend(core.__all__)
