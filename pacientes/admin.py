from django.contrib import admin

from .models import Consultas, Pacientes, Tarefas


@admin.register(Pacientes)
class PacientesAdmin(admin.ModelAdmin):
    list_display = ("nome", "email", "psicologo", "queixa", "pagamento_em_dia")
    list_filter = ("queixa", "pagamento_em_dia", "psicologo")
    search_fields = ("nome", "email")


@admin.register(Tarefas)
class TarefasAdmin(admin.ModelAdmin):
    list_display = ("tarefa", "psicologo", "frequencia")
    list_filter = ("frequencia", "psicologo")
    search_fields = ("tarefa",)


admin.site.register(Consultas)
