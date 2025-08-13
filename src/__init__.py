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

from . import core, smart
from .__version__ import __version__
from .core import *
from .smart import *

__all__: list[str] = ["smart"]
__all__.extend(core.__all__)
__all__.extend(smart.__all__)
