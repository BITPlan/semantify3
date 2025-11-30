"""
```yaml
# 🌐🕸
lod2rdf:
  isA: PythonModule
  author: Wolfgang Fahl
  createdAt: 2025-11-10
  purpose: list of dict to RDF conversion for semantify³.
```
"""

import re
import textwrap
from dataclasses import asdict, is_dataclass
from typing import Any, Dict, List, Optional

from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import RDF, XSD


class RDFDumper:
    """Converts list of dicts/dataclasses to RDF.

    This class provides functionality to convert Python dataclasses or dictionaries
    into RDF format using the rdflib library.
    """

    def __init__(
        self, base_uri: str, namespace_prefix: str = "ex", debug: bool = False
    ):
        """Initialize RDF dumper.

        Args:
            base_uri: Base URI for resources.
            namespace_prefix: Prefix for namespace.
            debug: Enable debug logging (default: False).
        """
        self.base_uri = base_uri
        self.namespace_prefix = namespace_prefix
        self.ns = Namespace(base_uri)
        self.debug = debug

    def sanitize_query(self, sparql_query: str) -> str:
        """Handle RDFlib/pyparsing/SPARQL parser quirks (strict WS after projection).

        1. textwrap.dedent(): Removes code-block indentation (e.g., 8-spaces method indent).
        2. .strip(): Drops leading/trailing WS (f-string '\\n').
        3. re.sub(r'\\s+', ' ', ): **CRUCIAL** - Collapses ALL internal '\\n'/multi-spaces/tabs
           to single ' ' → 'SELECT (...) WHERE { ?s ... }' (no '\\n' at char 34).
        4. Validates SPARQL op start.

        Args:
            sparql_query (str): Indented f-string (e.g., test_lod2rdf raw_query).

        Returns:
            str: Single-line, normalized, parser-proof query.

        Raises:
            ValueError: Missing SELECT/ASK/CONSTRUCT/DESCRIBE.
        """
        # Step-by-step (debug-friendly)
        dedented = textwrap.dedent(sparql_query)
        stripped = dedented.strip()
        normalized = re.sub(r"\s+", " ", stripped)
        if not normalized.startswith(("SELECT", "ASK", "CONSTRUCT", "DESCRIBE")):
            raise ValueError(f"Invalid SPARQL: '{normalized[:50]}...'")
        return normalized

    def as_rdf(
        self,
        lod: List[Dict[str, Any]],  # ✅ LOD (List of Dicts/Dataclasses)
        type_name: str,
        id_field: Optional[str] = None,
    ) -> Graph:
        """Convert list of dicts/dataclasses to RDF Graph (PURE: no I/O).

        Args:
            lod: List of dicts or dataclass instances.  # ✅ LOD-first
            type_name: RDF type name for resources.
            id_field: Field to use as resource identifier (auto-generated if None).

        Returns:
            Graph: Fresh rdflib.Graph with triples (serialize yourself).
        """
        if self.debug:
            print(f"LOD→RDF: {len(lod)} | type={type_name} | id={id_field or 'auto'}")

        graph = Graph()
        graph.bind(self.namespace_prefix, self.ns)

        for idx, item in enumerate(lod):
            item_dict = asdict(item) if is_dataclass(item) else item
            self.add_resource(
                graph, item_dict, type_name, id_field, idx
            )  # Inject graph

        if self.debug:
            print(f"Graph ready: {len(graph)} triples")

        return graph

    def as_file(
        self,
        lod: List[Dict[str, Any]],  # ✅ LOD param (CLI wrapper)
        type_name: str,
        id_field: Optional[str] = None,
        output_path: Optional[str] = None,  # None → stdout
        output_format: str = "turtle",
    ) -> Graph:
        """LOD → RDF Graph + serialize (file/stdout). Wrapper over as_rdf().

        Args:
            lod: List of dicts or dataclass instances.
            type_name: RDF type name for resources.
            id_field: Field to use as resource identifier (auto-generated if None).
            output_path: Path to save RDF file (None → print to stdout).
            output_format: Output format (turtle, xml, nt, json-ld).

        Returns:
            Graph: The generated Graph (chainable).
        """
        graph = self.as_rdf(lod, type_name, id_field)

        if output_path:
            graph.serialize(destination=output_path, format=output_format)
            if self.debug:
                print(f"Saved {len(graph)} triples → {output_path} ({output_format})")
        else:
            # ✅ CLI stdout
            print(graph.serialize(format=output_format).decode("utf-8"))
            if self.debug:
                print(f"Serialized {len(graph)} triples ({output_format}) → stdout")

        return graph

    def add_resource(
        self,
        graph: Graph,  # ✅ Inject Graph (no self.graph)
        item_dict: Dict[str, Any],
        type_name: str,
        id_field: Optional[str],
        idx: int,
    ) -> None:
        """Add resource to RDF graph.

        Args:
            graph: Target rdflib.Graph.
            item_dict: Dictionary with resource data.
            type_name: RDF type name for resource.
            id_field: Field name containing resource identifier.
            idx: Index for auto-generating IDs.
        """
        if id_field and id_field in item_dict:
            resource_id = item_dict[id_field]
        else:
            resource_id = f"{type_name.lower()}_{idx}"

        subject = URIRef(f"{self.base_uri}{resource_id}")
        graph.add((subject, RDF.type, self.ns[type_name]))

        for key, value in item_dict.items():
            if value is not None:
                predicate = self.ns[key]
                obj = self.create_literal(value)
                graph.add((subject, predicate, obj))

    def create_literal(self, value: Any) -> Literal:
        """Create RDF literal from Python value.

        Args:
            value: Python value to convert.

        Returns:
            Literal: RDF Literal with appropriate datatype.
        """
        if isinstance(value, bool):
            result = Literal(value, datatype=XSD.boolean)
        elif isinstance(value, int):
            result = Literal(value, datatype=XSD.integer)
        elif isinstance(value, float):
            result = Literal(value, datatype=XSD.double)
        else:
            result = Literal(str(value))
        return result
