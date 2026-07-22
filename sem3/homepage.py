"""Service-overview homepage generator for semantify³.

Python successor of the two-file PHP generator (index.php + sites.php) that
renders a live service list from 🌐🕸-annotated web-server configuration files.
Engine-agnostic: the same annotation blocks work in Apache ``.conf`` comments
and in Caddyfile comments — only the default input glob differs.

```yaml
# 🌐🕸
homepage:
  isA: PythonModule
  author: Wolfgang Fahl
  createdAt: 2026-07-22
  purpose: Generate a service-overview homepage from semantify³-annotated web-server configs.
```
"""

import html
from typing import Dict, List, Optional

from sem3.extractor import Extractor

# default input globs per web-server engine whose config comments may carry
# 🌐🕸 annotation blocks
ENGINE_GLOBS: Dict[str, List[str]] = {
    "apache": ["/etc/apache2/sites-available/*.conf"],
    "caddy": ["/etc/caddy/Caddyfile", "/etc/caddy/conf.d/*.caddy"],
}

# publicity buckets that get rendered, in order, with their section titles;
# any other publicity value (e.g. "hidden", "intranet") is not rendered
DEFAULT_SECTIONS: Dict[str, str] = {
    "public": "Public services",
    "login": "Login required",
}


class Service:
    """A single annotated service (one top-level key of a 🌐🕸 YAML block)."""

    # housekeeping keys that never belong in the visible tooltip
    HIDDEN_KEYS = {"name", "id", "url", "source"}

    def __init__(self, service_id: str, props: Dict[str, object]):
        """
        Construct a Service from its id and annotation properties.

        Args:
            service_id: the annotation's top-level key, e.g. "jena.bitplan.com"
            props: the parsed annotation properties (isA, url, publicity, ...)
        """
        self.id = service_id
        self.props = props
        self.url = str(props.get("url", "#"))
        self.publicity = str(props.get("publicity", "hidden"))
        self.is_a = str(props.get("isA", "Uncategorized"))

    def tooltip(self) -> str:
        """
        Build the hover tooltip from all scalar props except id/url/housekeeping.

        Returns:
            newline-joined "key: value" lines
        """
        lines = []
        for key, value in self.props.items():
            if key in self.HIDDEN_KEYS:
                continue
            if isinstance(value, (list, dict)):
                continue
            lines.append(f"{key}: {value}")
        tooltip = "\n".join(lines)
        return tooltip

    def as_html(self) -> str:
        """
        Render the service as an HTML list item with a tooltip.

        Returns:
            an <li> element linking to the service url
        """
        href = html.escape(self.url, quote=True)
        tooltip = html.escape(self.tooltip(), quote=True)
        label = html.escape(self.id)
        item = (
            f'<li><a href="{href}" target="_blank" title="{tooltip}">{label}</a></li>'
        )
        return item


class ServiceHomepage:
    """Generate a grouped service-overview homepage from 🌐🕸 annotations."""

    def __init__(
        self,
        title: str,
        sections: Optional[Dict[str, str]] = None,
        debug: bool = False,
    ):
        """
        Construct the homepage generator.

        Args:
            title: page title / heading, typically the host the page runs on
            sections: ordered {publicity: section_title} map to render
            debug: if True enable extractor debug output
        """
        self.title = title
        self.sections = sections if sections is not None else DEFAULT_SECTIONS
        self.debug = debug
        self.services: List[Service] = []

    def add_lod(self, lod: List[Dict[str, object]]) -> None:
        """
        Add services from an extracted list-of-dicts.

        Args:
            lod: extractor output; each dict is one annotated service
        """
        for record in lod:
            service_id = record.get("name")
            if not service_id:
                continue
            service = Service(str(service_id), record)
            self.services.append(service)

    def read_files(self, patterns: List[str]) -> int:
        """
        Extract services from files matching the given glob patterns.

        Args:
            patterns: glob patterns for annotated config files

        Returns:
            the number of services collected so far
        """
        extractor = Extractor(debug=self.debug)
        markups = extractor.extract_from_glob_list(patterns)
        lod = extractor.markups_to_lod(markups)
        self.add_lod(lod)
        service_count = len(self.services)
        return service_count

    def services_by_section(self) -> Dict[str, List[Service]]:
        """
        Group renderable services by publicity section, each sorted by id.

        Services whose publicity is not a configured section (e.g. "hidden" or
        a missing publicity, which defaults to "hidden") are excluded.

        Returns:
            {publicity: [Service, ...]} limited to configured sections
        """
        grouped: Dict[str, List[Service]] = {}
        for service in self.services:
            publicity = service.publicity
            if publicity not in self.sections:
                continue
            grouped.setdefault(publicity, []).append(service)
        for service_list in grouped.values():
            service_list.sort(key=lambda service: service.id)
        return grouped

    def section_as_html(self, section_title: str, services: List["Service"]) -> str:
        """
        Render one publicity section as a heading followed by a service list.

        Args:
            section_title: the visible section heading
            services: the (already sorted) services of this section

        Returns:
            the section's HTML
        """
        items = "\n".join(f"  {service.as_html()}" for service in services)
        section = f"<h2>{html.escape(section_title)}</h2>\n<ul>\n{items}\n</ul>"
        return section

    def as_html(self) -> str:
        """
        Render the full service-overview homepage.

        Returns:
            a complete, self-contained HTML document
        """
        grouped = self.services_by_section()
        sections = "\n".join(
            self.section_as_html(section_title, grouped[publicity])
            for publicity, section_title in self.sections.items()
            if grouped.get(publicity)
        )
        title = html.escape(self.title)
        credit = '<a href="https://github.com/BITPlan/semantify3">semantify3</a>'
        page = f"""\
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<title>{title}</title>
</head>
<body>
<h1>{title}</h1>
<p>Service list generated from {credit}-annotated web-server configurations.</p>
{sections}
</body>
</html>"""
        return page
