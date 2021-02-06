The programs here generate custom dictionaries that are in Mathics, its
scanner and elsewhere.


The dictionaries are dumped as JSON because ujson was benchmarked as
one of the fastest way to read in table data into Python.

Other alternatives considered were YAML, Python Pickle, and the
standard Python JSON loader.
