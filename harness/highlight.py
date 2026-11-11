"""Syntax highlighting for the case pages' code, at build time: `highlight(code, path)` is the
code as HTML, escaped, its tokens in <span>s whose classes style.css colours:

  c comment (and a Python docstring), s string, n number, k keyword, b a constant (true, None, self, an ALL_CAPS name),
  t a type (a Capitalised name), f a function called or defined, m a macro or an attribute.

A language is told by the file's extension: Rust (.rs), Python (.py), Rhai (.rhai) and
Firmament (.firmament); any other file comes back escaped and nothing more. `loc(code, path)`
counts its lines of code by the same lexers, leaving out comments. A lexer here is a
list of patterns tried in order at each place, not a parser: it knows strings and comments from
code, and names by their spelling and by whether a `(` follows them. Standard library only."""
import html
import os
import re

RUST_KEYWORDS = """as async await break const continue crate dyn else enum extern fn for if impl in
    let loop match mod move mut pub ref return static struct super trait type unsafe use where
    while""".split()
PYTHON_KEYWORDS = """and as assert async await break class continue def del elif else except
    finally for from global if import in is lambda nonlocal not or pass raise return try while
    with yield""".split()
RHAI_KEYWORDS = """as break catch const continue do else export fn for if import in let loop
    private return switch throw try until while""".split()

NUMBER = r"\b(?:0[xob][0-9a-fA-F_]+|\d[\d_]*(?:\.\d[\d_]*|\.(?![.\w]))?(?:[eE][+-]?\d[\d_]*)?)"
BLOCK = r"/\*[\s\S]*?\*/"
DQ = r'"(?:\\[\s\S]|[^"\\])*"'  # may span lines, as Rust's and Rhai's do


def lexer(rules, keywords, constants):
    return re.compile("|".join(f"(?P<{name}>{pattern})" for name, pattern in rules)), \
        frozenset(keywords), frozenset(constants)


LEXERS = {
    ".rs": lexer([
        ("c", r"//[^\n]*|" + BLOCK),
        ("s", r'b?r(?P<hashes>#*)"[\s\S]*?"(?P=hashes)|b?' + DQ
              + r"|b?'(?:\\(?:u\{[0-9a-fA-F]+\}|x[0-9a-fA-F]{2}|.)|[^'\\\n])'"),
        ("m", r"#!?\[[^\]\n]*\]|\b[a-z_]\w*!(?!=)"),
        ("lifetime", r"'[A-Za-z_]\w*"),
        ("n", NUMBER + r"(?:_?(?:f32|f64|[iu](?:8|16|32|64|128|size)))?"),
        ("id", r"[A-Za-z_]\w*"),
    ], RUST_KEYWORDS, ["true", "false", "self", "Self"]),
    ".py": lexer([
        ("c", r"#[^\n]*"),
        ("s", r"(?i:[rbuf]{0,2})(?:\"\"\"[\s\S]*?\"\"\"|'''[\s\S]*?'''"
              r"|\"(?:\\.|[^\"\\\n])*\"|'(?:\\.|[^'\\\n])*')"),
        ("m", r"(?m:^[ \t]*@[\w.]+)"),
        ("n", NUMBER + "j?"),
        ("id", r"[A-Za-z_]\w*"),
    ], PYTHON_KEYWORDS, ["True", "False", "None", "self", "cls"]),
    ".rhai": lexer([
        ("c", r"//[^\n]*|" + BLOCK),
        ("s", DQ + r"|`[^`]*`|'(?:\\.|[^'\\\n])'"),
        ("n", NUMBER),
        ("id", r"[A-Za-z_]\w*"),
    ], RHAI_KEYWORDS, ["true", "false", "this"]),
    ".firmament": lexer([
        ("c", r"//[^\n]*|" + BLOCK),
        ("s", DQ),
        ("n", NUMBER + r"(?:[a-zA-Z]+\b)?"),  # a length or an angle with its unit: 5mm, 90deg
        ("id", r"[A-Za-z_]\w*"),
    ], [], ["true", "false"]),
}


def kind(name, after, keywords, constants):
    """The class of the name `name`, `after` the code that follows it."""
    if name in keywords:
        return "k"
    if name in constants or (len(name) > 1 and name.isupper()):
        return "b"
    if name[0].isupper():
        return "t"
    if after.lstrip(" ").startswith("("):
        return "f"
    return None


def tokens(code, lex):
    """Each token of `code` by the lexer `lex`, in order: (start, end, class), the class one of the
    module docstring's or None for a plain name. A Python docstring is prose: a comment, `c`."""
    pattern, keywords, constants = lex
    for match in pattern.finditer(code):
        start, end = match.span()
        text = match.group()
        cls = next(c for c in ("c", "s", "m", "lifetime", "n", "id")
                   if c in match.re.groupindex and match.group(c) is not None)
        if cls == "lifetime":
            cls = "m"
        elif cls == "id":
            cls = kind(text, code[end:end + 40], keywords, constants)
        elif cls == "s" and text.startswith(('"""', "'''")) \
                and not code[code.rfind("\n", 0, start) + 1:start].strip():
            cls = "c"
        yield start, end, cls


def loc(code, path):
    """The lines of `code` that hold code: not blank, and not only comment (or a Python
    docstring). A file in no language known here counts its lines that are not blank."""
    lex = LEXERS.get(os.path.splitext(path)[1])
    if lex:
        kept, at = [], 0
        for start, end, cls in tokens(code, lex):
            if cls == "c":  # left out, its line breaks kept
                kept += [code[at:start], "\n" * code.count("\n", start, end)]
                at = end
        kept.append(code[at:])
        code = "".join(kept)
    return sum(1 for line in code.splitlines() if line.strip())


def highlight(code, path):
    lex = LEXERS.get(os.path.splitext(path)[1])
    if not lex:
        return html.escape(code)
    out, at = [], 0
    for start, end, cls in tokens(code, lex):
        out.append(html.escape(code[at:start]))
        token = html.escape(code[start:end])
        out.append(f"<span class={cls}>{token}</span>" if cls else token)
        at = end
    out.append(html.escape(code[at:]))
    return "".join(out)
