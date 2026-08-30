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
  echo "[1/5] Criando ambiente virtual..."
  python3 -m venv venv
else
  echo "[1/5] Ambiente virtual já existe."
fi

PY="venv/bin/python"

echo "[2/5] Instalando dependências..."
"$PY" -m pip install -q -r requirements.txt

echo "[3/5] Aplicando migrações..."
"$PY" manage.py migrate

echo "[4/5] Carregando dados demo (se a base estiver vazia)..."
"$PY" manage.py carregar_demo

echo "[5/5] A iniciar o servidor..."
echo
echo "Login: http://127.0.0.1:8000/entrar/  (demo / demo123)"
echo "Admin: http://127.0.0.1:8000/admin/  (admin / admin123)"
echo
echo "Ctrl+C para parar."
echo

exec "$PY" manage.py runserver
