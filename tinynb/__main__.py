import sys

import mistune
from mistune.plugins.math import math

from .tinynb import (
    MyRenderer,
    template,
    css,
    argv
)

# Redirect sys.stdout to sys.stderr so that user execution can print() to
# the terminal without interrupting the HTML output.
stdout = sys.stdout
sys.stdout = sys.stderr

# Parse args and fill tinynb.argv with the unrecognized arguments.
argv += sys.argv[1:]

renderer = MyRenderer()
markdown = mistune.Markdown(
    renderer = renderer,
    plugins = [math]
)
body = markdown(sys.stdin.read())
stdout.write(template.format(
    title = renderer.title if renderer.title else 'Untitled',
    css = css,
    body = body
))

