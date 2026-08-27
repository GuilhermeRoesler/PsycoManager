#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"

echo "=== PsycoManager ==="
echo

if ! command -v python3 >/dev/null 2>&1; then
  echo "[ERRO] Python 3 não encontrado no PATH."
  echo "Instale Python 3 e tente novamente."
  exit 1
fi

if [ ! -x "venv/bin/python" ]; then
  echo "[1/4] Criando ambiente virtual..."
  python3 -m venv venv
else
  echo "[1/4] Ambiente virtual já existe."
fi

PY="venv/bin/python"

echo "[2/4] Instalando dependências..."
"$PY" -m pip install -q -r requirements.txt

echo "[3/4] Aplicando migrações..."
"$PY" manage.py migrate

echo "[4/4] A iniciar o servidor..."
echo
echo "UI:    http://127.0.0.1:8000/pacientes/"
echo "Admin: http://127.0.0.1:8000/admin/"
echo
echo "Ctrl+C para parar."
echo

exec "$PY" manage.py runserver
