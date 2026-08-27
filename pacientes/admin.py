from django.contrib import admin

from .models import Consultas, Pacientes, Tarefas

admin.site.register(Pacientes)
admin.site.register(Consultas)
admin.site.register(Tarefas)
