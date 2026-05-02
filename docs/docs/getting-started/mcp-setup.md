# MCP Setup Guide

The Model Context Protocol (MCP) is the bridge between your AI assistant and CodeGraphContext.

## The Smartest Way to Setup

The fastest and most reliable way to configure CodeGraphContext for your IDE is using `uvx`. This command will automatically detect your installed editors and configure the MCP server for you.

```bash
uvx codegraphcontext mcp setup
```

**What this does:**
1. **Detects Clients:** Scans for Claude Desktop, Cursor, Windsurf, VS Code, and more.
2. **Injects Config:** Automatically adds the necessary JSON configuration to your editor's settings.
3. **Validates Environment:** Ensures your database (LadybugDB or FalkorDB) is ready to use.

---

## Supported Clients & Configuration Paths

If the automatic setup doesn't work for your specific environment, you can manually configure the server using the paths below:

| OS | Claude Desktop Config Path |
| :--- | :--- |
| **macOS** | `~/Library/Application Support/Claude/claude_desktop_config.json` |
| **Windows** | `%APPDATA%\Claude\claude_desktop_config.json` |
| **Linux** | `~/.config/Claude/claude_desktop_config.json` |

### Manual JSON Entry
Add this to your `mcpServers` block:

```json
{
  "mcpServers": {
    "CodeGraphContext": {
      "command": "cgc",
      "args": ["mcp", "start"]
    }
  }
}
```

---

## Verifying the Setup

Once configured, restart your AI assistant and look for the following tools:
* `analyze_callers`
* `find_code_definitions`
* `get_code_context`

If you see these tools, your AI is now powered by the CodeGraphContext!

---

## Troubleshooting

* **Command not found:** Ensure `codegraphcontext` is in your PATH, or use `uvx codegraphcontext`.
* **Database error:** Run `cgc doctor` to check your backend health.
* **Linux Users:** If using a flatpak or snap version of Claude/Cursor, paths may vary. Check the official documentation for your specific installation method.
