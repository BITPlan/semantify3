# semantify3
semantify³ - extract knowledge graph ready triples from human readable annotations whereever  possible - Syntax matters!

| | |
| :--- | :--- |
| **PyPi** | [![PyPI Status](https://img.shields.io/pypi/v/semantify3.svg)](https://pypi.python.org/pypi/semantify3/) [![License](https://img.shields.io/github/license/BITPlan/semantify3.svg)](https://www.apache.org/licenses/LICENSE-2.0) [![pypi](https://img.shields.io/pypi/pyversions/semantify3)](https://pypi.org/project/semantify3/) [![format](https://img.shields.io/pypi/format/semantify3)](https://pypi.org/project/semantify3/) [![downloads](https://img.shields.io/pypi/dd/semantify3)](https://pypi.org/project/semantify3/) |
| **GitHub** | [![Github Actions Build](https://github.com/BITPlan/semantify3/actions/workflows/build.yml/badge.svg)](https://github.com/BITPlan/semantify3/actions/workflows/build.yml) [![Release](https://img.shields.io/github/v/release/BITPlan/semantify3)](https://github.com/BITPlan/semantify3/releases) [![Contributors](https://img.shields.io/github/contributors/BITPlan/semantify3)](https://github.com/BITPlan/semantify3/graphs/contributors) [![Last Commit](https://img.shields.io/github/last-commit/BITPlan/semantify3)](https://github.com/BITPlan/semantify3/commits/) [![GitHub issues](https://img.shields.io/github/issues/BITPlan/semantify3.svg)](https://github.com/BITPlan/semantify3/issues) [![GitHub closed issues](https://img.shields.io/github/issues-closed/BITPlan/semantify3.svg)](https://github.com/BITPlan/semantify3/issues/?q=is%3Aissue+is%3Aclosed) |
| **Code** | [![style-black](https://img.shields.io/badge/%20style-black-000000.svg)](https://github.com/psf/black) [![imports-isort](https://img.shields.io/badge/%20imports-isort-%231674b1)](https://pycqa.github.io/isort/) |
| **Docs** | [![API Docs](https://img.shields.io/badge/API-Documentation-blue)](https://BITPlan.github.io/semantify3/) [![formatter-docformatter](https://img.shields.io/badge/%20formatter-docformatter-fedcba.svg)](https://github.com/PyCQA/docformatter) [![style-google](https://img.shields.io/badge/%20style-google-3666d6.svg)](https://google.github.io/styleguide/pyguide.html#s3.8-comments-and-docstrings) |

## Documentation
[Wiki](https://wiki.bitplan.com/index.php/semantify3)

### Authors
* [Tim Holzheim](https://www.semantic-mediawiki.org/wiki/Tim_Holzheim)
* [Wolfgang Fahl](http://www.bitplan.com/Wolfgang_Fahl)

### Usage
```bash
usage: sem3 [-h] [-a] [-d] [--debugLocalPath DEBUGLOCALPATH] [--debugPort DEBUGPORT]
            [--debugRemotePath DEBUGREMOTEPATH] [--debugServer DEBUGSERVER] [-f] [-q] [-v] [-V] [-i INPUT]
            [-o OUTPUT] [--format {turtle,n3,ntriples,xml,json-ld,sidif,graphml,graphson,cypher}]
            [files ...]

Extract knowledge graph ready triples from human-readable annotations wherever possible — Syntax matters!

positional arguments:
  files

options:
  -h, --help            show this help message and exit
  -a, --about           show version info and open documentation
  -d, --debug           enable debug output
  --debugLocalPath DEBUGLOCALPATH
                        remote debug Server path mapping - localPath - path on machine where python runs
  --debugPort DEBUGPORT
                        remote debug Port [default: 5678]
  --debugRemotePath DEBUGREMOTEPATH
                        remote debug Server path mapping - remotePath - path on debug server
  --debugServer DEBUGSERVER
                        remote debug Server
  -f, --force           force overwrite or unsafe actions
  -q, --quiet           suppress all output
  -v, --verbose         increase output verbosity
  -V, --version         show program's version number and exit
  -i INPUT, --input INPUT
                        Input file glob expression
  -o OUTPUT, --output OUTPUT
                        Output file path for triples
  --format {turtle,n3,ntriples,xml,json-ld,sidif,graphml,graphson,cypher}
                        Output serialization format (default: turtle)
```
#### Example
```
sem3 -i "**/*.py"
1: yaml in extractor.py:3
extractor:
  isA: PythonModule
  author: Wolfgang Fahl
  createdAt: 2025-11-29
  purpose: extraction of relevant markup snippets for semantify³.
--------------------
2: yaml in sem3_cmd.py:3
sem3_cmd:
  isA: PythonModule
  author: Wolfgang Fahl
  createdAt: 2025-11-29
  purpose: Command-line interface for semantify³.
--------------------
3: yaml in test_cmd.py:3
test_cmd:
  isA: PythonTestModule
  author: Wolfgang Fahl
  createdAt: 2025-11-29
  purpose: Unit tests for the semantify³ CLI.
--------------------
4: sidif in test_extractor.py:2
test_extractor isA PythonModule
  "Wolfgang Fahl" is author of it
  "2025-11-29" is createdAt of it
  "Test main micro annotation snippet extraction" is purpose of it
--------------------
5: yaml in test_extractor.py:63
ypgen.bitplan.com:
  isA: Service
  ui: nicegui
  url: https://ypgen.bitplan.com
  createdAt: 2024-07-23T09:19:32.709025
  publicity: intranet
--------------------
```
