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

        # 2. Execute a SPARQL to count the total number of resources (any type)
        # Since the fix now uses isA from data, resources may have different types
        raw_query = """
SELECT (COUNT(DISTINCT ?s) AS ?resourceCount)
    WHERE {
        ?s a ?type .
    }"""
        sparql_query = dumper.sanitize_query(raw_query)
        qres = g.query(sparql_query)

        # 3. Get the result
        count = 0
        for row in qres:
            # Access the renamed variable
            count = int(row.resourceCount)

        if self.debug:
            print(f"SPARQL Count Result: {count}")

        # 4. Assert that the RDF graph contains the same number of items as our list of dicts
        self.assertEqual(
            count,
            len(modules_lod),
            f"Expected {len(modules_lod)} resources in RDF, found {count}",
        )

    def test_isa_field_usage(self):
        """
        Test that the RDF dumper uses the isA field from the data
        instead of always using the type_name parameter.
        """
        base_uri = "https://example.org/"
        fallback_type = "DefaultType"
        
        dumper = RDFDumper(base_uri=base_uri, namespace_prefix="test")
        
        # Create test data with different isA values
        test_lod = [
            {"name": "item1", "isA": "VirtualHost", "purpose": "Test host"},
            {"name": "item2", "isA": "FarmSetting", "purpose": "Test setting"},
            {"name": "item3", "purpose": "No isA field"},  # Should use fallback
        ]
        
        # Generate RDF
        graph = dumper.as_rdf(
            lod=test_lod,
            type_name=fallback_type,
            id_field="name"
        )
        
        if self.debug:
            print(f"\nGenerated graph:\n{graph.serialize(format='turtle')}")
        
        # Verify that item1 has type VirtualHost
        query1 = dumper.sanitize_query(f"""
            SELECT ?type
            WHERE {{
                <{base_uri}item1> a ?type .
            }}
        """)
        result1 = list(graph.query(query1))
        self.assertEqual(len(result1), 1, "item1 should have exactly one type")
        type1 = str(result1[0][0])
        self.assertTrue(type1.endswith("VirtualHost"), 
                       f"item1 should be VirtualHost, got {type1}")
        
        # Verify that item2 has type FarmSetting
        query2 = dumper.sanitize_query(f"""
            SELECT ?type
            WHERE {{
                <{base_uri}item2> a ?type .
            }}
        """)
        result2 = list(graph.query(query2))
        self.assertEqual(len(result2), 1, "item2 should have exactly one type")
        type2 = str(result2[0][0])
        self.assertTrue(type2.endswith("FarmSetting"), 
                       f"item2 should be FarmSetting, got {type2}")
        
        # Verify that item3 has the fallback type
        query3 = dumper.sanitize_query(f"""
            SELECT ?type
            WHERE {{
                <{base_uri}item3> a ?type .
            }}
        """)
        result3 = list(graph.query(query3))
        self.assertEqual(len(result3), 1, "item3 should have exactly one type")
        type3 = str(result3[0][0])
        self.assertTrue(type3.endswith(fallback_type), 
                       f"item3 should be {fallback_type}, got {type3}")
