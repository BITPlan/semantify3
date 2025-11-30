"""Created on 2025-11-29.

@author: wf
"""

from basemkit.yamlable import lod_storable

import sem3


@lod_storable
class Version:
    """Version handling for semantify³."""

    name = "semantify³"
    version = sem3.__version__
    date = "2025-11-29"
    updated = "2025-11-30"
    description = "Extract knowledge graph ready triples from human-readable annotations wherever possible — Syntax matters!"

    authors = "Wolfgang Fahl, Tim Holzheim"

    doc_url = "https://wiki.bitplan.com/index.php/semantify3"
    chat_url = "https://github.com/BITPlan/semantify3/discussions"
    cm_url = "https://github.com/BITPlan/semantify3"

    license = """Copyright 2025 contributors. All rights reserved.

  Licensed under the Apache License 2.0
  http://www.apache.org/licenses/LICENSE-2.0

  Distributed on an "AS IS" basis without warranties
  or conditions of any kind, either express or implied."""

    longDescription = f"""{name} version {version}
{description}

  Created by {authors} on {date} last updated {updated}"""
