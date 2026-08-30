from django.urls import path

from . import views

urlpatterns = [
    path("", views.pacientes, name="pacientes"),
    path("tarefas/", views.tarefas_view, name="tarefas"),
    path("tarefas/<int:id>/atualizar", views.atualizar_tarefa, name="atualizar_tarefa"),
    path("tarefas/<int:id>/excluir", views.excluir_tarefa, name="excluir_tarefa"),
    path("<int:id>", views.pacientes_view, name="paciente_view"),
    path("atualizar_paciente/<int:id>", views.atualizar_paciente, name="atualizar_paciente"),
    path("excluir_consulta/<int:id>", views.excluir_consulta, name="excluir_consulta"),
    path("consulta_publica/<int:id>", views.consulta_publica, name="consulta_publica"),
]
