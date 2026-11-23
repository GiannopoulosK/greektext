"""greektext: Greek text made easy to compare, search, transliterate and slugify.

>>> import greektext
>>> isinstance(greektext.__version__, str)
True
"""

from ._accents import fold, strip_accents
from ._case import fix_final_sigma, lower, upper
from ._normalize import normalize
from ._phonetic import phonetic_key
from ._script import fix_lookalikes, greek_ratio, is_greek, sort_key
from ._slug import slugify
from ._translit import to_latin

__version__ = "1.0.0"

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
