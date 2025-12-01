#!/usr/bin/env python3
"""Build wiki markdown files into static HTML with dark theme."""

from pathlib import Path
import markdown
import re

SITE_DIR = Path('_site')

CSS = """
:root {
  --bg: #0f172a;
  --bg-card: #1e293b;
  --text: #e2e8f0;
  --text-muted: #94a3b8;
  --accent: #38bdf8;
  --border: #334155;
}
* { box-sizing: border-box; margin: 0; padding: 0; }
body {
  font-family: system-ui, -apple-system, sans-serif;
  background: var(--bg);
  color: var(--text);
  line-height: 1.6;
  padding: 2rem;
  max-width: 900px;
  margin: 0 auto;
}
header {
  border-bottom: 1px solid var(--border);
  padding-bottom: 1rem;
  margin-bottom: 2rem;
}
header h1 {
  font-size: 1.5rem;
  color: var(--accent);
  margin-bottom: 0.5rem;
}
nav a {
  color: var(--text-muted);
  text-decoration: none;
  margin-right: 1rem;
  font-size: 0.875rem;
}
nav a:hover { color: var(--accent); }
main h1, main h2, main h3 {
  color: var(--text);
  margin: 1.5rem 0 0.75rem;
}
main h1 { font-size: 2rem; border-bottom: 1px solid var(--border); padding-bottom: 0.5rem; }
main h2 { font-size: 1.5rem; }
main h3 { font-size: 1.25rem; }
main p { margin: 0.75rem 0; }
main a { color: var(--accent); text-decoration: none; }
main a:hover { text-decoration: underline; }
main ul, main ol { margin: 0.75rem 0 0.75rem 1.5rem; }
main li { margin: 0.25rem 0; }
main code {
  background: var(--bg-card);
  padding: 0.125rem 0.375rem;
  border-radius: 0.25rem;
  font-size: 0.875em;
}
main pre {
  background: var(--bg-card);
  padding: 1rem;
  border-radius: 0.5rem;
  overflow-x: auto;
  margin: 1rem 0;
}
main pre code { background: none; padding: 0; }
main table {
  width: 100%;
  border-collapse: collapse;
  margin: 1rem 0;
}
main th, main td {
  border: 1px solid var(--border);
  padding: 0.5rem;
  text-align: left;
}
main th { background: var(--bg-card); }
main blockquote {
  border-left: 3px solid var(--accent);
  padding-left: 1rem;
  margin: 1rem 0;
  color: var(--text-muted);
}
main hr {
  border: none;
  border-top: 1px solid var(--border);
  margin: 2rem 0;
}
footer {
  margin-top: 3rem;
  padding-top: 1rem;
  border-top: 1px solid var(--border);
  color: var(--text-muted);
  font-size: 0.875rem;
}
"""

TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <title>{title} - SecAI Radar Wiki</title>
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <style>{css}</style>
</head>
<body>
  <header>
    <h1>SecAI Radar</h1>
    <nav>
      <a href="index.html">Home</a>
      <a href="Getting-Started.html">Getting Started</a>
      <a href="User-Guide.html">User Guide</a>
      <a href="API-Reference.html">API</a>
    </nav>
  </header>
  <main>{body}</main>
  <footer><p>SecAI Radar Documentation • Command Center Interface</p></footer>
</body>
</html>
"""


def rewrite_links(text: str) -> str:
    """Rewrite markdown links to HTML links."""
    pattern = re.compile(r"\[([^\]]+)\]\(([^\)]+)\)")
    
    def repl(match: re.Match) -> str:
        label, target = match.group(1), match.group(2)
        if target.startswith(('http://', 'https://', 'mailto:', '#')):
            return match.group(0)
        if target.endswith('.html'):
            return match.group(0)
        if target.endswith('.md'):
            target = target[:-3] + '.html'
            return f"[{label}]({target})"
        # Handle /wiki/ paths - remove /wiki/ prefix
        if target.startswith('/wiki/'):
            target = target[6:] + '.html'
            return f"[{label}]({target})"
        return f"[{label}]({target}.html)"
    
    return pattern.sub(repl, text)


def render_markdown(source: Path, destination: Path) -> None:
    """Render a markdown file to HTML."""
    text = source.read_text(encoding='utf-8')
    text = rewrite_links(text)
    
    # Extract title from first heading
    title_match = re.search(r'^#\s+(.+)', text, flags=re.MULTILINE)
    title = title_match.group(1).strip() if title_match else destination.stem
    
    # Convert to HTML
    html_body = markdown.markdown(
        text,
        extensions=['extra', 'toc', 'tables', 'fenced_code']
    )
    
    # Write output
    html = TEMPLATE.format(title=title, css=CSS, body=html_body)
    destination.write_text(html, encoding='utf-8')
    print(f"  Converted: {source.name} -> {destination.name}")


def main():
    """Build all markdown files in _site to HTML."""
    print("Building wiki HTML files...")
    
    for md_file in SITE_DIR.glob('*.md'):
        render_markdown(md_file, md_file.with_suffix('.html'))
    
    # Handle index.html
    index_html = SITE_DIR / 'index.html'
    index_md_html = SITE_DIR / 'index.html'  # Already converted from index.md
    home_html = SITE_DIR / 'Home.html'
    
    if (SITE_DIR / 'index.md').exists():
        # index.md was converted to index.html, we're good
        pass
    elif home_html.exists() and not index_html.exists():
        # Create redirect from index to Home
        redirect = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta http-equiv="refresh" content="0; url=Home.html" />
  <title>SecAI Radar Documentation</title>
</head>
<body>
  <p>Redirecting to <a href="Home.html">Home</a>...</p>
</body>
</html>
"""
        index_html.write_text(redirect, encoding='utf-8')
        print("  Created: index.html (redirect to Home.html)")
    
    print("Wiki build complete!")


if __name__ == '__main__':
    main()

