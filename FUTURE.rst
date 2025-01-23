2025-2026 Roadmap

* Revise scanner to reduce/remove "prescanner" code that does not respect comments. A lot of this code such as for named characters \[...] can be done inside the main scanner.
* Use more data from YAML data in the tokenizer rather than hard code the values in Python.
* Add token positions inside the tokenizer (and a container id?) the way CodeTokenize handles this.
* Get ``mathics3-tokens -C`` output more aligned with CodeTokenize.
* Remove no-longer-needed operator information from ``named-characters.yml``

In general, there is work to do to get the scanner to be more WMA compliant; adding more position information in the tokens will allow us to provide better debugging and error reporting information.
