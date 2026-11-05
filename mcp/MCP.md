# MCP-серверы

| Сервер | Зачем | Установка |
|---|---|---|
| blender | Claude управляет живым Blender (bpy, просмотр сцены, импорт ассетов) | `uv` → `claude mcp add --scope user blender -- uvx blender-mcp` (или `scripts/install.sh --with-blender-mcp`) + аддон в Blender (ниже) |

Аддон Blender: в Blender → Edit → Preferences → Add-ons → Install from Disk → файл `addon.py` из
https://github.com/ahujasid/blender-mcp (на исходной машине стоял как `blender_mcp_addon.py`) → включить →
в N-панели «BlenderMCP» нажать Connect. Проверь репозиторий перед установкой.

Встроенные инструменты Claude Desktop (браузер, Chrome, артефакты, docs) ставятся вместе с приложением — переносить не нужно.
