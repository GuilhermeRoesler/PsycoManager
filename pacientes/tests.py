from io import BytesIO

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse
from PIL import Image

from .models import Consultas, Pacientes, Tarefas, Visualizacoes


def _imagem_teste(nome="foto.jpg"):
    buffer = BytesIO()
    Image.new("RGB", (10, 10), color="red").save(buffer, format="JPEG")
    return SimpleUploadedFile(nome, buffer.getvalue(), content_type="image/jpeg")


def _video_teste(nome="video.mp4"):
    return SimpleUploadedFile(nome, b"fake-video-bytes", content_type="video/mp4")


class PacientesModelTests(TestCase):
    def test_str_retorna_nome(self):
        paciente = Pacientes.objects.create(
            nome="Ana Silva",
            email="ana@example.com",
            queixa="TDAH",
            foto=_imagem_teste(),
        )
        self.assertEqual(str(paciente), "Ana Silva")


class ConsultaPublicaTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.paciente = Pacientes.objects.create(
            nome="João",
            email="joao@example.com",
            queixa="A",
            foto=_imagem_teste(),
            pagamento_em_dia=True,
        )
        self.tarefa = Tarefas.objects.create(
            tarefa="Respiração",
            instrucoes="Inspirar e expirar",
            frequencia="D",
        )
        self.consulta = Consultas.objects.create(
            humor=4,
            registro_geral="Notas privadas da sessão",
            video=_video_teste(),
            paciente=self.paciente,
        )
        self.consulta.tarefas.add(self.tarefa)

    def test_consulta_publica_ok_quando_pagamento_em_dia(self):
        url = reverse("consulta_publica", kwargs={"id": self.consulta.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Respiração")
        self.assertNotContains(response, "Notas privadas da sessão")
        self.assertEqual(Visualizacoes.objects.filter(consulta=self.consulta).count(), 1)

    def test_consulta_publica_404_quando_pagamento_atrasado(self):
        self.paciente.pagamento_em_dia = False
        self.paciente.save()

        url = reverse("consulta_publica", kwargs={"id": self.consulta.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(Visualizacoes.objects.filter(consulta=self.consulta).count(), 0)

    def test_link_publico_usa_reverse(self):
        path = reverse("consulta_publica", kwargs={"id": self.consulta.id})
        self.assertTrue(self.consulta.link_publico.endswith(path))

    def test_views_conta_totais_e_unicas(self):
        Visualizacoes.objects.create(consulta=self.consulta, ip="1.1.1.1")
        Visualizacoes.objects.create(consulta=self.consulta, ip="1.1.1.1")
        Visualizacoes.objects.create(consulta=self.consulta, ip="2.2.2.2")

        self.assertEqual(self.consulta.views, "3 - 2")


class PacientesViewsTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.paciente = Pacientes.objects.create(
            nome="Maria",
            email="maria@example.com",
            queixa="D",
            foto=_imagem_teste(),
            pagamento_em_dia=True,
        )

    def test_lista_pacientes_get(self):
        response = self.client.get(reverse("pacientes"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Maria")

    def test_detalhe_paciente_get(self):
        response = self.client.get(reverse("paciente_view", kwargs={"id": self.paciente.id}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Maria")

    def test_atualizar_pagamento(self):
        url = reverse("atualizar_paciente", kwargs={"id": self.paciente.id})
        response = self.client.post(url, {"pagamento_em_dia": "inativo"})

        self.paciente.refresh_from_db()
        self.assertFalse(self.paciente.pagamento_em_dia)
        self.assertEqual(response.status_code, 302)

    def test_excluir_consulta_exige_post(self):
        consulta = Consultas.objects.create(
            humor=2,
            registro_geral="x",
            video=_video_teste(),
            paciente=self.paciente,
        )
        url = reverse("excluir_consulta", kwargs={"id": consulta.id})

        response_get = self.client.get(url)
        self.assertEqual(response_get.status_code, 405)
        self.assertTrue(Consultas.objects.filter(id=consulta.id).exists())

        response_post = self.client.post(url)
        self.assertEqual(response_post.status_code, 302)
        self.assertFalse(Consultas.objects.filter(id=consulta.id).exists())
