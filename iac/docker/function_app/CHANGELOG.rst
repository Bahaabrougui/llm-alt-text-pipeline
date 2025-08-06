Changelog
=========

All notable changes to this project will be documented in this file.

Each version refers to a tag of the corresponding docker image
`psiacr/alttext-func`.

The format is based on `Keep a Changelog`_,
and this project adheres to `Semantic Versioning`_.


Version 0.0.2 (2025-07-04)
--------------------------

* Changed: Use low-weight blip-base for captioning
* Changed: Run all inference on CPU
* Changed: Load all low-weight models to RAM
* Added: Safe json logging
* Added: LLM related metrics logging


Version 0.0.1 (2025-06-30)
--------------------------

* Added: initial release
    * Uses Blip2 2.7B
    * Uses Detoxify
    * Uses Helsinki-NLP/opus-mt-en-{target_lang}


.. _Keep a Changelog:
    https://keepachangelog.com/en/1.0.0/
.. _Semantic Versioning:
    https://semver.org/spec/v2.0.0.html
