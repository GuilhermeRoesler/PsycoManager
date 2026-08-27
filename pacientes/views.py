from django.contrib import messages
from django.contrib.messages import constants
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .models import Consultas, Pacientes, Tarefas, Visualizacoes


def pacientes(request):
    if request.method == "GET":
        pacientes_qs = Pacientes.objects.all()
        queixas = Pacientes.queixa_choices
        return render(request, "pacientes.html", {"queixas": queixas, "pacientes": pacientes_qs})
    elif request.method == "POST":
        nome = request.POST.get("nome")
        email = request.POST.get("email")
        telefone = request.POST.get("telefone")
        queixa = request.POST.get("queixa")
        foto = request.FILES.get("foto")

        if not nome or len(nome.strip()) == 0 or not foto:
            messages.add_message(request, constants.ERROR, "Preencha todos os campos")
            return redirect("pacientes")

        paciente = Pacientes(nome=nome, email=email, telefone=telefone, queixa=queixa, foto=foto)

        paciente.save()
        messages.add_message(request, constants.SUCCESS, "Cadastro realizado com sucesso")

        return redirect("pacientes")


def pacientes_view(request, id):
    paciente = get_object_or_404(Pacientes, id=id)
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


def atualizar_paciente(request, id):
    pagamento_em_dia = request.POST.get("pagamento_em_dia")
    paciente = get_object_or_404(Pacientes, id=id)
    status = True if pagamento_em_dia == "ativo" else False
    paciente.pagamento_em_dia = status
    paciente.save()

    return redirect("paciente_view", id=id)


@require_POST
def excluir_consulta(request, id):
    consulta = get_object_or_404(Consultas, id=id)
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
