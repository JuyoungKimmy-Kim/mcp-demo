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

### 2.3 MCP 구현 방식

MCP 서버를 만드는 방법은 크게 두 가지가 있습니다:

#### 1. **공식 MCP Python SDK** (이 튜토리얼에서 사용)

```python
from mcp.server import Server

app = Server("server-name")

@app.list_tools()
async def list_tools():
    return [Tool(...)]

@app.call_tool()
async def call_tool(name: str, arguments: dict):
    # 수동 라우팅 처리
    if name == "my_tool":
        return [TextContent(type="text", text="result")]
```

**특징**:
- ✅ 공식 SDK, 가장 표준적인 방식
- ✅ 명시적이고 세밀한 제어 가능
- ✅ MCP 스펙을 직접 다룸
- ❌ 코드가 비교적 장황함
- ❌ 수동으로 라우팅 처리 필요

#### 2. **FastMCP** (간편한 대안)

```python
from fastmcp import FastMCP

mcp = FastMCP("server-name")

@mcp.tool()
def my_tool(arg: str) -> str:
    """도구 설명"""
    return "result"
```

**특징**:
- ✅ FastAPI 스타일의 간결한 문법
- ✅ 타입 힌트로 자동 스키마 생성
- ✅ 자동 라우팅
- ❌ 비공식 라이브러리
- ❌ 세밀한 제어가 어려울 수 있음

#### 이 튜토리얼의 선택

**공식 SDK를 사용하는 이유**:
1. **표준 방식 학습**: MCP의 기본 개념을 정확히 이해
2. **공식 지원**: Anthropic 공식 SDK
3. **세밀한 제어**: Tool 정의, 실행 로직, Transport를 명확히 분리
4. **확장성**: 복잡한 로직도 쉽게 구현

> FastMCP는 프로토타이핑이나 간단한 서버에 적합합니다. 하지만 이 튜토리얼에서는 MCP의 내부 동작을 이해하기 위해 공식 SDK를 사용합니다.

#### MCP 서버의 역할

**중요**: MCP 서버는 **중개자(Proxy)** 역할입니다.

```
AI Model (Claude)
    ↓ MCP Protocol
MCP Server (우리가 만드는 것)
    ↓ HTTP/DB/File/etc
External Data Source (MCP Hub API 등)
```

- MCP Hub REST API (`http://localhost:8000`)는 **외부 데이터 소스**
- MCP 서버는 이 API를 호출하여 결과를 AI에게 전달
- FastMCP든 공식 SDK든 **모두 외부 API를 호출하는 중개자**

### 2.4 Resources와 Prompts (이번 실습에서는 다루지 않음)

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

### 4.3 Roocode 연동 방법 (참고용)

> **주의**: Hello World 서버는 실제로 유용한 기능이 없습니다. 이 섹션은 **MCP 서버를 Roocode에 연결하는 방법을 설명하기 위한 것**입니다. 실제로 사용할 MCP 서버는 섹션 5의 "MCP Hub 서버"입니다.

Roocode (또는 다른 MCP 클라이언트)에서 MCP 서버를 연결하는 방법을 알아봅시다.

#### 1. Roocode 설정 파일 수정

Roocode의 MCP 설정 파일에 다음을 추가합니다:

**macOS/Linux:**
```bash
# Roocode 설정 파일 위치
~/.roo/mcp_config.json
```

**설정 내용:**
```json
{
  "mcpServers": {
    "hello-mcp": {
      "command": "${workspaceFolder}/.venv/bin/python",
      "args": ["${workspaceFolder}/hello_mcp.py"],
      "disabled": false
    }
  }
}
```

**Windows의 경우:**
```json
{
  "mcpServers": {
    "hello-mcp": {
      "command": "${workspaceFolder}\\.venv\\Scripts\\python.exe",
      "args": ["${workspaceFolder}\\hello_mcp.py"],
      "disabled": false
    }
  }
}
```

**설정 설명:**
- `command`: Python 실행 파일 경로 (가상환경의 Python 사용)
- `args`: 실행할 스크립트 경로
- `${workspaceFolder}`: 현재 프로젝트 디렉토리를 자동으로 참조
- `disabled: false`: 서버 활성화

#### 2. Roocode 재시작

설정 파일을 저장한 후 Roocode를 재시작합니다.

#### 3. 테스트 (선택 사항)

원한다면 Roocode에서 다음과 같이 질문해보세요:

```
"내 이름은 김철수야. 인사해줘!"
```

Roocode가 `say_hello` 도구를 사용하여 "안녕하세요, 김철수님!"이라고 응답하는 것을 확인할 수 있습니다.

> 하지만 이 서버는 단순히 인사만 하는 기능이므로 실제로는 유용하지 않습니다. 실전 프로젝트인 "MCP Hub 서버"에서 실제로 유용한 MCP 서버를 만들어봅시다!

#### 4. 직접 실행 테스트

터미널에서 직접 실행할 수도 있습니다:

```bash
python hello_mcp.py
```

서버가 실행되면 대기 상태가 됩니다. (MCP 클라이언트와 연결 전)

**주의사항:**
- 가상환경이 활성화된 상태에서 실행해야 합니다
- `hello_mcp.py` 파일이 실행 가능한지 확인하세요 (`chmod +x hello_mcp.py`)
- 로그 메시지가 표시되면 정상적으로 실행된 것입니다

---

## 5. 실전 프로젝트 Part 1: Tool과 API 클라이언트

이제 실제로 유용한 MCP 서버를 만들어봅시다!

**목표**: MCP Hub 데이터베이스를 조회하는 MCP 서버

**제공 기능**:
- `get_mcp_server_details`: 특정 MCP 서버의 상세 정보 조회

> 이 튜토리얼에서는 `get_mcp_server_details` 하나만 구현하여 MCP 서버의 핵심 개념을 배웁니다. 다른 기능들(`list_mcp_servers`, `search_mcp_servers`, `get_top_contributors`)은 같은 패턴으로 추가할 수 있습니다.

**데이터 소스**: MCP Hub REST API (`http://localhost:8000`)

**Transport**: HTTP/SSE

**Server URL**: `http://localhost:10004/messages`

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
        name="get_mcp_server_details",
        description="Get detailed information about a specific MCP server",
        inputSchema={
            "type": "object",
            "properties": {
                "server_id": {
                    "type": "integer",
                    "description": "The ID of the MCP server"
                }
            },
            "required": ["server_id"]
        }
    ),
]
```

**핵심 포인트**:
- `name`: 도구 이름 (함수명 스타일)
- `description`: Claude가 언제 이 도구를 사용할지 이해할 수 있는 명확한 설명
- `inputSchema`: JSON Schema로 입력 검증
  - `type`: 데이터 타입 (integer, string 등)
  - `description`: 파라미터 설명
  - `required`: 필수 필드 목록

### 5.3 Step 2: API 클라이언트 구현

**중요**: 이 코드는 **실제 MCP Hub REST API**를 호출합니다. API 문서(`CLAUDE.md` 참고)에 정의된 엔드포인트를 그대로 사용합니다.

예를 들어, 다음 API 호출:
```bash
curl 'http://localhost:8000/api/v1/mcp-servers/2'
```

이것을 Python 코드로 작성:
```python
data = await self._get(f"/api/v1/mcp-servers/{server_id}")
```

`src/client/api_client.py`:

```python
"""API client for MCP Hub"""
from typing import Dict, Any
import httpx


class APIClient:
    """Client for accessing MCP Hub REST API"""

    def __init__(self, api_base_url: str = "http://localhost:8000"):
        self.api_base_url = api_base_url
        self.client = httpx.AsyncClient(
            timeout=30.0,
            verify=False  # SSL 에러 방지 (사내 서비스용)
        )

    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()

    async def _get(self, endpoint: str) -> Dict[str, Any]:
        """Make a GET request to the API"""
        url = f"{self.api_base_url}{endpoint}"
        response = await self.client.get(url)
        response.raise_for_status()
        return response.json()

    async def get_server_details(self, server_id: int) -> Dict[str, Any]:
        """Get detailed information about a specific MCP server"""
        return await self._get(f"/api/v1/mcp-servers/{server_id}")
```

**코드 상세 설명**:

#### 1. `__init__` - 클라이언트 초기화
```python
def __init__(self, api_base_url: str = "http://localhost:8000"):
    self.api_base_url = api_base_url
    self.client = httpx.AsyncClient(timeout=30.0, verify=False)
```
- `api_base_url`: MCP Hub API의 기본 URL
- `timeout=30.0`: 요청 타임아웃 30초
- `verify=False`: SSL 인증서 검증 비활성화 (사내 HTTPS 서비스에서 자체 서명 인증서 사용 시 필요)

#### 2. `_get` - HTTP GET 요청 헬퍼
```python
async def _get(self, endpoint: str) -> Dict[str, Any]:
    url = f"{self.api_base_url}{endpoint}"
    response = await self.client.get(url)
    response.raise_for_status()
    return response.json()
```
- 모든 GET 요청을 통합 처리
- `raise_for_status()`: HTTP 에러 시 예외 발생
- **반환값**: API 응답을 JSON Dict로 반환 (포맷팅은 Handler에서 담당)

#### 3. `get_server_details` - MCP 서버 상세 정보 조회
```python
async def get_server_details(self, server_id: int) -> Dict[str, Any]:
    return await self._get(f"/api/v1/mcp-servers/{server_id}")
```
- **API 엔드포인트**: `/api/v1/mcp-servers/{server_id}`
- **파라미터**: `server_id` (MCP 서버 ID)
- **반환값**: 서버 상세 정보를 담은 Dict

**핵심 포인트**:
- `httpx.AsyncClient`: 비동기 HTTP 클라이언트 (MCP는 비동기 기반)
- `verify=False`: SSL 인증서 검증 비활성화 (사내 서비스용)
- **관심사 분리**: API Client는 데이터 조회만, 포맷팅은 Handler가 담당

> **참고**: 실제 프로덕션 환경에서는 에러 처리(`try-except`)와 로깅을 추가하는 것이 좋습니다. 이 튜토리얼에서는 핵심 개념에 집중하기 위해 생략했습니다.

---

## 6. 실전 프로젝트 Part 2: MCP 서버 구현

이제 Tool 정의와 API 클라이언트를 MCP 서버로 통합해봅시다!

### 6.1 Tool Handler 구현

`src/handlers/tools.py`:

```python
"""Tool handlers for MCP Hub MCP Server"""
from typing import Any, Dict
from mcp.types import TextContent


def format_server_details(data: Dict[str, Any]) -> str:
    """Format server details data into readable text"""
    if not data:
        return "Server not found"

    lines = []
    lines.append(f"📦 {data.get('name', 'Unknown')}")
    lines.append(f"   ID: {data.get('id')}")
    lines.append(f"   Description: {data.get('description', 'No description')}")
    lines.append(f"   Author: {data.get('author', 'Unknown')}")
    lines.append(f"   ⭐ Favorites: {data.get('favorites_count', 0)}")

    if data.get('repository_url'):
        lines.append(f"   🔗 Repository: {data['repository_url']}")

    if data.get('created_at'):
        lines.append(f"   📅 Created: {data['created_at']}")

    return "\n".join(lines)


async def handle_tool_call(name: str, arguments: Any, api_client) -> list[TextContent]:
    """Handle tool calls from MCP clients"""

    if name == "get_mcp_server_details":
        server_id = arguments.get("server_id")
        data = await api_client.get_server_details(server_id)
        formatted_text = format_server_details(data)
        return [TextContent(type="text", text=formatted_text)]

    return [TextContent(type="text", text=f"Unknown tool: {name}")]
```

**핵심 포인트**:
- **관심사 분리**: `format_server_details()` 함수가 포맷팅 담당
- **간단한 라우팅**: Tool이 하나뿐이므로 간단한 `if` 문으로 처리
- **파라미터 처리**: `arguments.get("server_id")`로 파라미터 추출
- **응답 형식**: 반드시 `list[TextContent]` 반환 (MCP 스펙)
- **도구 추가하기**: 더 많은 도구를 추가하려면 `elif` 문으로 확장

> **참고**: 실제 프로덕션 환경에서는 에러 처리(`try-except`)와 로깅을 추가하는 것이 좋습니다.

### 6.2 HTTP Transport 구현

`src/transport/http.py`:

```python
"""HTTP/SSE transport for MCP Hub MCP Server"""
import os
from mcp.server.sse import SseServerTransport
import uvicorn


async def run_http_transport(app, api_client) -> None:
    """Run server with HTTP/SSE transport"""
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "10004"))

    # SSE Transport 생성
    sse = SseServerTransport("/messages")

    # ASGI app
    async def asgi_app(scope, receive, send):
        """Main ASGI app for routing"""
        if scope["type"] == "http":
            path = scope["path"]

            if path == "/sse":
                # Handle SSE endpoint
                async with sse.connect_sse(scope, receive, send) as streams:
                    await app.run(
                        streams[0], streams[1], app.create_initialization_options()
                    )
            elif path == "/messages":
                # Handle messages endpoint
                await sse.handle_post_message(scope, receive, send)
            elif path == "/health":
                # Health check
                await send({
                    "type": "http.response.start",
                    "status": 200,
                    "headers": [[b"content-type", b"application/json"]],
                })
                await send({
                    "type": "http.response.body",
                    "body": b'{"status":"healthy","service":"mcp-hub-mcp"}',
                })
            else:
                # 404 for other paths
                await send({
                    "type": "http.response.start",
                    "status": 404,
                    "headers": [[b"content-type", b"text/plain"]],
                })
                await send({
                    "type": "http.response.body",
                    "body": b"Not Found",
                })

    try:
        config = uvicorn.Config(asgi_app, host=host, port=port)
        server = uvicorn.Server(config)
        await server.serve()
    finally:
        await api_client.close()
```

**핵심 포인트**:
- **순수 ASGI 구현**: 외부 웹 프레임워크 없이 ASGI만 사용
- **SSE 엔드포인트**: `/sse` - 클라이언트가 연결하는 주소
- **메시지 엔드포인트**: `/messages` - 클라이언트가 메시지를 보내는 주소
- **Health Check**: `/health` 엔드포인트로 서버 상태 확인

### 6.3 메인 진입점 구현

`src/main.py`:

```python
#!/usr/bin/env python3
"""MCP Hub MCP Server - Main Entry Point"""
import asyncio
import os
from mcp.server import Server

from client.api_client import APIClient
from schemas.tools import TOOLS
from handlers.tools import handle_tool_call
from transport.http import run_http_transport


async def main():
    """Main function"""
    # MCP Hub URL 설정
    api_base_url = os.getenv("MCP_HUB_URL", "http://localhost:8000")

    # API Client 생성
    api_client = APIClient(api_base_url)

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
    asyncio.run(main())
```

**핵심 포인트**:
- **환경 변수**: `MCP_HUB_URL`로 API 엔드포인트 설정
- **데코레이터**: `@app.list_tools()`, `@app.call_tool()`로 핸들러 등록
- **모듈화**: 각 기능을 별도 모듈로 분리하여 관리

> **참고**: 로깅과 예외 처리를 간소화했습니다. 실제 프로덕션 환경에서는 더 상세한 로깅과 에러 처리를 추가하세요.

### 6.4 실행 및 테스트

#### 1. 서버 실행

```bash
cd src
python main.py
```

서버가 시작되고 포트 10004에서 대기합니다.

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

## 7. Claude Desktop 연동

### 7.1 Claude Desktop 설정 파일 위치

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

### 7.2 HTTP Transport 연결 설정

#### Claude Desktop 설정

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

#### Roocode 설정

Roocode의 MCP 설정 파일(`~/.roo/mcp_config.json`):

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

**중요**:
- URL에 반드시 `http://` 또는 `https://` 프로토콜을 명시해야 합니다
- Claude Desktop은 `/messages` 엔드포인트를 사용
- Roocode와 Claude Desktop 모두 `/messages` 엔드포인트를 사용합니다

**사내 환경에서 사용하는 경우:**

Roocode 설정 예시 (사내 서버):
```json
{
  "mcpServers": {
    "mcp-hub": {
      "url": "https://your-internal-server:7540/messages",
      "transport": "sse"
    }
  }
}
```

- `https://your-internal-server:7540`: 사내 MCP 서버 주소
- SSL 인증서 문제가 있는 경우, MCP 서버 코드에서 `verify=False` 설정이 적용됨

### 7.3 Claude Desktop / Roocode 재시작

설정 파일을 저장한 후 Claude Desktop을 완전히 종료하고 다시 시작합니다.

### 7.4 MCP 서버 연결 확인

Claude Desktop에서 MCP 서버가 연결되었는지 확인:
1. 우측 하단의 🔌 아이콘 클릭
2. "mcp-hub" 서버가 목록에 표시되는지 확인
3. 연결 상태가 "Connected"인지 확인

### 7.5 테스트 질문

Claude Desktop (또는 Roocode)에서 다음과 같이 질문해보세요:

```
1. "ID가 2인 MCP 서버의 상세 정보를 알려줘"

2. "MCP 서버 5번의 정보를 보여줘"

3. "서버 ID 1의 상세 정보를 확인해줘"
```

Claude가 MCP 서버의 `get_mcp_server_details` 도구를 사용하여 응답하는 것을 확인할 수 있습니다!

**예상 결과**:
- Claude가 자동으로 `server_id` 파라미터를 추출
- MCP Hub API에서 해당 서버의 상세 정보를 가져와 포맷팅된 결과 반환
- 서버 이름, 설명, 저자, 즐겨찾기 수, 저장소 URL 등이 표시됨

---

## 8. 마무리

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
   - 더 많은 Tool 추가:
     - `list_mcp_servers`: 서버 목록 조회 (정렬, 페이징)
     - `search_mcp_servers`: 키워드로 MCP 서버 검색
     - `get_top_contributors`: 상위 기여자 조회
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
