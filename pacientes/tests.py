from io import BytesIO

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse
from PIL import Image

from .demo_auth import DEMO_PASSWORD, DEMO_USERNAME
from .models import Consultas, Pacientes, Tarefas, Visualizacoes


def _imagem_teste(nome="foto.jpg"):
    buffer = BytesIO()
    Image.new("RGB", (10, 10), color="red").save(buffer, format="JPEG")
    return SimpleUploadedFile(nome, buffer.getvalue(), content_type="image/jpeg")


def _video_teste(nome="video.mp4"):
    return SimpleUploadedFile(nome, b"fake-video-bytes", content_type="video/mp4")


class PacientesModelTests(TestCase):
    def test_str_retorna_nome(self):
        user = User.objects.create_user("psico", password="senha123")
        paciente = Pacientes.objects.create(
            psicologo=user,
            nome="Ana Silva",
            email="ana@example.com",
            queixa="TDAH",
            foto=_imagem_teste(),
        )
        self.assertEqual(str(paciente), "Ana Silva")


class ConsultaPublicaTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user("psico", password="senha123")
        self.paciente = Pacientes.objects.create(
            psicologo=self.user,
            nome="João",
            email="joao@example.com",
            queixa="A",
            foto=_imagem_teste(),
            pagamento_em_dia=True,
        )
        self.tarefa = Tarefas.objects.create(
            psicologo=self.user,
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


class AuthTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_login_mostra_credenciais_demo(self):
        response = self.client.get(reverse("login"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, DEMO_USERNAME)
        self.assertContains(response, DEMO_PASSWORD)

    def test_login_ok(self):
        user, _ = User.objects.get_or_create(username=DEMO_USERNAME)
        user.set_password(DEMO_PASSWORD)
        user.save()
        response = self.client.post(
            reverse("login"),
            {"username": DEMO_USERNAME, "password": DEMO_PASSWORD},
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("pacientes"))

    def test_registo_cria_conta_e_entra(self):
        response = self.client.post(
            reverse("registo"),
            {
                "username": "nova",
                "email": "nova@example.com",
                "password": "senha123",
                "password2": "senha123",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username="nova").exists())
        # Conta nova não vê pacientes de outros
        outro = User.objects.create_user("outro", password="senha123")
        Pacientes.objects.create(
            psicologo=outro,
            nome="Só do outro",
            email="o@example.com",
            queixa="A",
            foto=_imagem_teste(),
        )
        lista = self.client.get(reverse("pacientes"))
        self.assertEqual(lista.status_code, 200)
        self.assertNotContains(lista, "Só do outro")

    def test_rotas_privadas_exigem_login(self):
        response = self.client.get(reverse("pacientes"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("login"), response.url)


class PacientesViewsTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user("psico", password="senha123")
        self.outro = User.objects.create_user("outro", password="senha123")
        self.client.login(username="psico", password="senha123")
        self.paciente = Pacientes.objects.create(
            psicologo=self.user,
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

    def test_nao_ve_paciente_de_outro_psicologo(self):
        Pacientes.objects.create(
            psicologo=self.outro,
            nome="Paciente Alheio",
            email="alheio@example.com",
            queixa="A",
            foto=_imagem_teste("alheio.jpg"),
        )
        response = self.client.get(reverse("pacientes"))
        self.assertNotContains(response, "Paciente Alheio")

        detalhe = self.client.get(
            reverse("paciente_view", kwargs={"id": Pacientes.objects.get(nome="Paciente Alheio").id})
        )
        self.assertEqual(detalhe.status_code, 404)

    def test_lista_pacientes_filtro_e_paginacao(self):
        for i in range(21):
            Pacientes.objects.create(
                psicologo=self.user,
                nome=f"Paciente {i:02d}",
                email=f"p{i}@example.com",
                queixa="A",
                foto=_imagem_teste(f"foto{i}.jpg"),
            )

        response = self.client.get(reverse("pacientes"), {"queixa": "A"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["page_obj"].paginator.num_pages, 2)
        self.assertTrue(response.context["page_obj"].has_next())

        page2 = self.client.get(reverse("pacientes"), {"queixa": "A", "page": 2})
        self.assertEqual(page2.status_code, 200)
        self.assertEqual(page2.context["page_obj"].number, 2)

    def test_paginas_erro_usam_templates(self):
        with self.settings(DEBUG=False):
            r404 = self.client.get("/rota-inexistente-xyz/")
            self.assertEqual(r404.status_code, 404)
            self.assertTemplateUsed(r404, "404.html")
            self.assertContains(r404, "Página não encontrada", status_code=404)

        from django.core.exceptions import PermissionDenied
        from django.test import RequestFactory
        from django.views.defaults import permission_denied

        request = RequestFactory().get("/")
        r403 = permission_denied(request, PermissionDenied("negado"))
        self.assertEqual(r403.status_code, 403)
        self.assertIn(b"Acesso negado", r403.content)

    def test_detalhe_paciente_get(self):
        response = self.client.get(reverse("paciente_view", kwargs={"id": self.paciente.id}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Maria")

    def test_atualizar_paciente_dados(self):
        url = reverse("atualizar_paciente", kwargs={"id": self.paciente.id})
        response = self.client.post(
            url,
            {
                "nome": "Maria Silva",
                "email": "maria.nova@example.com",
                "telefone": "11999999999",
                "queixa": "A",
                "pagamento_em_dia": "inativo",
            },
        )

        self.paciente.refresh_from_db()
        self.assertEqual(self.paciente.nome, "Maria Silva")
        self.assertEqual(self.paciente.email, "maria.nova@example.com")
        self.assertEqual(self.paciente.queixa, "A")
        self.assertFalse(self.paciente.pagamento_em_dia)
        self.assertEqual(response.status_code, 302)

    def test_consulta_sem_video(self):
        url = reverse("paciente_view", kwargs={"id": self.paciente.id})
        response = self.client.post(
            url,
            {"humor": "4", "registro_geral": "Sem gravação"},
        )
        self.assertEqual(response.status_code, 302)
        consulta = Consultas.objects.get(paciente=self.paciente)
        self.assertFalse(bool(consulta.video))

        publica = self.client.get(reverse("consulta_publica", kwargs={"id": consulta.id}))
        self.assertEqual(publica.status_code, 200)
        self.assertContains(publica, "não tem gravação")

    def test_crud_tarefas(self):
        lista = self.client.get(reverse("tarefas"))
        self.assertEqual(lista.status_code, 200)

        criar = self.client.post(
            reverse("tarefas"),
            {
                "tarefa": "Diário de gratidão",
                "instrucoes": "Escrever 3 itens",
                "frequencia": "D",
            },
        )
        self.assertEqual(criar.status_code, 302)
        tarefa = Tarefas.objects.get(psicologo=self.user, tarefa="Diário de gratidão")

        editar = self.client.post(
            reverse("atualizar_tarefa", kwargs={"id": tarefa.id}),
            {
                "tarefa": "Diário",
                "instrucoes": "Escrever 5 itens",
                "frequencia": "1S",
            },
        )
        self.assertEqual(editar.status_code, 302)
        tarefa.refresh_from_db()
        self.assertEqual(tarefa.tarefa, "Diário")
        self.assertEqual(tarefa.frequencia, "1S")

        excluir = self.client.post(reverse("excluir_tarefa", kwargs={"id": tarefa.id}))
        self.assertEqual(excluir.status_code, 302)
        self.assertFalse(Tarefas.objects.filter(id=tarefa.id).exists())

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
