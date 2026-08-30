# Building a Calculator MCP Server (Python SDK, no `uv`)

A step-by-step guide to building, testing, and connecting a simple two-tool
(`add`, `multiply`) MCP server to Claude Code, using the official Python MCP
SDK directly with `pip` (no `uv`).

---

## Step 1 — Set up your project folder

```bash
mkdir calculator-mcp
cd calculator-mcp
python3 -m venv venv
source venv/bin/activate      # on WSL/Linux/Mac
# .\venv\Scripts\activate     # on native Windows cmd/powershell
```

A virtual environment isn't strictly required, but it keeps this package
isolated from anything else on your system — good habit for MCP
experiments.

---

## Step 2 — Install the SDK (no `uv`)

```bash
pip install "mcp[cli]"
```

- `mcp` is the core SDK — the classes and machinery that speak the MCP
  protocol.
- The `[cli]` extra pulls in a few extra dependencies that give you the
  `mcp` command-line tool, used to test the server locally.

---

## Step 3 — Write `server.py`

```python
from mcp.server import MCPServer

mcp = MCPServer("Calculator")

@mcp.tool()
def add(a: float, b: float) -> float:
    """Add two numbers together."""
    return a + b

@mcp.tool()
def multiply(a: float, b: float) -> float:
    """Multiply two numbers together."""
    return a * b

if __name__ == "__main__":
    mcp.run()
```

### Line-by-line explanation

| Line | What it means |
|---|---|
| `from mcp.server import MCPServer` | Imports the `MCPServer` class — the object that knows how to speak the MCP protocol so you don't have to write any of that plumbing yourself. |
| `mcp = MCPServer("Calculator")` | Creates your server and names it `"Calculator"`. This name shows up when a host (like Claude Code) lists connected servers. |
| `@mcp.tool()` | A **decorator** placed above a function. It tells the SDK "expose the function below as a tool the AI model can call." |
| `def add(a: float, b: float) -> float:` | A normal Python function named `add`, taking two numbers and returning a number. |
| `a: float, b: float` | Type hints. The SDK reads these directly to build the tool's input schema — no manual JSON Schema needed. |
| `"""Add two numbers together."""` | The docstring. This becomes the tool's **description**, which the model reads to decide *when* to call the tool. Always write a clear one. |
| `return a + b` | The actual logic — plain Python. |
| `@mcp.tool()` / `def multiply(...)` | Same pattern, second tool, multiplication instead of addition. |
| `if __name__ == "__main__":` | Standard Python guard — only run the code below when this file is executed directly (`python server.py`), not when it's imported. |
| `mcp.run()` | Starts the server using **stdio transport**: it reads MCP protocol messages from standard input and writes responses to standard output. No port, no URL — the host launches this as a child process and owns those two pipes. |

---

## Step 4 — Test it standalone (optional but useful)

Before wiring it into Claude Code, sanity-check it with the MCP Inspector
(a small web UI):

```bash
mcp dev server.py
```

This opens a browser tab. Go to **Tools**, you'll see `add` and
`multiply`, each with a form built automatically from your type hints.
Try `add` with `a=2, b=3` → you should get `5` back. `Ctrl-C` to stop it
when done.

(Needs Node's `npx` on your `PATH`, since the Inspector itself is a Node
app. Skip this step and go straight to Claude Code if you don't have
Node installed.)

---

## Step 5 — Connect it to Claude Code

No config file to hand-edit necessarily — you can register it with the
`claude` CLI:

```bash
claude mcp add calculator -- python3 /absolute/path/to/server.py
```

Or add it directly to your project's `.mcp.json`:

```json
{
  "mcpServers": {
    "calculator-mcp-server": {
      "type": "stdio",
      "command": "python3",
      "args": [
        "/absolute/path/to/calculator-mcp-server/server.py"
      ]
    }
  }
}
```

Key points:

- **Use an absolute path**, not `server.py` — Claude Code may launch the
  process from a different working directory, and a relative path will
  fail to find the file.
- **`python3`, not `python`** — on most WSL/Ubuntu setups there's no
  `python` binary on `PATH` at all, only `python3`.
- **The interpreter must actually have `mcp` installed.** Claude Code
  launches this as a bare subprocess — it does **not** inherit your
  activated shell. If you installed `mcp` inside a venv, point `command`
  at that venv's Python directly:
  ```json
  "command": "/absolute/path/to/calculator-mcp-server/venv/bin/python3"
  ```
  Run `which python3` from inside your activated venv to get the exact
  path.
- **No trailing comma** on the last entry inside `mcpServers` — JSON
  doesn't allow it, and it's one of the most common causes of a silently
  broken config.

---

## Step 6 — Verify and use it

Inside a Claude Code session, run:

```
/mcp
```

You should see `calculator` (or `calculator-mcp-server`) listed as
connected, with `add` and `multiply` as its tools. Then just ask
something like "add 12 and 30" or "what's 7 times 8" — Claude Code will
call your tool and return the real, computed result.

---

## Troubleshooting

If the server doesn't show up or shows as disconnected:

1. **Run the launch command by hand first**, exactly as it appears in
   your config:
   ```bash
   python3 /absolute/path/to/server.py
   ```
   Nothing should print, and it shouldn't return — that silence is
   correct (it's waiting for a host to speak over stdin). A traceback or
   an immediate exit tells you the real bug directly, instead of
   guessing at it through Claude Code.
2. **Check for a relative path** in your config — the single most common
   failure.
3. **Never let anything but the SDK write to stdout.** On stdio,
   stdout *is* the protocol — a stray `print()` will corrupt the
   connection. Use Python's `logging` module (defaults to stderr)
   instead if you need debug output.
4. **Restart Claude Code** after editing `.mcp.json` — config is read at
   launch.