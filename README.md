# mcp-demo

MCP server for querying MCP Hub database

## Installation

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Configuration

Copy `.env.example` to `.env` and configure:

```bash
MCP_HUB_URL=http://localhost:8000/api/v1
VERIFY_SSL=true
```

## Run Server

```bash
# HTTP mode (default)
python -m src.main

# stdio mode
TRANSPORT_MODE=stdio python -m src.main
```

Server runs on `http://localhost:8080`

## Tools

- `search_mcp_servers` - Search for MCP servers by keyword
- `list_mcp_servers` - List MCP servers with pagination and sorting
- `get_mcp_server_details` - Get detailed information about a specific server
- `get_top_servers` - Get top servers by popularity or recency
- `get_top_contributors` - Get top contributors


## RooCode Setup

### HTTP Mode

Add to RooCode MCP settings (`cline_mcp_settings.json`):

```json
{
  "mcpServers": {
    "mcp-hub-mcp": {
      "transport": {
        "type": "sse",
        "url": "http://localhost:8080/sse"
      }
    }
  }
}
```

### stdio Mode

```json
{
  "mcpServers": {
    "mcp-hub-mcp": {
      "command": "python",
      "args": ["-m", "src.main"],
      "cwd": "/path/to/mcp-demo",
      "env": {
        "TRANSPORT_MODE": "stdio",
        "MCP_HUB_URL": "http://localhost:8000/api/v1"
      }
    }
  }
}
```

## Test

```bash
python test_all_tools.py
```
