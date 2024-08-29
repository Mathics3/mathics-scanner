Files in this directory contains data for conversion between

* WL characters, names, and unicode symbols
* Information about WL operators

Input data for conversion programs is in YAML:
``named-characters.yml`` and ``operators.yml`` Processed data is in
JSON since that is the format which affords the fasted loading into
Python programs (via ujson).
