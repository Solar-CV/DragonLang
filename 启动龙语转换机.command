#!/bin/bash
cd -- "$(dirname -- "$0")" || exit 1
if ! command -v python3 >/dev/null 2>&1; then
  echo '需要 Python 3.9 或更新版本：https://www.python.org/downloads/'
  read -r -p '按回车关闭…'; exit 1
fi
python3 server.py
rc=$?
if [ "$rc" -ne 0 ]; then read -r -p '启动失败，按回车关闭…'; fi
exit "$rc"
