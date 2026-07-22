"""Tests for the semantify³ service-overview homepage generator.

```yaml
# 🌐🕸
test_homepage:
  isA: PythonTestModule
  author: Wolfgang Fahl
  createdAt: 2026-07-22
  purpose: Unit tests for the semantify³ homepage generator.
```
"""

import io
import os
import tempfile
from contextlib import redirect_stdout

from sem3.homepage import Service, ServiceHomepage
from sem3.sem3_cmd import Semantify3Cmd
from tests.base_sem3test import BaseSem3test

# a sample Apache vhost .conf carrying four annotated services with different
# publicity values (public, login, hidden, and a missing publicity)
SAMPLE_CONF = """\
# ```yaml
# # 🌐🕸
# jena.bitplan.com:
#   isA: TripleStore
#   ui: Fuseki
#   url: https://jena.bitplan.com
#   publicity: public
# ```
<VirtualHost *:80>
  ServerName jena.bitplan.com
</VirtualHost>

# ```yaml
# # 🌐🕸
# alpha.example.org:
#   isA: Website
#   url: https://alpha.example.org
#   publicity: public
# ```
<VirtualHost *:80>
  ServerName alpha.example.org
</VirtualHost>

# ```yaml
# # 🌐🕸
# admin.example.org:
#   isA: Website
#   url: https://admin.example.org
#   publicity: login
# ```
<VirtualHost *:80>
  ServerName admin.example.org
</VirtualHost>

# ```yaml
# # 🌐🕸
# secret.example.org:
#   isA: Website
#   url: https://secret.example.org
#   publicity: hidden
# ```
<VirtualHost *:80>
  ServerName secret.example.org
</VirtualHost>

# ```yaml
# # 🌐🕸
# nopub.example.org:
#   isA: Website
#   url: https://nopub.example.org
# ```
<VirtualHost *:80>
  ServerName nopub.example.org
</VirtualHost>
"""


class TestHomepage(BaseSem3test):
    """Test the service-overview homepage generator."""

    def setUp(self, debug=True, profile=True):
        BaseSem3test.setUp(self, debug=debug, profile=profile)
        self.tmp_dir = tempfile.mkdtemp()
        self.conf_path = os.path.join(self.tmp_dir, "sites.conf")
        with open(self.conf_path, "w", encoding="utf-8") as conf_file:
            conf_file.write(SAMPLE_CONF)

    def test_service_tooltip_and_html(self):
        """A Service renders an <li> and a tooltip without id/url."""
        service = Service(
            "jena.bitplan.com",
            {
                "name": "jena.bitplan.com",
                "isA": "TripleStore",
                "ui": "Fuseki",
                "url": "https://jena.bitplan.com",
                "publicity": "public",
            },
        )
        html = service.as_html()
        self.assertIn('href="https://jena.bitplan.com"', html)
        self.assertIn(">jena.bitplan.com</a>", html)
        tooltip = service.tooltip()
        self.assertIn("isA: TripleStore", tooltip)
        self.assertIn("ui: Fuseki", tooltip)
        # id and url must not appear in the tooltip
        self.assertNotIn("url:", tooltip)
        self.assertNotIn("name:", tooltip)

    def test_grouping_excludes_hidden(self):
        """hidden and publicity-less services are excluded from sections."""
        homepage = ServiceHomepage(title="test", debug=self.debug)
        count = homepage.read_files([self.conf_path])
        self.assertEqual(count, 5)  # all five annotations are parsed
        grouped = homepage.services_by_section()
        # only public + login sections are rendered
        self.assertEqual(set(grouped.keys()), {"public", "login"})
        public_ids = [service.id for service in grouped["public"]]
        # public sorted by id: alpha before jena
        self.assertEqual(public_ids, ["alpha.example.org", "jena.bitplan.com"])
        login_ids = [service.id for service in grouped["login"]]
        self.assertEqual(login_ids, ["admin.example.org"])

    def test_as_html_page(self):
        """The rendered page groups by publicity and hides hidden services."""
        homepage = ServiceHomepage(title="fur.bitplan.com", debug=self.debug)
        homepage.read_files([self.conf_path])
        page = homepage.as_html()
        if self.debug:
            print(page)
        self.assertIn("<title>fur.bitplan.com</title>", page)
        self.assertIn("<h2>Public services</h2>", page)
        self.assertIn("<h2>Login required</h2>", page)
        self.assertIn("jena.bitplan.com", page)
        self.assertIn("admin.example.org", page)
        # hidden and publicity-less services must not appear
        self.assertNotIn("secret.example.org", page)
        self.assertNotIn("nopub.example.org", page)

    def test_cli_homepage(self):
        """The --homepage CLI flag renders the page to stdout."""
        cmd = Semantify3Cmd()
        capture = io.StringIO()
        with redirect_stdout(capture):
            exit_code = cmd.run(
                ["--homepage", "--title", "fur.bitplan.com", "-i", self.conf_path]
            )
        output = capture.getvalue()
        self.assertEqual(exit_code, 0)
        self.assertIn("<h1>fur.bitplan.com</h1>", output)
        self.assertIn("jena.bitplan.com", output)
        self.assertNotIn("secret.example.org", output)
