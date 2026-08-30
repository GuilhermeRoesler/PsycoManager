from django.contrib import admin

from .models import Consultas, Pacientes, Tarefas


@admin.register(Pacientes)
class PacientesAdmin(admin.ModelAdmin):
    list_display = ("nome", "email", "psicologo", "queixa", "pagamento_em_dia")
    list_filter = ("queixa", "pagamento_em_dia", "psicologo")
    search_fields = ("nome", "email")


admin.site.register(Consultas)
admin.site.register(Tarefas)
