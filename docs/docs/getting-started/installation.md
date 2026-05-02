# Installation

We have designed the installation to be as automatic as possible.

## Step 1: Install the Package

You can install CodeGraphContext using `pip` or run it instantly using `uvx`.

=== "uv (Recommended)"
    If you use [uv](https://github.com/astral-sh/uv), you can run CGC instantly without manual installation:
    ```bash
    uvx codegraphcontext --help
    ```
    *Tip: This is the fastest way to get started and ensures you always have the latest version.*

=== "pip"
    Open your terminal and run:
    ```bash
    pip install codegraphcontext
    ```
    *Tip: We recommend installing this in a virtual environment (venv) or globally via `pipx`.*

---

## Step 2: Database Setup

CGC requires a graph database backend. Choose **ONE** path below.

=== "Option A: LadybugDB (Default & Recommended)"
    **LadybugDB** (formerly LadybugDBDB) is an embedded, extremely fast graph database. It requires zero configuration and runs directly within the CGC process.
    
    *   **Installation:** `pip install real_ladybug`
    *   **Best for:** Local development, individual projects, and zero-ops setups.
    *   **Pros:** No external services, portable database files.
    
    *Note: LadybugDB is used as the default fallback for all devices.*

=== "Option B: FalkorDB (High Performance)"
    **FalkorDB** is a low-latency graph database. CGC supports both local (embedded) and remote instances.
    
    *   **Installation:** `pip install falkordblite` (Linux/macOS only)
    *   **Best for:** Large codebases and performance-critical queries.
    *   **Pros:** Industry-leading query performance.
    
    *Note: CGC automatically prefers FalkorDB Lite on supported devices (Unix/macOS with Python 3.12+).*

=== "Option C: Neo4j (Enterprise / Visual)"
    Neo4j is the industry-standard enterprise graph database.
    *   **Pros:** Powerful web-based Graph Browser (`localhost:7474`). Handles massive codebases perfectly.
    *   **Cons:** Heavier resource usage. Requires Docker or a separate service running in the background.

    1.  **Configure environment for Neo4j:**
        Create a `.env` file or export `CGC_GRAPH_BACKEND=neo4j` and `NEO4J_URI=bolt://localhost:7687` along with `NEO4J_USER` and `NEO4J_PASSWORD`.
    2.  **Start Neo4j via Docker:**
        ```bash
        docker run -d --name neo4j -p 7474:7474 -p 7687:7687 -e NEO4J_AUTH=neo4j/password neo4j:latest
        ```

---

## Step 3: Verify Installation

Let's make sure everything is talking to each other. Run the "Doctor" command for a health check:

```bash
cgc doctor
```

---

## Step 4: Configure AI Assistant (For MCP Users)

If you plan to use CodeGraphContext with **Cursor**, **Claude**, **Windsurf**, or **Kiro**, you must configure the MCP server.

### The Smart Way (Automatic Setup)
Run the following command to automatically configure your favorite IDE:
```bash
uvx codegraphcontext mcp setup
```
*(Or `cgc mcp setup` if already installed)*

### Manual Configuration
If you prefer manual setup, add it to your `claude_desktop_config.json`:
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

**Configuration Paths:**
*   **macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
*   **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`
*   **Linux:** `~/.config/Claude/claude_desktop_config.json`

---

### Step 5: Integration with Editors

1.  **Cursor:**
    *   Go to Cursor Settings > Features > MCP.
    *   Add a new server: type `command`, name it `CodeGraphContext`, and command `cgc mcp start`.

2.  **Claude Desktop:**
    *   Add the configuration to your `claude_desktop_config.json` (see paths above).
    *   Restart Claude Desktop.

3.  **Refresh your AI Tool:**
    *   Verify that tools like `analyze_code_relationships` or `find_code` are now available for the AI to use.
