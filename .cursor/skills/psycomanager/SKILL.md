---
name: psycomanager
description: >-
  Especificações e convenções do PsycoManager (Django: pacientes, consultas,
  tarefas, link público). Usar ao implementar features, corrigir bugs,
  alterar models/views/templates, ou quando o utilizador mencionar PsycoManager,
  pacientes, consultas ou consulta pública.
---

# PsycoManager — Especificações

## Produto

Sistema web para **psicólogos** gerirem pacientes, sessões e tarefas terapêuticas.

| Papel | Acesso |
|-------|--------|
| Psicólogo | UI em `/pacientes/` + Django Admin `/admin/` |
| Paciente | Só `consulta_publica` (vídeo + tarefas), se pagamento em dia |

Não é multi-clínica, agenda, billing real nem API pública.

## Stack

- Python 3, **Django ≥ 5.0**, **Pillow**, **SQLite**
- Templates Django + **Tailwind CSS via CDN** (`@tailwindcss/browser@4` em `templates/base.html`)
- Sem React/Vue, DRF, package.json ou `.env` em uso

Deps: `requirements.txt` → `Django>=5.0`, `Pillow`

## Estrutura

```
PsycoManager/
├── manage.py
├── requirements.txt
├── core/                 # settings, urls raiz, wsgi/asgi
├── pacientes/            # app de domínio
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   ├── admin.py
│   └── templates/        # pacientes.html, paciente.html, consulta_publica.html
├── templates/base.html   # layout global
└── media/                # photos/, videos/ (gitignore)
```

## Modelos (`pacientes/models.py`)

### Pacientes
- `psicologo` FK → `User` (CASCADE; cada psicólogo só vê os seus)
- `nome`, `email`, `telefone` (opcional), `foto` → `photos/`
- `pagamento_em_dia` (bool, default `True`)
- `queixa`: `TDAH` | `D` | `A` | `TAG`

### Tarefas (catálogo global)
- `tarefa`, `instrucoes`
- `frequencia`: `D` | `1S` | `2S` | `3S` | `N`

Criação/edição de tarefas: **só via Admin**. A UI de consulta só associa tarefas existentes (M2M).

### Consultas
- `humor` (PositiveInteger, UI usa 1–5)
- `registro_geral`, `video` → `videos/`
- `tarefas` M2M → `Tarefas`
- `paciente` FK → `Pacientes` (CASCADE)
- `data` (`auto_now=True`)
- Props: `link_publico`, `views` (`totais - unicas` via `Visualizacoes`)

### Visualizacoes
- `consulta` FK, `ip` (GenericIPAddressField)
- Não registado no admin

## Rotas

Auth (`core/urls.py`):

| Path | View | Nome |
|------|------|------|
| `entrar/` | `login_view` | `login` |
| `criar-conta/` | `registo_view` | `registo` |
| `sair/` | `logout_view` (POST) | `logout` |

App (`pacientes/urls.py`, prefixo `/pacientes/`):

| Path | View | Nome |
|------|------|------|
| `` | `pacientes` | `pacientes` |
| `<int:id>` | `pacientes_view` | `paciente_view` |
| `atualizar_paciente/<int:id>` | `atualizar_paciente` | `atualizar_paciente` |
| `excluir_consulta/<int:id>` | `excluir_consulta` | `excluir_consulta` |
| `consulta_publica/<int:id>` | `consulta_publica` | `consulta_publica` |

Raiz: redirect → `pacientes`, `/admin/`, media em DEBUG. Credenciais demo: `demo` / `demo123` (`pacientes/demo_auth.py`).

## Features existentes

1. Auth básica: login (com conta demo visível), registo, logout
2. Listar / cadastrar pacientes (foto obrigatória no create atual; scoped ao `request.user`)
3. Detalhe do paciente: toggle pagamento, nova consulta, histórico
4. Consulta: humor, notas, vídeo, tarefas M2M
5. Consulta pública partilhável (vídeo + tarefas; **sem** `registro_geral`; sem login)
6. Contagem de visualizações (total + IPs únicos)
7. Admin para Pacientes, Consultas, Tarefas

## Regras de domínio

- Rotas privadas (`pacientes`, detalhe, atualizar, excluir) exigem `@login_required` e filtro por `psicologo=request.user`
- Link público: se `not paciente.pagamento_em_dia` → `Http404`
- Cada GET em `consulta_publica` grava IP em `Visualizacoes`
- Apagar paciente apaga consultas (CASCADE); apagar user apaga os seus pacientes
- Humor na UI: `>= 3` positivo, senão negativo
- Conta demo (`carregar_demo`) recebe todos os pacientes seed; contas novas começam vazias

## Padrões de código (obrigatório seguir)

- Views **function-based**; ORM direto nas views (sem services/repositories)
- Templates com `{% extends "base.html" %}`, CSRF, `enctype="multipart/form-data"` em uploads
- Feedback: `django.contrib.messages` + `MESSAGE_TAGS` Tailwind
- Nomes de domínio em **português**; models no **plural** (`Pacientes`, `Consultas`, …) — manter consistência
- Choices como tuplas no model
- Locale: `pt-BR` em settings
- Preferir `{% url 'nome' %}` a paths hardcoded ao alterar templates

## Ao adicionar features

1. Preferir estender `pacientes/` em vez de novas apps, salvo domínio claramente separado
2. Novos campos → migration Django; registar no admin se fizer sentido
3. Manter server-rendered + Tailwind CDN, salvo pedido explícito de mudança de stack
4. Não expor `registro_geral` na consulta pública
5. Rotas privadas: `@login_required` + ownership (`psicologo`); `consulta_publica` permanece pública
6. Evitar exclusões destrutivas via GET; preferir POST quando tocares nesse fluxo

## Limitações conhecidas (contexto, não “bugs a ignorar”)

- Auth demo (sem email verification, reset password, OAuth)
- `SECRET_KEY` / `DEBUG` via env com defaults inseguros para prod
- Placeholders na UI (ex.: faltas / totais) podem não ter contexto na view

## Comandos locais

```bash
python -m venv venv
# Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py carregar_demo
python manage.py runserver
# Login: http://127.0.0.1:8000/entrar/  (demo / demo123)
# Admin: /admin/  (admin / admin123 via carregar_demo)
```
