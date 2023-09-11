import sys
import io
import base64

import mistune
from mistune.plugins.math import math

renderer_list = []
def renderer(ty):
    def renderer_inner(fun):
        renderer_list.append((ty, fun))
        return fun
    return renderer_inner

try:
    import matplotlib
    import matplotlib.figure as figure
    HAS_MATPLOTLIB = True
except:
    pass

# This isn't in the try block because of except: pass.
if HAS_MATPLOTLIB:
    @renderer(matplotlib.figure.Figure)
    def render_matplotlib(fig):
        """Render a matplotlib Figure as a static image."""
        stream = io.BytesIO()
        fig.savefig(stream, format = 'png')
        enc = base64.b64encode(stream.getvalue()).decode()
        return f'<img src="data:image/png;base64,{enc}" />'

@renderer(str)
def render_str(s):
    """Render a string as a paragraph."""
    s = mistune.escape(s)
    return f'<p>{s}</p>'

# Must be registered last!
@renderer(object)
def render_object(x):
    """Render a generic object."""
    if hasattr(x, '__mmd__'):
        return x.__mmd__()
    s = mistune.escape(repr(x))
    return f'<pre>{s}</pre>'

def render_any(x):
    """Dispatch renderers by type."""
    for ty, h in renderer_list:
        if isinstance(x, ty):
            return h(x)
    assert False, 'Unreachable in render_any()!'

class MyRenderer(mistune.HTMLRenderer):
    def __init__(self):
        super().__init__()
        self.g = {}
        self.title = None
        self.counter = 0

    def heading(self, text, level, **attrs):
        if self.title is None:
            self.title = text
        return super().heading(text, level, **attrs)

    def block_code(self, code, info = None):
        self.counter += 1
        block_nr = self.counter
        sys.stderr.write(f'Running block {block_nr}...\n')

        # Parse args
        args = []
        if info is not None:
            args = info.split(' ')
        class FLAGS:
            PLOT_GCF = False
        for a in args:
            if a == 'plot':
                FLAGS.PLOT_GCF = True
            else:
                sys.stderr.write(f'Unknown block flag: {a}\n')

        # Set up execution environment
        emitted = []
        class TNB:
            def emit(obj, name = None):
                if name is None:
                    name = f'Output {len(emitted)+1}'
                html = render_any(obj)
                emitted.append((name, html))
        self.g['tnb'] = TNB

        exec(code, self.g)

        if FLAGS.PLOT_GCF:
            import matplotlib.pyplot as plt
            TNB.emit(plt.gcf())

        # Combine multiple outputs into an accordion
        n = len(emitted)
        if n == 0:
            output = ''
        elif n == 1:
            output = emitted[0][1]
        else:
            output = ''.join([
                f'<details><summary>{name}</summary>{html}</details>'
                for name, html in emitted
            ])

        # Bind source and output into a "codeblock" div
        code_esc = mistune.escape(code)
        return f"""
        <div class="codeblock">
          <div><pre><code class="hljs language-python">{code_esc}</code></pre></div>
          <div class="output">{output}</div>
        </div>
        """

template = """
<!DOCTYPE html>
<html lang="en">
  <head>
    <script type="text/javascript" id="MathJax-script" async
      src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js">
    </script>

    <link href="https://cdn.jsdelivr.net/npm/prism-themes@v1.x/themes/prism-one-dark.css" rel="stylesheet" />

    <style>{css}</style>
    </style>

    <title>{title}</title>
  </head>

  <body>
    {body}

	<script src="https://cdn.jsdelivr.net/npm/prismjs@v1.x/components/prism-core.min.js"></script>
	<script src="https://cdn.jsdelivr.net/npm/prismjs@v1.x/plugins/autoloader/prism-autoloader.min.js"></script>
  </body>
</html>
"""

css = """
body {
  background: white;
  font-family: sans-serif;
  margin: 25px 25px 500px 25px;
  padding: 0 25px 0px 25px;
  border-style: none dashed none none;
  border-color: black;
  border-width: 2px;
  max-width: 1250px;
}

@media screen and (max-width: 1250px) {
  body {
    border-style: none;
    margin: 25px 10px 500px 10px;
    padding: 0px;
  }
}

img {
  display: block;
  margin: auto;
}

.codeblock {
  padding-left: 1em;
  margin-left: 1em;
  border-style: none none none solid;
  border-color: deepskyblue;
  border-width: 2px;
}

details {
  margin: .5em 0em .5em 0em;
  padding-left: .5em;
  border-style: none none none solid;
  border-color: lightcoral;
  border-width: 2px;
}

details[open] {
  border-color: limegreen;
}

summary {
  list-style: none;
  width: fit-content;
  border-radius: 10px;
  padding: .5em .5em .5em .5em;
}

summary:hover {
  background: lavender;
  cursor: pointer;
}

pre {
  background: gainsboro;
  padding: .5em 10em .5em .5em;
  border-radius: 0.3em;
}
"""

# Redirect sys.stdout to sys.stderr so that user execution can print() to
# the terminal without interrupting the HTML output.
stdout = sys.stdout
sys.stdout = sys.stderr

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

