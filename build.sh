#!/usr/bin/env bash
# Exit on error
set -o errexit

pip install -r requirements.txt

python manage.py collectstatic --no-input

python manage.py migrate

# Site de demonstração: recria dados demo em cada deploy (sem precisar do Shell pago)
python manage.py carregar_demo --limpar
