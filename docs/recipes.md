# Recipes

greektext ships no framework integrations: every function is a plain `str -> str` callable, so it
plugs into frameworks and libraries directly. These are the common cases.

## Django

### Slugs

Django's `slugify` deletes Greek letters (`slugify("Καλημέρα")` is `""`). Use greektext's
instead when populating a `SlugField`:

```python
from django.db import models
from greektext import slugify


class Article(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title, max_length=50)  # "Καλημέρα Κόσμε" -> "kalimera-kosme"
        super().save(*args, **kwargs)
```

### Template filters

CSS `text-transform: uppercase` keeps the tonos (*ΑΘΉΝΑ*), and emails, PDFs and plain-text
exports have no CSS at all. Register greektext's functions as filters in one of your apps, e.g.
`yourapp/templatetags/greek.py`:

```python
from django import template
from django.template.defaultfilters import stringfilter

import greektext

register = template.Library()
register.filter("greek_upper", stringfilter(greektext.upper))
register.filter("greek_slug", stringfilter(greektext.slugify), is_safe=True)
register.filter("greek_latin", stringfilter(greektext.to_latin), is_safe=True)
```

```django
{% load greek %}
<h1>{{ title|greek_upper }}</h1>            {# Μάιος -> ΜΑΪΟΣ #}
<a href="/{{ name|greek_slug }}/">{{ name|greek_latin }}</a>
```

## Search

Store a folded copy of the text next to the original and search the folded column with the
folded query. Accents, case and final sigma then no longer matter:

```python
>>> from greektext import fold
>>> rows = ["Αθήνα", "Θεσσαλονίκη", "ΠΆΤΡΑ"]
>>> index = {fold(r): r for r in rows}
>>> index[fold("πατρα")]
'ΠΆΤΡΑ'

```

To also find Greeklish and transliterated spellings, index `phonetic_key` the same way (see
[Matching Greeklish](phonetic.md)).

## Keyword matching (keylex)

[keylex](https://github.com/GiannopoulosK/keylex) accepts any `str -> str` callable as its
token `stemmer` and lets a keyword carry spelling `variants`:

```python
from keylex import Keyword, KeywordMatcher
from greektext import phonetic_key, to_latin


def greek_keyword(name: str) -> Keyword:
    """A keyword that also matches its ELOT 743 and simple transliterations."""
    return Keyword(name, variants=[to_latin(name), to_latin(name, scheme="simple")])


matcher = KeywordMatcher([greek_keyword("Θεσσαλονίκη")], ignore_accents=True)
matcher.find("ΘΕΣΣΑΛΟΝΙΚΗ, Thessaloniki")  # both match

# Broader but less precise: compare tokens by sound, so Greeklish spellings match too.
fuzzy = KeywordMatcher([Keyword("Θεσσαλονίκη")], stemmer=phonetic_key)
fuzzy.find("thesaloniki, Thessalonikh")  # both match
```

keylex applies the stemmer only to purely alphabetic tokens, so spellings with digits
(`8essalonikh`) need an explicit variant.
