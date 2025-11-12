# MCP 서버 만들기 Codelab

> **소요 시간**: 약 60분
> **난이도**: 초급~중급
> **사전 지식**: Python 기본, REST API 개념

MCP(Model Context Protocol)의 핵심 개념을 이해하고, 실제로 동작하는 MCP 서버를 처음부터 만들어봅니다.

---

## 📚 목차

1. [MCP란 무엇인가?](#1-mcp란-무엇인가)
2. [MCP의 핵심 개념](#2-mcp의-핵심-개념)
3. [실습 준비](#3-실습-준비)
4. [첫 번째 MCP 서버 만들기](#4-첫-번째-mcp-서버-만들기)
5. [실전 프로젝트: MCP Hub 서버](#5-실전-프로젝트-mcp-hub-서버)
6. [Claude Desktop 연동](#6-claude-desktop-연동)

---

## 1. MCP란 무엇인가?

### 1.1 왜 MCP가 필요한가?

```
문제:
- AI 모델(Claude, GPT)은 학습 시점의 데이터만 알고 있음
- 실시간 정보 접근 불가 (날씨, 최신 뉴스, DB 데이터 등)
- 사용자별 개인 데이터 접근 불가 (파일, 이메일 등)

해결:
MCP = AI 모델과 외부 세계를 연결하는 표준 프로토콜
```

### 1.2 MCP의 구조

```
┌─────────────────┐
│   AI Model      │  ← Claude 같은 AI 모델
│   (Client)      │
└────────┬────────┘
         │ MCP Protocol
         │ (표준 통신 규약)
┌────────▼────────┐
│   MCP Server    │  ← 우리가 만들 것!
│                 │
└────────┬────────┘
         │ HTTP/DB/File/CLI
┌────────▼────────┐
│   Data Source   │  ← 실제 데이터
│                 │
└─────────────────┘
```

### 1.3 실제 사용 예시

**시나리오: MCP Hub 검색**
```
사용자: "GitHub 관련 MCP 서버를 찾아줘"
  ↓
Claude: MCP 서버의 search_mcp_servers tool 호출
  ↓
MCP 서버: MCP Hub API 호출
  ↓
Claude: "GitHub 관련 MCP 서버 5개를 찾았습니다. 첫 번째는..."
```

---

## 2. MCP의 핵심 개념

### 2.1 Tools (도구)

**정의**: AI 모델이 **실행**할 수 있는 함수

**특징**:
- 동작을 수행 (검색, 조회, 생성 등)
- 입력 파라미터를 받을 수 있음
- 결과를 반환

**예시**:
```python
Tool(
    name="search_mcp_servers",
    description="MCP 서버를 키워드로 검색합니다",
    inputSchema={
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "검색 키워드"}
        },
        "required": ["query"]
    }
)
```

**언제 사용하나?**
- ✅ 검색, 조회 작업
- ✅ 외부 API 호출
- ✅ 데이터 생성/수정

### 2.2 Transport (통신 방식)

MCP 서버와 AI 모델이 **어떻게** 통신할지 정의합니다.

#### 주요 Transport 방식

**1. stdio (Standard Input/Output)**
```
┌──────────────┐
│ Claude       │
│ Desktop      │
└──────┬───────┘
       │ stdin/stdout
┌──────▼───────┐
│ MCP Server   │
│ (로컬 실행)   │
└──────────────┘
```

- ✅ 로컬 환경에서 실행
- ✅ 설정 간단
- ❌ 원격 접근 불가

**2. HTTP/SSE (Server-Sent Events)**
```
┌──────────────┐
│ Claude       │
│ Desktop      │
└──────┬───────┘
       │ HTTP(S)
┌──────▼───────┐
│ MCP Server   │
│ (웹 서버)     │
└──────────────┘
```

- ✅ 원격 접근 가능
- ✅ 다중 클라이언트 지원
- ✅ 디버깅 용이

**Transport 선택 가이드**:

| 상황 | stdio | HTTP/SSE |
|-----|-------|----------|
| 개인 사용 | ⭐ 추천 | - |
| 팀 공유 | ❌ | ⭐ 추천 |
| 로컬 파일 접근 | ⭐ 필수 | - |
| 순수 API 호출 | - | ⭐ 추천 |

### 2.3 Resources와 Prompts (이번 실습에서는 다루지 않음)

- **Resources**: AI가 읽을 수 있는 데이터 (파일, 문서 등)
- **Prompts**: 재사용 가능한 프롬프트 템플릿

---

## 3. 실습 준비

### 3.1 환경 설정

```bash
# 프로젝트 디렉토리 생성
mkdir mcp-demo
cd mcp-demo

# 가상환경 생성 및 활성화
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 파일 생성
cat > requirements.txt <<EOF
mcp>=0.9.0
httpx>=0.27.0
uvicorn>=0.30.0
starlette>=0.37.0
sse-starlette>=2.1.0
EOF

# 설치
pip install -r requirements.txt
```

### 3.2 프로젝트 구조

```
mcp-demo/
├── src/
│   ├── main.py           # 메인 진입점
│   ├── client/           # API 클라이언트
│   │   └── api_client.py
│   ├── schemas/          # Tool 정의
│   │   └── tools.py
│   ├── handlers/         # Tool 실행 로직
│   │   └── tools.py
│   └── transport/        # 통신 프로토콜
│       └── http.py
└── requirements.txt
```

---

## 4. 첫 번째 MCP 서버 만들기

### 4.1 Hello World MCP 서버

가장 간단한 MCP 서버를 만들어봅시다.

`hello_mcp.py` 생성:

```python
#!/usr/bin/env python3
"""최소 MCP 서버 - Hello World"""
import asyncio
import logging
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("hello-mcp")

# MCP 서버 생성
app = Server("hello-mcp")


@app.list_tools()
async def list_tools() -> list[Tool]:
    """사용 가능한 도구 목록"""
    return [
        Tool(
            name="say_hello",
            description="인사를 합니다",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "이름"
                    }
                },
                "required": ["name"]
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """도구 실행"""
    if name == "say_hello":
        user_name = arguments.get("name", "World")
        message = f"안녕하세요, {user_name}님!"
        return [TextContent(type="text", text=message)]

    return [TextContent(type="text", text=f"Unknown tool: {name}")]


async def main():
    """메인 함수"""
    async with stdio_server() as (read_stream, write_stream):
        logger.info("Hello MCP Server started!")
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
```

### 4.2 코드 이해하기

#### 1. Server 생성
```python
app = Server("hello-mcp")
```
- MCP 서버 인스턴스 생성
- "hello-mcp"는 서버 식별자

#### 2. Tools 정의 (`@app.list_tools()`)
```python
@app.list_tools()
async def list_tools() -> list[Tool]:
    return [Tool(...)]
```
- Claude가 사용할 수 있는 도구 목록 정의
- 각 Tool은 이름, 설명, 입력 스키마를 포함

#### 3. Tool 실행 (`@app.call_tool()`)
```python
@app.call_tool()
async def call_tool(name: str, arguments: dict):
    # 도구 실행 로직
```
- Claude가 도구를 호출하면 실행되는 함수
- `name`: 도구 이름
- `arguments`: 입력 파라미터

#### 4. Transport (stdio)
```python
async with stdio_server() as (read_stream, write_stream):
    await app.run(read_stream, write_stream, ...)
```
- 표준 입출력으로 통신
- 로컬에서 Claude Desktop과 연동 가능

### 4.3 테스트

```bash
python hello_mcp.py
```

서버가 실행되면 대기 상태가 됩니다. (Claude Desktop과 연결 전)

---

## 5. 실전 프로젝트: MCP Hub 서버

이제 실제로 유용한 MCP 서버를 만들어봅시다!

**목표**: MCP Hub 데이터베이스를 검색하는 MCP 서버

**제공 기능**:
- `search_mcp_servers`: 키워드로 MCP 서버 검색
- `list_mcp_servers`: 서버 목록 조회 (정렬, 페이징)
- `get_mcp_server_details`: 서버 상세 정보
- `get_top_contributors`: 상위 기여자 조회

**데이터 소스**: MCP Hub REST API (`http://localhost:8000`)

**Transport**: HTTP/SSE

### 5.1 프로젝트 구조 만들기

```bash
mkdir -p src/{client,schemas,handlers,transport}
touch src/__init__.py
touch src/client/__init__.py
touch src/schemas/__init__.py
touch src/handlers/__init__.py
touch src/transport/__init__.py
```

### 5.2 Step 1: Tool 정의하기

`src/schemas/tools.py`:

```python
"""Tool definitions for MCP Hub MCP Server"""
from mcp.types import Tool

TOOLS = [
    Tool(
        name="search_mcp_servers",
        description="Search for MCP servers by keyword",
        inputSchema={
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search keyword"
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of results",
                    "default": 10
                }
            },
            "required": ["query"]
        }
    ),
    Tool(
        name="list_mcp_servers",
        description="List MCP servers with sorting and pagination",
        inputSchema={
            "type": "object",
            "properties": {
                "sort": {
                    "type": "string",
                    "enum": ["favorites", "created_at"],
                    "description": "Sort by favorites or creation date",
                    "default": "favorites"
                },
                "order": {
                    "type": "string",
                    "enum": ["asc", "desc"],
                    "description": "Sort order",
                    "default": "desc"
                },
                "limit": {
                    "type": "integer",
                    "description": "Number of results",
                    "default": 20
                }
            }
        }
    ),
    Tool(
        name="get_mcp_server_details",
        description="Get detailed information about a specific MCP server",
        inputSchema={
            "type": "object",
            "properties": {
                "server_id": {
                    "type": "integer",
                    "description": "The server ID"
                }
            },
            "required": ["server_id"]
        }
    ),
    Tool(
        name="get_top_contributors",
        description="Get list of top contributors",
        inputSchema={
            "type": "object",
            "properties": {
                "limit": {
                    "type": "integer",
                    "description": "Number of contributors to return",
                    "default": 10
                }
            }
        }
    ),
]
```

**핵심 포인트**:
- `name`: 도구 이름 (함수명 스타일)
- `description`: Claude가 언제 이 도구를 사용할지 이해할 수 있는 명확한 설명
- `inputSchema`: JSON Schema로 입력 검증
  - `type`: 데이터 타입
  - `enum`: 허용된 값 목록
  - `default`: 기본값
  - `required`: 필수 필드

### 5.3 Step 2: API 클라이언트 구현

`src/client/api_client.py`:

```python
"""API client for MCP Hub"""
import logging
from typing import Optional, Dict, Any
import httpx

logger = logging.getLogger("mcp-hub-mcp.api_client")


class APIClient:
    """Client for accessing MCP Hub REST API"""

    def __init__(self, api_base_url: str = "http://localhost:8000"):
        self.api_base_url = api_base_url.rstrip('/')
        # SSL 검증 비활성화 (사내 서비스용)
        self.client = httpx.AsyncClient(
            timeout=30.0,
            verify=False  # SSL 에러 방지
        )

    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()

    async def _get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make a GET request to the API"""
        url = f"{self.api_base_url}{endpoint}"
        try:
            logger.debug(f"GET {url} with params: {params}")
            response = await self.client.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error: {e.response.status_code}")
            return {"error": f"HTTP {e.response.status_code}"}
        except Exception as e:
            logger.error(f"Request error: {str(e)}")
            return {"error": str(e)}

    async def search_servers(self, query: str, limit: int = 10) -> str:
        """Search for MCP servers"""
        # MCP Hub API는 검색을 지원하지 않으므로 전체 목록에서 필터링
        params = {"status": "approved", "limit": 100}
        data = await self._get("/api/v1/mcp-servers/", params)

        if "error" in data:
            return f"Error: {data['error']}"

        servers = data.get("items", [])

        # 키워드로 필터링
        filtered = [
            s for s in servers
            if query.lower() in s.get("name", "").lower()
            or query.lower() in s.get("description", "").lower()
        ][:limit]

        if not filtered:
            return f"No servers found matching '{query}'"

        result = f"Found {len(filtered)} server(s) matching '{query}':\n\n"
        for server in filtered:
            result += f"ID: {server['id']}\n"
            result += f"Name: {server['name']}\n"
            result += f"Description: {server.get('description', 'N/A')}\n"
            result += f"Favorites: {server.get('favorites_count', 0)}\n"
            result += "-" * 60 + "\n\n"

        return result

    async def list_servers(
        self,
        sort: str = "favorites",
        order: str = "desc",
        limit: int = 20
    ) -> str:
        """List MCP servers with sorting"""
        params = {
            "status": "approved",
            "sort": sort,
            "order": order,
            "limit": limit,
            "offset": 0
        }
        data = await self._get("/api/v1/mcp-servers/", params)

        if "error" in data:
            return f"Error: {data['error']}"

        servers = data.get("items", [])
        total = data.get("total", 0)

        result = f"Total servers: {total}\n"
        result += f"Showing {len(servers)} servers (sorted by {sort}, {order}):\n\n"

        for server in servers:
            result += f"ID: {server['id']}\n"
            result += f"Name: {server['name']}\n"
            result += f"Description: {server.get('description', 'N/A')}\n"
            result += f"Favorites: {server.get('favorites_count', 0)}\n"
            result += "-" * 60 + "\n\n"

        return result

    async def get_server_details(self, server_id: int) -> str:
        """Get detailed information about a server"""
        data = await self._get(f"/api/v1/mcp-servers/{server_id}")

        if "error" in data:
            return f"Error: {data['error']}"

        result = f"Server Details (ID: {server_id}):\n\n"
        result += f"Name: {data.get('name', 'N/A')}\n"
        result += f"Description: {data.get('description', 'N/A')}\n"
        result += f"Repository: {data.get('repository_url', 'N/A')}\n"
        result += f"Author: {data.get('username', 'N/A')}\n"
        result += f"Status: {data.get('status', 'N/A')}\n"
        result += f"Favorites: {data.get('favorites_count', 0)}\n"
        result += f"Created: {data.get('created_at', 'N/A')}\n"

        return result

    async def get_top_contributors(self, limit: int = 10) -> str:
        """Get top contributors"""
        params = {"limit": limit}
        data = await self._get("/api/v1/mcp-servers/top-users", params)

        if "error" in data:
            return f"Error: {data['error']}"

        contributors = data.get("top_users", [])

        result = f"Top {len(contributors)} Contributors:\n\n"
        for i, contributor in enumerate(contributors, 1):
            result += f"{i}. {contributor.get('username', 'N/A')}\n"
            result += f"   Total Servers: {contributor.get('total_servers', 0)}\n"
            result += f"   Total Favorites: {contributor.get('total_favorites', 0)}\n\n"

        return result
```

**핵심 포인트**:
- `httpx.AsyncClient`: 비동기 HTTP 클라이언트 (MCP는 비동기 기반)
- `verify=False`: SSL 인증서 검증 비활성화 (사내 서비스용)
- 에러 처리: `try-except`로 네트워크 에러 핸들링
- 응답 포맷팅: Claude가 읽기 좋은 문자열로 변환

### 5.4 Step 3: Tool Handler 구현

`src/handlers/tools.py`:

```python
"""Tool handlers for MCP Hub MCP Server"""
import logging
from typing import Any
from mcp.types import TextContent

logger = logging.getLogger("mcp-hub-mcp.handlers")


async def _search_mcp_servers(api_client, arguments: dict[str, Any]) -> str:
    """Search MCP servers"""
    return await api_client.search_servers(
        query=arguments["query"],
        limit=arguments.get("limit", 10)
    )


async def _list_mcp_servers(api_client, arguments: dict[str, Any]) -> str:
    """List MCP servers"""
    return await api_client.list_servers(
        sort=arguments.get("sort", "favorites"),
        order=arguments.get("order", "desc"),
        limit=arguments.get("limit", 20)
    )


async def _get_mcp_server_details(api_client, arguments: dict[str, Any]) -> str:
    """Get MCP server details"""
    return await api_client.get_server_details(
        server_id=arguments["server_id"]
    )


async def _get_top_contributors(api_client, arguments: dict[str, Any]) -> str:
    """Get top contributors"""
    return await api_client.get_top_contributors(
        limit=arguments.get("limit", 10)
    )


# Tool handler mapping
TOOL_HANDLERS = {
    "search_mcp_servers": _search_mcp_servers,
    "list_mcp_servers": _list_mcp_servers,
    "get_mcp_server_details": _get_mcp_server_details,
    "get_top_contributors": _get_top_contributors,
}


async def handle_tool_call(name: str, arguments: Any, api_client) -> list[TextContent]:
    """
    Handle tool calls from MCP clients

    Args:
        name: Tool name
        arguments: Tool arguments
        api_client: API client instance

    Returns:
        List of TextContent responses
    """
    if api_client is None:
        return [TextContent(type="text", text="Error: API client not initialized")]

    try:
        handler = TOOL_HANDLERS.get(name)
        if handler is None:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]

        result = await handler(api_client, arguments)
        return [TextContent(type="text", text=result)]

    except Exception as e:
        logger.error(f"Error calling tool {name}: {e}", exc_info=True)
        return [TextContent(type="text", text=f"Error: {str(e)}")]
```

**핵심 포인트**:
- **Dict 기반 라우팅**: `TOOL_HANDLERS` 딕셔너리로 도구 이름을 핸들러 함수에 매핑
- **각 도구를 별도 함수로**: 단일 책임 원칙, 테스트 용이
- **응답 형식**: 반드시 `list[TextContent]` 반환 (MCP 스펙)

### 5.5 Step 4: HTTP Transport 구현

`src/transport/http.py`:

```python
"""HTTP/SSE transport for MCP Hub MCP Server"""
import asyncio
import logging
import os

logger = logging.getLogger("mcp-hub-mcp.transport.http")


async def run_http_transport(app, api_client) -> None:
    """
    Run server with HTTP/SSE transport

    Args:
        app: MCP Server instance
        api_client: API client instance
    """
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "10004"))
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()

    try:
        from mcp.server.sse import SseServerTransport
        from starlette.applications import Starlette
        from starlette.routing import Route
        from starlette.responses import JSONResponse
        import uvicorn

        # Health check endpoint
        async def health_check(request):
            return JSONResponse({
                "status": "healthy",
                "service": "mcp-hub-mcp",
                "transport": "http/sse",
                "port": port
            })

        # SSE Transport 생성
        sse = SseServerTransport("/messages")

        # Starlette 앱 생성
        starlette_app = Starlette(
            routes=[
                Route("/health", health_check),
                *sse.get_routes()
            ]
        )

        logger.info(f"Starting MCP Hub MCP Server on {host}:{port} (HTTP/SSE)")

        async def run_server():
            """Run uvicorn server"""
            config = uvicorn.Config(
                starlette_app,
                host=host,
                port=port,
                log_level=log_level.lower()
            )
            server = uvicorn.Server(config)
            await server.serve()

        async def run_mcp():
            """Run MCP protocol handler"""
            async with sse.connect_sse(
                starlette_app.app,
                app.create_initialization_options()
            ) as streams:
                await app.run(
                    streams[0],
                    streams[1],
                    app.create_initialization_options()
                )

        # 서버와 MCP 핸들러 동시 실행
        await asyncio.gather(run_server(), run_mcp())

    except ImportError as e:
        logger.error(f"HTTP transport dependencies not installed: {e}")
        raise
    finally:
        if api_client:
            await api_client.close()
            logger.info("API client closed")
```

**핵심 포인트**:
- **SSE (Server-Sent Events)**: 실시간 양방향 통신 지원
- **Health Check**: `/health` 엔드포인트로 서버 상태 확인
- **asyncio.gather**: 웹 서버와 MCP 핸들러를 동시에 실행

### 5.6 Step 5: 메인 진입점 구현

`src/main.py`:

```python
#!/usr/bin/env python3
"""MCP Hub MCP Server - Main Entry Point"""
import asyncio
import logging
import os
from mcp.server import Server

from client.api_client import APIClient
from schemas.tools import TOOLS
from handlers.tools import handle_tool_call
from transport.http import run_http_transport

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("mcp-hub-mcp")


async def main():
    """Main function"""
    # MCP Hub URL 설정
    api_base_url = os.getenv("MCP_HUB_URL", "http://localhost:8000")

    # API Client 생성
    api_client = APIClient(api_base_url)
    logger.info(f"API client initialized with base URL: {api_base_url}")

    # MCP Server 생성
    app = Server("mcp-hub-mcp")

    @app.list_tools()
    async def list_tools():
        """Return list of available tools"""
        return TOOLS

    @app.call_tool()
    async def call_tool(name: str, arguments: dict):
        """Handle tool calls"""
        return await handle_tool_call(name, arguments, api_client)

    # HTTP Transport로 실행
    await run_http_transport(app, api_client)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}", exc_info=True)
```

**핵심 포인트**:
- **환경 변수**: `MCP_HUB_URL`로 API 엔드포인트 설정
- **데코레이터**: `@app.list_tools()`, `@app.call_tool()`로 핸들러 등록
- **모듈화**: 각 기능을 별도 모듈로 분리하여 관리

### 5.7 실행 및 테스트

#### 1. 서버 실행

```bash
cd src
python main.py
```

출력:
```
INFO - API client initialized with base URL: http://localhost:8000
INFO - Starting MCP Hub MCP Server on 0.0.0.0:10004 (HTTP/SSE)
```

#### 2. Health Check

다른 터미널에서:
```bash
curl http://localhost:10004/health
```

출력:
```json
{
  "status": "healthy",
  "service": "mcp-hub-mcp",
  "transport": "http/sse",
  "port": 10004
}
```

---

## 6. Claude Desktop 연동

### 6.1 Claude Desktop 설정 파일 위치

**macOS:**
```
~/Library/Application Support/Claude/claude_desktop_config.json
```

**Windows:**
```
%APPDATA%\Claude\claude_desktop_config.json
```

**Linux:**
```
~/.config/Claude/claude_desktop_config.json
```

### 6.2 HTTP Transport 연결 설정

`claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "mcp-hub": {
      "url": "http://localhost:10004/messages",
      "transport": "sse"
    }
  }
}
```

### 6.3 Claude Desktop 재시작

설정 파일을 저장한 후 Claude Desktop을 완전히 종료하고 다시 시작합니다.

### 6.4 MCP 서버 연결 확인

Claude Desktop에서 MCP 서버가 연결되었는지 확인:
1. 우측 하단의 🔌 아이콘 클릭
2. "mcp-hub" 서버가 목록에 표시되는지 확인
3. 연결 상태가 "Connected"인지 확인

### 6.5 테스트 질문

Claude Desktop에서 다음과 같이 질문해보세요:

```
1. "MCP 서버 목록을 보여줘"

2. "GitHub 관련 MCP 서버를 검색해줘"

3. "인기 있는 MCP 서버 상위 5개를 보여줘"

4. "ID가 2인 MCP 서버의 상세 정보를 알려줘"

5. "상위 기여자 3명을 보여줘"
```

Claude가 MCP 서버의 도구를 사용하여 응답하는 것을 확인할 수 있습니다!

---

## 7. 마무리

축하합니다! 🎉

이제 당신은:
- ✅ MCP의 핵심 개념(Tool, Transport)을 이해했습니다
- ✅ 실제로 동작하는 MCP 서버를 만들었습니다
- ✅ HTTP/SSE Transport를 구현했습니다
- ✅ Claude Desktop과 연동했습니다

### 주요 개념 정리

1. **MCP Server = 중개자**
   - AI 모델과 외부 데이터 소스를 연결
   - 표준 프로토콜로 어떤 AI 모델과도 호환

2. **Tools = AI가 실행할 수 있는 함수**
   - 명확한 이름과 설명 필요
   - JSON Schema로 입력 검증

3. **Transport = 통신 방식**
   - stdio: 로컬 실행, 간단
   - HTTP/SSE: 원격 실행, 다중 클라이언트 지원

4. **공식 가이드 준수**
   - `mcp.server.Server` 사용
   - `@app.list_tools()`, `@app.call_tool()` 데코레이터
   - `TextContent` 응답 형식

### 다음 단계

1. **기능 확장**
   - Resources 추가 (MCP 서버 문서 제공)
   - Prompts 추가 (코드 리뷰 템플릿 등)

2. **배포**
   - Docker로 컨테이너화
   - 클라우드에 배포

3. **자신만의 MCP 서버**
   - 다른 API 연동 (날씨, 주식, 뉴스 등)
   - 로컬 도구 만들기 (파일 관리, 시스템 모니터링)

### 추가 학습 자료

**공식 문서**:
- [MCP Specification](https://spec.modelcontextprotocol.io)
- [MCP Python SDK](https://github.com/anthropics/python-mcp-sdk)
- [MCP 서버 예제](https://github.com/modelcontextprotocol/servers)

**커뮤니티**:
- [MCP Discord](https://discord.gg/mcp)
- [GitHub Discussions](https://github.com/modelcontextprotocol/discussions)

Happy coding! 🚀
