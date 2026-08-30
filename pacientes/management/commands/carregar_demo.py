"""
Carrega dados de demonstração para o PsycoManager.

Uso:
  python manage.py carregar_demo
  python manage.py carregar_demo --limpar
"""

from __future__ import annotations

import io
import random
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.utils import timezone
from PIL import Image, ImageDraw, ImageFont

from pacientes.demo_auth import DEMO_EMAIL, DEMO_PASSWORD, DEMO_USERNAME
from pacientes.models import Consultas, Pacientes, Tarefas, Visualizacoes

# MP4 mínimo válido (sample curto) — suficiente para o <video> não rebentar no upload.
MINI_MP4 = bytes.fromhex(
    "00000018667479706d703432000000006d703432000000206d646174"
    "000000000000000000000000000000000000000000000000"
)

CORES_AVATAR = [
    (59, 130, 246),
    (16, 185, 129),
    (244, 63, 94),
    (245, 158, 11),
    (139, 92, 246),
    (14, 165, 233),
    (236, 72, 153),
    (34, 197, 94),
    (249, 115, 22),
    (99, 102, 241),
]

PACIENTES_DEMO = [
    ("Ana Beatriz Costa", "ana.costa@email.com", "(11) 98765-4321", "A", True),
    ("Bruno Henrique Lima", "bruno.lima@email.com", "(11) 97654-3210", "TDAH", True),
    ("Camila Ferreira Santos", "camila.santos@email.com", "(21) 99876-5432", "D", True),
    ("Diego Almeida Rocha", "diego.rocha@email.com", "(21) 98765-1098", "TAG", False),
    ("Eduarda Martins Souza", "eduarda.souza@email.com", "(31) 99123-4567", "A", True),
    ("Felipe Nogueira Dias", "felipe.dias@email.com", "(31) 98234-5678", "TDAH", True),
    ("Gabriela Pinto Azevedo", "gabriela.azevedo@email.com", "(41) 99789-0123", "D", True),
    ("Henrique Barbosa Melo", "henrique.melo@email.com", None, "TAG", True),
    ("Isabela Ribeiro Campos", "isabela.campos@email.com", "(51) 98111-2233", "A", False),
    ("João Pedro Oliveira", "joao.oliveira@email.com", "(51) 99222-3344", "TDAH", True),
    ("Larissa Mendes Duarte", "larissa.duarte@email.com", "(61) 98333-4455", "D", True),
    ("Marcelo Teixeira Ramos", "marcelo.ramos@email.com", "(61) 97444-5566", "A", True),
    ("Natália Correia Freitas", "natalia.freitas@email.com", "(71) 96555-6677", "TAG", True),
    ("Otávio Moreira Castro", "otavio.castro@email.com", "(71) 95666-7788", "TDAH", False),
    ("Patrícia Gomes Vieira", "patricia.vieira@email.com", "(81) 94777-8899", "D", True),
    ("Rafael Cardoso Nunes", "rafael.nunes@email.com", "(81) 93888-9900", "A", True),
    ("Sofia Carvalho Lopes", "sofia.lopes@email.com", "(85) 92999-0011", "TAG", True),
    ("Thiago Araújo Batista", "thiago.batista@email.com", None, "TDAH", True),
    ("Vanessa Monteiro Paiva", "vanessa.paiva@email.com", "(19) 91122-3344", "D", True),
    ("William Prado Cunha", "william.cunha@email.com", "(19) 92233-4455", "A", True),
]

TAREFAS_DEMO = [
    (
        "Diário de humor",
        "Anote 3 vezes ao dia (manhã, tarde e noite) o humor de 1 a 5 e o que estava a sentir.",
        "D",
    ),
    (
        "Respiração diafragmática",
        "Pratique 5 minutos de respiração lenta: inspire 4s, segure 2s, expire 6s.",
        "D",
    ),
    (
        "Exercício de grounding 5-4-3-2-1",
        "Identifique 5 coisas que vê, 4 que toca, 3 que ouve, 2 que cheira e 1 que saboreia.",
        "N",
    ),
    (
        "Registo de pensamentos automáticos",
        "Quando notar ansiedade, escreva a situação, o pensamento e uma alternativa mais realista.",
        "D",
    ),
    (
        "Caminhada consciente",
        "Caminhe 20 minutos prestando atenção ao ritmo dos passos e à respiração.",
        "1S",
    ),
    (
        "Higiene do sono",
        "Deite-se e levante-se à mesma hora; evite ecrãs 30 min antes de dormir.",
        "D",
    ),
    (
        "Lista de gratidão",
        "Escreva 3 acontecimentos positivos do dia, por mais pequenos que sejam.",
        "D",
    ),
    (
        "Exposição gradual",
        "Escolha uma situação de evitação leve e permaneça nela 10–15 minutos.",
        "2S",
    ),
    (
        "Revisão semanal de objetivos",
        "Releia as metas da terapia e assinale o progresso da semana.",
        "1S",
    ),
    (
        "Técnica Pomodoro para foco",
        "Trabalhe 25 minutos sem interrupções e pause 5. Repita 3 ciclos.",
        "3S",
    ),
    (
        "Atividade prazerosa agendada",
        "Reserve um bloco de 45 minutos para algo que goste, sem culpabilização.",
        "2S",
    ),
    (
        "Meditação guiada curta",
        "Faça 10 minutos de meditação com áudio ou app, focando na respiração.",
        "1S",
    ),
    (
        "Assertividade em 3 passos",
        "Pratique: descrever o facto, expressar o sentimento, pedir a mudança desejada.",
        "N",
    ),
    (
        "Monitorização de energia",
        "Marque ao longo do dia momentos de baixa energia e o que os antecedeu.",
        "D",
    ),
]

REGISTROS = [
    "Sessão focada em estratégias de regulação emocional. Paciente relatou melhora parcial no sono.",
    "Trabalho de reestruturação cognitiva sobre pensamentos de autocrítica. Boa adesão às tarefas.",
    "Exploração de gatilhos de ansiedade em contexto laboral. Combinámos exposição gradual.",
    "Sessão mais difícil: humor baixo e evitação social. Validação e plano de segurança emocional.",
    "Revisão de progresso. Paciente identificou padrões de procrastinação ligados a perfeccionismo.",
    "Técnicas de grounding praticadas em sessão. Redução notável da intensidade ansiosa no momento.",
    "Discussão sobre limites interpessoais. Homework: ensaio de comunicação assertiva.",
    "Foco em rotina e higiene do sono. Humor estável; engajamento elevado nas tarefas.",
    "Processamento de episódio de irritabilidade. Identificados pensamentos dicotómicos.",
    "Sessão de consolidação: paciente verbalizou insights sobre ciclo ruminação–evitação.",
    "Abordagem de TDAH: organização da semana e uso de alarmes externos. Bom feedback.",
    "Espaço para ventilação emocional. Encerrámos com lista de recursos de apoio.",
]


def _iniciais(nome: str) -> str:
    partes = [p for p in nome.split() if p]
    if len(partes) >= 2:
        return (partes[0][0] + partes[-1][0]).upper()
    return partes[0][:2].upper()


def _fonte_avatar(tamanho: int = 96):
    candidatos = (
        "arial.ttf",
        "C:/Windows/Fonts/arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
    )
    for caminho in candidatos:
        try:
            return ImageFont.truetype(caminho, tamanho)
        except OSError:
            continue
    # Fallback portátil (Render/Linux sem Arial) — Pillow >= 10.1
    return ImageFont.load_default(size=tamanho)


def _gerar_foto(nome: str, indice: int) -> ContentFile:
    cor = CORES_AVATAR[indice % len(CORES_AVATAR)]
    img = Image.new("RGB", (256, 256), cor)
    draw = ImageDraw.Draw(img)
    texto = _iniciais(nome)
    font = _fonte_avatar(96)

    bbox = draw.textbbox((0, 0), texto, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.text(((256 - tw) / 2, (256 - th) / 2 - 8), texto, fill=(255, 255, 255), font=font)

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return ContentFile(buf.getvalue(), name=f"demo_{indice + 1:02d}_{texto.lower()}.png")


def _gerar_video(indice: int) -> ContentFile:
    return ContentFile(MINI_MP4, name=f"demo_consulta_{indice:03d}.mp4")


class Command(BaseCommand):
    help = "Carrega pacientes, tarefas, consultas e visualizações de demonstração."

    def add_arguments(self, parser):
        parser.add_argument(
            "--limpar",
            action="store_true",
            help="Apaga pacientes, consultas, visualizações e tarefas antes de carregar.",
        )
        parser.add_argument(
            "--sem-superuser",
            action="store_true",
            help="Não cria o utilizador admin de demo.",
        )

    def handle(self, *args, **options):
        rng = random.Random(42)

        if options["limpar"]:
            self.stdout.write("A limpar dados existentes...")
            Visualizacoes.objects.all().delete()
            Consultas.objects.all().delete()
            Pacientes.objects.all().delete()
            Tarefas.objects.all().delete()

        if Pacientes.objects.exists() and not options["limpar"]:
            self.stdout.write(
                self.style.WARNING("Já existem pacientes. Use --limpar para recriar os dados demo.")
            )
            return

        self.stdout.write("A criar tarefas...")
        tarefas = [
            Tarefas.objects.create(tarefa=t, instrucoes=i, frequencia=f) for t, i, f in TAREFAS_DEMO
        ]

        self.stdout.write("A criar conta demo e pacientes...")
        User = get_user_model()
        demo_user, created = User.objects.get_or_create(
            username=DEMO_USERNAME,
            defaults={"email": DEMO_EMAIL},
        )
        demo_user.set_password(DEMO_PASSWORD)
        demo_user.is_staff = False
        demo_user.is_superuser = False
        demo_user.save()
        if created:
            self.stdout.write(self.style.SUCCESS(f"Conta demo criada: {DEMO_USERNAME} / {DEMO_PASSWORD}"))
        else:
            self.stdout.write(f"Conta demo atualizada: {DEMO_USERNAME} / {DEMO_PASSWORD}")

        pacientes = []
        for idx, (nome, email, telefone, queixa, pagamento) in enumerate(PACIENTES_DEMO):
            p = Pacientes(
                psicologo=demo_user,
                nome=nome,
                email=email,
                telefone=telefone,
                queixa=queixa,
                pagamento_em_dia=pagamento,
            )
            p.foto.save(f"demo_{idx + 1:02d}.png", _gerar_foto(nome, idx), save=False)
            p.save()
            pacientes.append(p)

        self.stdout.write("A criar consultas e visualizações...")
        agora = timezone.now()
        consulta_idx = 0
        total_consultas = 0
        total_views = 0

        for p_idx, paciente in enumerate(pacientes):
            n_consultas = rng.randint(2, 5)
            for c_offset in range(n_consultas):
                consulta_idx += 1
                consulta = Consultas(
                    humor=rng.randint(1, 5),
                    registro_geral=rng.choice(REGISTROS),
                    paciente=paciente,
                )
                consulta.video.save(
                    f"demo_consulta_{consulta_idx:03d}.mp4",
                    _gerar_video(consulta_idx),
                    save=False,
                )
                consulta.save()

                n_tarefas = rng.randint(2, 5)
                consulta.tarefas.set(rng.sample(tarefas, n_tarefas))

                # Datas espalhadas pelas últimas ~12 semanas (bypass auto_now)
                dias_atras = (p_idx * 3) + (c_offset * 7) + rng.randint(0, 3)
                data = agora - timedelta(days=dias_atras, hours=rng.randint(8, 18))
                Consultas.objects.filter(pk=consulta.pk).update(data=data)
                total_consultas += 1

                # Mais views nas consultas recentes / pacientes em dia
                if paciente.pagamento_em_dia:
                    n_views = rng.randint(1, 8)
                else:
                    n_views = rng.randint(0, 2)

                ips = {f"192.168.{rng.randint(0, 3)}.{rng.randint(1, 254)}" for _ in range(n_views)}
                for ip in ips:
                    Visualizacoes.objects.create(consulta=consulta, ip=ip)
                    total_views += 1

        if not options["sem_superuser"]:
            User = get_user_model()
            if not User.objects.filter(username="admin").exists():
                User.objects.create_superuser("admin", "admin@psycomanager.local", "admin123")
                self.stdout.write(self.style.SUCCESS("Superuser criado: admin / admin123"))
            else:
                self.stdout.write("Superuser 'admin' já existia — mantido.")

        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS("Dados demo carregados:"))
        self.stdout.write(f"  • {len(pacientes)} pacientes")
        self.stdout.write(f"  • {len(tarefas)} tarefas")
        self.stdout.write(f"  • {total_consultas} consultas")
        self.stdout.write(f"  • {total_views} visualizações")
        self.stdout.write("")
        self.stdout.write(f"Login: http://127.0.0.1:8000/entrar/  ({DEMO_USERNAME} / {DEMO_PASSWORD})")
        self.stdout.write("Admin: http://127.0.0.1:8000/admin/  (admin / admin123)")
