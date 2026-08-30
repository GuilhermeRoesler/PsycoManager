from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.messages import constants
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods, require_POST

from .demo_auth import DEMO_PASSWORD, DEMO_USERNAME
from .models import Consultas, Pacientes, Tarefas, Visualizacoes

PACIENTES_POR_PAGINA = 20


def _paciente_do_usuario(request, id):
    return get_object_or_404(Pacientes, id=id, psicologo=request.user)


@require_http_methods(["GET", "POST"])
def login_view(request):
    if request.user.is_authenticated:
        return redirect("pacientes")

    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            next_url = request.GET.get("next") or request.POST.get("next")
            if next_url:
                return redirect(next_url)
            return redirect("pacientes")
        messages.add_message(request, constants.ERROR, "Utilizador ou palavra-passe incorretos")

    return render(
        request,
        "login.html",
        {
            "demo_username": DEMO_USERNAME,
            "demo_password": DEMO_PASSWORD,
            "next": request.GET.get("next", ""),
        },
    )


@require_http_methods(["GET", "POST"])
def registo_view(request):
    if request.user.is_authenticated:
        return redirect("pacientes")

    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        email = request.POST.get("email", "").strip()
        password = request.POST.get("password", "")
        password2 = request.POST.get("password2", "")

        if not username or not password:
            messages.add_message(request, constants.ERROR, "Preencha utilizador e palavra-passe")
        elif password != password2:
            messages.add_message(request, constants.ERROR, "As palavras-passe não coincidem")
        elif len(password) < 6:
            messages.add_message(
                request, constants.ERROR, "A palavra-passe deve ter pelo menos 6 caracteres"
            )
        elif User.objects.filter(username__iexact=username).exists():
            messages.add_message(request, constants.ERROR, "Este utilizador já existe")
        else:
            user = User.objects.create_user(username=username, email=email, password=password)
            login(request, user)
            messages.add_message(
                request, constants.SUCCESS, "Conta criada. Pode começar a cadastrar pacientes."
            )
            return redirect("pacientes")

    return render(request, "registo.html")


@require_POST
def logout_view(request):
    logout(request)
    messages.add_message(request, constants.SUCCESS, "Sessão terminada")
    return redirect("login")


@login_required
def pacientes(request):
    if request.method == "GET":
        qs = Pacientes.objects.filter(psicologo=request.user).order_by("nome")
        q = request.GET.get("q", "").strip()
        pagamento = request.GET.get("pagamento", "").strip()
        queixa = request.GET.get("queixa", "").strip()

        if q:
            q_lower = q.casefold()
            queixa_codes = [
                code
                for code, label in Pacientes.queixa_choices
                if q_lower in code.casefold() or q_lower in label.casefold()
            ]
            qs = qs.filter(
                Q(nome__icontains=q)
                | Q(email__icontains=q)
                | Q(queixa__in=queixa_codes)
            )
        if pagamento == "em_dia":
            qs = qs.filter(pagamento_em_dia=True)
        elif pagamento == "pendente":
            qs = qs.filter(pagamento_em_dia=False)
        if queixa:
            qs = qs.filter(queixa=queixa)

        page_obj = Paginator(qs, PACIENTES_POR_PAGINA).get_page(request.GET.get("page"))
        total = qs.count()
        filtros_ativos = bool(q or pagamento or queixa)

        return render(
            request,
            "pacientes.html",
            {
                "queixas": Pacientes.queixa_choices,
                "pacientes": page_obj,
                "page_obj": page_obj,
                "total_pacientes": total,
                "tem_pacientes": Pacientes.objects.filter(psicologo=request.user).exists(),
                "filtros_ativos": filtros_ativos,
                "filtro_q": q,
                "filtro_pagamento": pagamento,
                "filtro_queixa": queixa,
            },
        )
    elif request.method == "POST":
        nome = request.POST.get("nome")
        email = request.POST.get("email")
        telefone = request.POST.get("telefone")
        queixa = request.POST.get("queixa")
        foto = request.FILES.get("foto")

        if not nome or len(nome.strip()) == 0 or not foto:
            messages.add_message(request, constants.ERROR, "Preencha todos os campos")
            return redirect("pacientes")

        paciente = Pacientes(
            psicologo=request.user,
            nome=nome,
            email=email,
            telefone=telefone,
            queixa=queixa,
            foto=foto,
        )

        paciente.save()
        messages.add_message(request, constants.SUCCESS, "Cadastro realizado com sucesso")

        return redirect("pacientes")


@login_required
def pacientes_view(request, id):
    paciente = _paciente_do_usuario(request, id)
    if request.method == "GET":
        tarefas = Tarefas.objects.all()
        consultas = Consultas.objects.filter(paciente=paciente).order_by("-data")
        consultas_ordenadas = list(consultas.order_by("data"))
        return render(
            request,
            "paciente.html",
            {
                "paciente": paciente,
                "tarefas": tarefas,
                "consultas": consultas,
                "consultas_ordenadas": consultas_ordenadas,
                "total_consultas": consultas.count(),
            },
        )
    elif request.method == "POST":
        humor = request.POST.get("humor")
        registro_geral = request.POST.get("registro_geral")
        video = request.FILES.get("video")
        tarefas = request.POST.getlist("tarefas")

        consulta = Consultas(
            humor=int(humor), registro_geral=registro_geral, video=video, paciente=paciente
        )
        consulta.save()

        for i in tarefas:
            tarefa = Tarefas.objects.get(id=i)
            consulta.tarefas.add(tarefa)

        consulta.save()

        messages.add_message(
            request, constants.SUCCESS, "Registro de consulta adicionado com sucesso"
        )
        return redirect("paciente_view", id=id)


@login_required
@require_POST
def atualizar_paciente(request, id):
    pagamento_em_dia = request.POST.get("pagamento_em_dia")
    paciente = _paciente_do_usuario(request, id)
    status = True if pagamento_em_dia == "ativo" else False
    paciente.pagamento_em_dia = status
    paciente.save()

    return redirect("paciente_view", id=id)


@login_required
@require_POST
def excluir_consulta(request, id):
    consulta = get_object_or_404(Consultas, id=id, paciente__psicologo=request.user)
    paciente_id = consulta.paciente.id
    consulta.delete()
    messages.add_message(request, constants.SUCCESS, "Consulta excluída com sucesso")
    return redirect("paciente_view", id=paciente_id)


def consulta_publica(request, id):
    consulta = get_object_or_404(Consultas, id=id)
    if not consulta.paciente.pagamento_em_dia:
        raise Http404("Consulta não pública")

    Visualizacoes.objects.create(consulta=consulta, ip=request.META.get("REMOTE_ADDR"))
    return render(request, "consulta_publica.html", {"consulta": consulta})
