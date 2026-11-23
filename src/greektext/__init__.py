"""greektext: Greek text made easy to compare, search, transliterate and slugify.

>>> import greektext
>>> isinstance(greektext.__version__, str)
True
"""

from .accents import fold, strip_accents
from .case import fix_final_sigma, lower, upper
from .normalize import normalize
from .phonetic import phonetic_key
from .script import fix_lookalikes, greek_ratio, is_greek, sort_key
from .slug import slugify
from .translit import to_latin

__version__ = "0.3.0"

__all__ = [
    "__version__",
    "fix_final_sigma",
    "fix_lookalikes",
    "fold",
    "greek_ratio",
    "is_greek",
    "lower",
    "normalize",
    "phonetic_key",
    "slugify",
    "sort_key",
    "strip_accents",
    "to_latin",
    "upper",
]
