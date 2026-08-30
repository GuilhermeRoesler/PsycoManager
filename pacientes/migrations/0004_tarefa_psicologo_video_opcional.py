import django.db.models.deletion
from django.contrib.auth.hashers import make_password
from django.conf import settings
from django.db import migrations, models


def atribuir_psicologo_tarefas(apps, schema_editor):
    User = apps.get_model("auth", "User")
    Tarefas = apps.get_model("pacientes", "Tarefas")

    demo, created = User.objects.get_or_create(
        username="demo",
        defaults={
            "email": "demo@psycomanager.local",
            "password": make_password("demo123"),
            "is_staff": False,
            "is_superuser": False,
        },
    )
    if not created and not demo.password:
        demo.password = make_password("demo123")
        demo.save(update_fields=["password"])

    Tarefas.objects.filter(psicologo__isnull=True).update(psicologo=demo)


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("pacientes", "0003_paciente_psicologo"),
    ]

    operations = [
        migrations.AddField(
            model_name="tarefas",
            name="psicologo",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="tarefas",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.RunPython(atribuir_psicologo_tarefas, noop_reverse),
        migrations.AlterField(
            model_name="tarefas",
            name="psicologo",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="tarefas",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AlterField(
            model_name="consultas",
            name="video",
            field=models.FileField(blank=True, null=True, upload_to="videos"),
        ),
    ]
