import sys
import io
import base64
import inspect

import mistune

# Command-line args passed through to the .md file.
argv = []

renderer_dict = {}
def renderer(ty):
    """Decorator to declare a renderer.

    Will be applied to all sub-classes unless overridden.

    Parameters:
    - ty: the type to be rendered
    """
    def renderer_inner(fun):
        renderer_dict[ty] = fun
        return fun
    return renderer_inner

try:
    import matplotlib.figure
    @renderer(matplotlib.figure.Figure)
    def render_matplotlib(fig):
        """Render a matplotlib Figure as a static image."""
        stream = io.BytesIO()
        fig.savefig(stream, format = 'png')
        enc = base64.b64encode(stream.getvalue()).decode()
        return f'<img src="data:image/png;base64,{enc}" />'
except ImportError:
    pass

@renderer(str)
def render_str(s):
    """Render a string as a paragraph."""
    s = mistune.escape(s)
    return f'<p>{s}</p>'

def render_any(x):
    """Dispatch renderers by type."""

    # __tnb__ overrides all the default renderers, since it will always
    # be provided by the user.
    # (E.g., consider a subclass of a matplotlib Figure.)
    if hasattr(x, '__tnb__'):
        return x.__tnb__()

    # Search for renderers for all parent classes, most-specific first
    mro = inspect.getmro(type(x))
    for ty in mro:
        if ty in renderer_dict:
            f = renderer_dict[ty]
            return f(x)

    # Default case.
    s = mistune.escape(repr(x))
    return f'<pre>{s}</pre>'

emitted = []
def emit(x, name = None):
    """Emit an object to be rendered."""
    if name is None:
        name = f'Output {len(emitted)+1}'
    html = render_any(x)
    emitted.append((name, html))

class MyRenderer(mistune.HTMLRenderer):
    def __init__(self):
        super().__init__()
        self.g = {}
        self.title = None
        self.counter = 0
        self.inline_counter = 0

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
        emitted.clear()
        exec(code, self.g)

        if FLAGS.PLOT_GCF:
            import matplotlib.pyplot as plt
            emit(plt.gcf())

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

    def codespan(self, text):
        self.inline_counter += 1
        block_nr = self.inline_counter
        sys.stderr.write(f'Running inline block {block_nr}...\n')

        # Set up execution environment
        emitted.clear()
        result = eval(text, self.g)

        if len(emitted) != 0:
            sys.stderr.write(f'Inline block emitted {len(emitted)} unexpected outputs! (Ignoring.)')

        return str(result)


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
  max-width: 1000px;
}

@media screen and (max-width: 1000px) {
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

