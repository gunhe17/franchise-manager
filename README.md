# franchise-manager

## 개발환경 실행

1. `.env` 생성

   ```bash
   cp .env/.env.develop.example .env/.env.develop
   ```

2. Dev Container 진입 (`Cmd+Shift+P`)
   - 최초: `Dev Containers: Rebuild and Reopen in Container`
   - 이후: `Dev Containers: Reopen in Container`

3. API 서버 실행

   ```bash
   python franchise_manager/api/bin/server.py
   ```

4. Claude Code에서 MCP 연결 확인

   ```
   /mcp
   ```

   목록에 `franchise-manager-dev` 존재 확인
