"""
Created on 2025-10-31

@author: wf
"""

import tempfile

from rdflib import Graph

from sem3.lod2rdf import RDFDumper
from tests.base_sem3test import BaseSem3test


class TestYaml2RDF(BaseSem3test):
    """
    test the Yaml to RDF conversion
    """

    def setUp(self, debug=True, profile=True):
        BaseSem3test.setUp(self, debug=debug, profile=profile)
        # Create a temporary directory for the test output
        self.tmp_path = tempfile.mkdtemp()
        self.turtle_file = f"{self.tmp_path}/python_modules.ttl"

    def test_lod2rdf(self):
        """
        Test RDF conversion of the extracted python modules list
        and verify with a SPARQL count query.
        """
        base_uri = "https://semantify3.bitplan.com/source_code/"
        type_name = "PythonModule"

        dumper = RDFDumper(base_uri=base_uri, namespace_prefix="python_module")

        # Get the list of dicts extracted from source code
        markups = self.get_markups()

        modules_lod = self.extractor.markups_to_lod(markups)

        # Ensure we found something before trying to dump
        self.assertGreater(len(modules_lod), 0, "No Python module YAML snippets found")

        dumper.as_file(
            lod=modules_lod,
            type_name=type_name,
            output_path=self.turtle_file,
            id_field="name",
            output_format="turtle",
        )

        if self.debug:
            print(f"RDF saved to: {self.turtle_file}")
            with open(self.turtle_file, "r") as f:
                print(f.read())

        # --- Verification Step ---

        # 1. Load the generated file into an rdflib Graph
        g = Graph()
        g.parse(self.turtle_file, format="turtle")

        if self.debug:
            print(f"Loaded {len(g)} triples.")

        # 2. Execute a SPARQL to count the number of resources of type PythonModule
        # We rename the variable to ?moduleCount to avoid conflict with method row.count()
        raw_query = f"""
SELECT (COUNT(?s) AS ?moduleCount)
    WHERE {{
        ?s a <{base_uri}{type_name}> .
    }}"""
        sparql_query = dumper.sanitize_query(raw_query)
        qres = g.query(sparql_query)

        # 3. Get the result
        count = 0
        for row in qres:
            # Access the renamed variable
            count = int(row.moduleCount)

        if self.debug:
            print(f"SPARQL Count Result: {count}")

        # 4. Assert that the RDF graph contains the same number of items as our list of dicts
        self.assertEqual(
            count,
            len(modules_lod),
            f"Expected {len(modules_lod)} resources in RDF, found {count}",
        )
