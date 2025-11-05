# MCP Hub MCP Server - Requirements

## Project Overview
- **Project Name**: mcp-demo
- **App Name**: mcp-hub-mcp
- **Purpose**: MCP server for querying MCP Hub database
- **MCP_HUB_URL**: http://localhost:8000

## Requirements

1. tools에는 search_mcp_servers, list_mcp_servers, get_mcp_server_details, get_top_servers, get_top_contributors를 만든다.
2. Transport type은 streamable-http 지원
3. resources는 추후 구현 (현재 구현하지 않는다)
4. Docker로 띄우는 것도 현재는 구현하지 않는다 (main.py 를 실행해서 띄우기)

## API 예시
1. MCP 서버 목록 조회

sort=favorites: 즐겨찾기 수 기준 정렬 (기본값)
sort=created_at: 등록일 기준 정렬
order=desc: 내림차순 (기본값)
order=asc: 오름차순
Examples:

GET /?sort=favorites&limit=3 # Top 3 인기 서버
GET /?sort=created_at&limit=3 # Latest 3 서버

 curl -X 'GET' \
  'http://localhost:8000/api/v1/mcp-servers/?status=approved&sort=favorites&order=desc&limit=20&offset=0' \
  -H 'accept: application/json'

2.Top Contributors 조회
 curl -X 'GET' \
  'http://localhost:8000/api/v1/mcp-servers/top-users?limit=3' \
  -H 'accept: application/json'

3.특정 MCP 서버의 즐겨찾기 수 조회
 curl -X 'GET' \
  'http://localhost:8000/api/v1/mcp-servers/2/favorites/count' \
  -H 'accept: application/json'

4.상세 조회
 curl -X 'GET' \
  'http://localhost:8000/api/v1/mcp-servers/2' \
  -H 'accept: application/json'

## Architecture

## Implementation Notes
1. 필요없는 기능 구현하지 않음
2. SOLID 원칙 준수
3. Test code 정확하게 작성 (pytest 이용)
4. 사내에 서비스를 들고 들어갔을 때 url은 https://xxxx:7540 으로 바뀌는데, SSL 에러가 발생하지 않도록 해야 함
