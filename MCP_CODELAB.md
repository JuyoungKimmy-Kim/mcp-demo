# MCP 서버 만들기 Codelab

> **소요 시간**: 약 30분
> **난이도**: 초급
> **사전 지식**: Python 기본, REST API 개념

MCP(Model Context Protocol)의 핵심 개념을 이해하고, 실제로 동작하는 간단한 MCP 서버를 처음부터 만들어봅니다.

---

## 📚 목차

1. [MCP란 무엇인가?](#1-mcp란-무엇인가)
2. [MCP의 핵심 개념](#2-mcp의-핵심-개념)
3. [실습 준비](#3-실습-준비)
4. [MCP 서버 만들기](#4-mcp-서버-만들기)
5. [Roocode 연동](#5-roocode-연동)

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

**시나리오: MCP Hub 서버 상세 정보 조회**
```
사용자: "ID가 2인 MCP 서버의 상세 정보를 알려줘"
  ↓
Claude: MCP 서버의 get_mcp_server_details tool 호출
  ↓
MCP 서버: MCP Hub API 호출
  ↓
Claude: "서버 이름, 설명, 저자 정보를 찾았습니다..."
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
    name="get_mcp_server_details",
    description="MCP 서버의 상세 정보를 조회합니다",
    inputSchema={
        "type": "object",
        "properties": {
            "server_id": {"type": "integer", "description": "서버 ID"}
        },
        "required": ["server_id"]
    }
)
```

**언제 사용하나?**
- ✅ 검색, 조회 작업
- ✅ 외부 API 호출
- ✅ 데이터 생성/수정

### 2.2 Transport (통신 방식)

MCP 서버와 AI 모델이 **어떻게** 통신할지 정의합니다.

#### HTTP/SSE (Server-Sent Events)
```
┌──────────────┐
│ Claude/      │
│ Roocode      │
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

### 2.3 MCP 서버의 역할

**중요**: MCP 서버는 **중개자(Proxy)** 역할입니다.

```
AI Model (Claude/Roocode)
    ↓ MCP Protocol
MCP Server (우리가 만드는 것)
    ↓ HTTP/DB/File/etc
External Data Source (MCP Hub API 등)
```

- MCP Hub REST API (`http://localhost:8000`)는 **외부 데이터 소스**
- MCP 서버는 이 API를 호출하여 결과를 AI에게 전달

---

## 3. 실습 준비

### 3.1 환경 설정

```bash
# 프로젝트 디렉토리 생성
mkdir mcp-demo
cd mcp-demo

# 가상환경 생성 및 활성화
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 파일 생성
cat > requirements.txt <<EOF
# MCP Server
mcp>=1.0.0

# HTTP Server (for SSE transport)
uvicorn>=0.23.0

# HTTP Client
httpx>=0.27.0
EOF

# 설치
pip install -r requirements.txt
```

### 3.2 프로젝트 구조

```
mcp-demo/
├── src/
│   ├── main.py           # 메인 진입점
│   ├── client.py         # API 클라이언트
│   ├── tools/
│   │   ├── schemas.py    # Tool 정의
│   │   └── handlers.py   # Tool 실행 로직
│   └── transport.py      # HTTP/SSE 통신
└── requirements.txt
```

---

## 4. MCP 서버 만들기

### 4.1 Step 1: Tool 정의하기

`src/tools/schemas.py`:

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

### 4.2 Step 2: API 클라이언트 구현

**중요**: 이 코드는 **실제 MCP Hub REST API**를 호출합니다.

`src/client.py`:

```python
"""API client for MCP Hub"""
import os
from typing import Dict, Any
import httpx


class APIClient:
    """Client for accessing MCP Hub REST API"""

    def __init__(self, base_url: str = None):
        """Initialize API client"""
        self.base_url = base_url or os.getenv("MCP_HUB_URL", "http://localhost:8000")
        self.client = httpx.AsyncClient(timeout=30.0, verify=False)

    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()

    async def get_server_details(self, server_id: int) -> Dict[str, Any]:
        """Get detailed information about a specific MCP server"""
        url = f"{self.base_url}/api/v1/mcp-servers/{server_id}"
        response = await self.client.get(url)
        response.raise_for_status()
        return response.json()
```

**핵심 포인트**:
- `httpx.AsyncClient`: 비동기 HTTP 클라이언트
- `verify=False`: SSL 인증서 검증 비활성화 (사내 서비스용)
- **관심사 분리**: API Client는 데이터 조회만, 포맷팅은 Handler가 담당

### 4.3 Step 3: Tool Handler 구현

`src/tools/handlers.py`:

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
- **간단한 라우팅**: 단순한 `if` 문으로 처리
- **응답 형식**: 반드시 `list[TextContent]` 반환 (MCP 스펙)

### 4.4 Step 4: HTTP Transport 구현

`src/transport.py`:

```python
"""HTTP/SSE transport for MCP Hub MCP Server"""
from mcp.server import Server
from mcp.server.sse import SseServerTransport
import uvicorn


async def run_http_transport(app: Server, host: str = "0.0.0.0", port: int = 10004):
    """Run MCP server with HTTP/SSE transport"""
    sse = SseServerTransport("/messages")

    async def asgi_app(scope, receive, send):
        """Main ASGI app for routing"""
        if scope["type"] == "http":
            path = scope["path"]

            if path == "/sse":
                async with sse.connect_sse(scope, receive, send) as streams:
                    await app.run(
                        streams[0], streams[1], app.create_initialization_options()
                    )
            elif path == "/messages":
                await sse.handle_post_message(scope, receive, send)
            elif path == "/health":
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
                await send({
                    "type": "http.response.start",
                    "status": 404,
                    "headers": [[b"content-type", b"text/plain"]],
                })
                await send({
                    "type": "http.response.body",
                    "body": b"Not Found",
                })

    config = uvicorn.Config(asgi_app, host=host, port=port, log_level="info")
    server = uvicorn.Server(config)
    await server.serve()
```

**핵심 포인트**:
- **순수 ASGI 구현**: 외부 웹 프레임워크 없이 ASGI만 사용
- **SSE 엔드포인트**: `/sse` - Roocode가 연결하는 주소
- **메시지 엔드포인트**: `/messages` - 클라이언트가 메시지를 보내는 주소
- **Health Check**: `/health` 엔드포인트로 서버 상태 확인

### 4.5 Step 5: 메인 진입점 구현

`src/main.py`:

```python
#!/usr/bin/env python3
"""MCP Hub MCP Server - Simple Example"""

import asyncio
import os
import sys
from pathlib import Path
from typing import Any
from mcp.server import Server
from mcp.types import Tool, TextContent

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from client import APIClient
from tools.schemas import TOOLS
from tools.handlers import handle_tool_call
from transport import run_http_transport

app = Server("mcp-hub-mcp")
api_client: APIClient | None = None


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools"""
    return TOOLS


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Handle tool calls"""
    return await handle_tool_call(name, arguments, api_client)


async def main():
    """Main entry point"""
    global api_client

    api_client = APIClient()
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "10004"))

    await run_http_transport(app, host=host, port=port)
    await api_client.close()


if __name__ == "__main__":
    asyncio.run(main())
```

**핵심 포인트**:
- **환경 변수**: `MCP_HUB_URL`, `HOST`, `PORT`로 설정 가능
- **데코레이터**: `@app.list_tools()`, `@app.call_tool()`로 핸들러 등록
- **모듈화**: 각 기능을 별도 모듈로 분리

### 4.6 실행 및 테스트

#### 1. 서버 실행

```bash
python src/main.py
```

서버가 시작되고 포트 10004에서 대기합니다.

#### 2. Health Check

다른 터미널에서:
```bash
curl http://localhost:10004/health
```

출력:
```json
{"status":"healthy","service":"mcp-hub-mcp"}
```

---

## 5. Roocode 연동

### 5.1 Roocode 설정

`~/.roo/mcp_config.json` 파일에 다음을 추가:

**로컬 환경:**
```json
{
  "mcpServers": {
    "mcp-hub": {
      "url": "http://localhost:10004/sse",
      "transport": "sse"
    }
  }
}
```

**사내 환경 (예시):**
```json
{
  "mcpServers": {
    "mcp-hub": {
      "url": "https://your-internal-server:7540/sse",
      "transport": "sse"
    }
  }
}
```

**중요**:
- URL에 반드시 `http://` 또는 `https://` 프로토콜을 명시해야 합니다
- Roocode는 `/sse` 엔드포인트를 사용합니다

### 5.2 Roocode 재시작

설정 파일을 저장한 후 Roocode를 재시작합니다.

### 5.3 테스트 질문

Roocode에서 다음과 같이 질문해보세요:

```
"ID가 2인 MCP 서버의 상세 정보를 알려줘"
```

Roocode가 `get_mcp_server_details` 도구를 사용하여 응답하는 것을 확인할 수 있습니다!

---

## 6. 마무리

축하합니다! 🎉

이제 당신은:
- ✅ MCP의 핵심 개념(Tool, Transport)을 이해했습니다
- ✅ 실제로 동작하는 간단한 MCP 서버를 만들었습니다
- ✅ HTTP/SSE Transport를 구현했습니다
- ✅ Roocode와 연동했습니다

### 주요 개념 정리

1. **MCP Server = 중개자**
   - AI 모델과 외부 데이터 소스를 연결
   - 표준 프로토콜로 어떤 AI 모델과도 호환

2. **Tools = AI가 실행할 수 있는 함수**
   - 명확한 이름과 설명 필요
   - JSON Schema로 입력 검증

3. **Transport = 통신 방식**
   - HTTP/SSE: 원격 실행, 다중 클라이언트 지원

4. **간단한 구조**
   - 복잡한 클래스나 설정 파일 없이
   - 필요한 기능만 구현

### 다음 단계

1. **기능 확장**
   - 더 많은 Tool 추가 (`list_mcp_servers`, `search_mcp_servers` 등)
   - 에러 처리 및 로깅 추가

2. **자신만의 MCP 서버**
   - 다른 API 연동 (날씨, 주식, 뉴스 등)
   - 로컬 도구 만들기 (파일 관리, 시스템 모니터링)

### 추가 학습 자료

**공식 문서**:
- [MCP Specification](https://spec.modelcontextprotocol.io)
- [MCP Python SDK](https://github.com/anthropics/python-mcp-sdk)
- [MCP 서버 예제](https://github.com/modelcontextprotocol/servers)

Happy coding! 🚀
