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

## Testing

### Unit Tests (Mock-based, no backend required)

Fast tests using mocks. Can run without backend server.

```bash
# Run all unit tests
pytest tests/unit/ -v

# Run specific unit test file
pytest tests/unit/test_client.py -v
pytest tests/unit/test_handlers.py -v
pytest tests/unit/test_schemas.py -v
```

### Integration Tests (Requires running backend)

Tests that call real API endpoints. Requires backend at `http://localhost:8000`.

```bash
# Run all integration tests
pytest tests/integration/ -v

# Run specific integration test
pytest tests/integration/test_client.py -v
```

### Run All Tests

```bash
# Run all tests (unit + integration)
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html
```

### Quick Manual Test

```bash
# Test all 5 tools manually
python test_all_tools.py
```
