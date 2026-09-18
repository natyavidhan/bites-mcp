# bites-mcp

An [MCP](https://modelcontextprotocol.io) server that lets any MCP-compatible
AI agent (Claude Code, Claude Desktop, etc.) publish and manage pages on your
own [Bites](https://github.com/natyavidhan/Bites) deployment — "upload
whatever you generate" as a live URL, straight from the agent.

It's a thin wrapper around Bites' public REST API (`/api/v1/*`): every tool
call here is one HTTP request to your Bites app, authenticated with an API
key.

## Requirements

- A deployed Bites app with `API_KEY` set (see the
  [Bites README](https://github.com/natyavidhan/Bites#deploying-to-vercel)).
- Python 3.10+.

## Install

```bash
git clone https://github.com/natyavidhan/bites-mcp
cd bites-mcp
pip install .
```

This installs a `bites-mcp` command (the MCP server, stdio transport).

## Configure

The server reads two environment variables:

| Variable | Description |
|---|---|
| `BITES_URL` | Where your Bites app is deployed, e.g. `https://your-app.vercel.app` |
| `BITES_API_KEY` | Must match the `API_KEY` set on that Bites deployment |

### Claude Code

```bash
claude mcp add bites -e BITES_URL=https://your-app.vercel.app -e BITES_API_KEY=your-api-key -- bites-mcp
```

Or, without installing first, run it straight from the repo with `uv`:

```bash
claude mcp add bites -e BITES_URL=https://your-app.vercel.app -e BITES_API_KEY=your-api-key -- uvx --from git+https://github.com/natyavidhan/bites-mcp bites-mcp
```

### Claude Desktop / other MCP clients

Add to the client's MCP config (e.g. `claude_desktop_config.json`):

```jsonc
{
  "mcpServers": {
    "bites": {
      "command": "bites-mcp",
      "env": {
        "BITES_URL": "https://your-app.vercel.app",
        "BITES_API_KEY": "your-api-key"
      }
    }
  }
}
```

## Tools

| Tool | Description |
|---|---|
| `check_connection` | Verify `BITES_URL`/`BITES_API_KEY` are valid |
| `list_themes` | List available Markdown rendering themes |
| `list_sites` | List every site on the deployment |
| `get_site(slug_or_id)` | Get a site's full details, including raw content |
| `create_site(content, source_type, ...)` | Publish a new HTML or Markdown page, returns its live URL |
| `update_site(slug_or_id, ...)` | Edit, re-theme, rename, or (un)publish an existing site |
| `delete_site(slug_or_id)` | Permanently delete a site |

`create_site`/`update_site` accept the same fields as the Bites API: `title`,
`slug`, `markdown_theme`, `is_public`, `protected`, `protect_username`,
`protect_password` — see their docstrings (surfaced to the agent) or the
[Bites API docs](https://github.com/natyavidhan/Bites#public-api-apiv1) for
details.

## Local testing

```bash
pip install -e .
cp .env.example .env   # fill in BITES_URL / BITES_API_KEY
bites-mcp               # runs the stdio MCP server; .env is loaded automatically
```

Or exercise the underlying client directly without the MCP protocol:

```bash
python -c "from dotenv import load_dotenv; load_dotenv(); from bites_mcp.client import BitesClient; print(BitesClient().ping())"
```
