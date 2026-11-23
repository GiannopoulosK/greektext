# API reference

All public functions live at the package top level, are pure and stateless, and accept any
Unicode input. They return `str`, except `sort_key` (a tuple), `greek_ratio` (a float) and
`is_greek` (a bool). The implementation modules (`greektext._*`) are private.

::: greektext
    options:
      members:
        - normalize
        - strip_accents
        - fold
        - upper
        - lower
        - fix_final_sigma
        - to_latin
        - phonetic_key
        - slugify
        - sort_key
        - is_greek
        - greek_ratio
        - fix_lookalikes
