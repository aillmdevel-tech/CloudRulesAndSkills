# MCP-серверы

Список с исходной машины (без ключей): `servers.json` (обновляет `scripts/sync.sh`).

| Сервер | Зачем | Установка |
|---|---|---|
| blender | живой Blender: bpy, `look`, поиск/импорт ассетов, `generate_3d` | `claude mcp add --scope user blender -- uvx blender-mcp` + аддон (ниже) |
| afk-rig | авториг GLB/FBX, анимации по типу тела, модель из картинки | `claude mcp add --scope user afk-rig -- npx -y afk-rig mcp`; ключ/аккаунт — afk.ai/developers, по запросу инструмента |
| playgama-developer-cabinet | кабинет разработчика Playgama | в папке игры: `claude mcp add --transport http --scope local playgama-developer-cabinet https://developer.playgama.com/api/mcp`, вход в браузере |

Первые два ставит `scripts/install.sh --with-mcp`.

## Аддон Blender
`blender/blender_mcp_addon.py` — «MCP for Blender» 1.8 (ahujasid/blender-mcp, MIT), сервер `mcp-for-blender` 2.2.6, Blender 5.2.
`install.sh --with-mcp` копирует его во все версии Blender и пытается включить. Если не включился: Blender → Edit → Preferences →
Add-ons → Install from Disk → этот файл → включить → в N-панели «BlenderMCP» нажать Connect.

Встроенные инструменты Claude Desktop (браузер, Chrome, артефакты, docs) ставятся с приложением.
