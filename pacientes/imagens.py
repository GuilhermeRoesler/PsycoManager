"""Processamento e validação de fotos de pacientes."""

from __future__ import annotations

import os
import re
from io import BytesIO

from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from PIL import Image, ImageOps

FOTO_MAX_BYTES = 5 * 1024 * 1024  # 5 MB
FOTO_MAX_LADO = 512
FOTO_VARIANTES = (40, 80, 128)
FOTO_QUALIDADE = 80
TIPOS_PERMITIDOS = frozenset(
    {"image/jpeg", "image/jpg", "image/png", "image/webp", "image/gif"}
)


class FotoInvalida(Exception):
    """Upload de foto rejeitado (tipo, tamanho ou conteúdo)."""


def caminho_variante(nome: str, tamanho: int) -> str:
    root, _ext = os.path.splitext(nome)
    return f"{root}_{tamanho}.webp"


def _nome_seguro(nome: str | None) -> str:
    base = os.path.basename(nome or "foto")
    stem = os.path.splitext(base)[0]
    stem = re.sub(r"[^\w\-]+", "_", stem, flags=re.UNICODE).strip("._") or "foto"
    return f"{stem[:80]}.webp"


def validar_foto(arquivo) -> None:
    tamanho = getattr(arquivo, "size", None)
    if tamanho is not None and tamanho > FOTO_MAX_BYTES:
        raise FotoInvalida("A foto deve ter no máximo 5 MB.")
    if tamanho == 0:
        raise FotoInvalida("Ficheiro de imagem vazio.")

    content_type = (getattr(arquivo, "content_type", None) or "").lower()
    if content_type and content_type not in TIPOS_PERMITIDOS:
        raise FotoInvalida("Formato de imagem não suportado. Use JPEG, PNG, WebP ou GIF.")

    try:
        with Image.open(arquivo) as img:
            img.verify()
    except Exception as exc:
        raise FotoInvalida("Ficheiro de imagem inválido.") from exc
    finally:
        if hasattr(arquivo, "seek"):
            arquivo.seek(0)


def otimizar_foto(arquivo) -> ContentFile:
    """Redimensiona (máx. 512px) e converte para WebP."""
    with Image.open(arquivo) as img:
        img = ImageOps.exif_transpose(img)
        if img.mode in ("RGBA", "LA") or (img.mode == "P" and "transparency" in img.info):
            img = img.convert("RGBA")
            fundo = Image.new("RGB", img.size, (255, 255, 255))
            fundo.paste(img, mask=img.split()[-1])
            img = fundo
        elif img.mode != "RGB":
            img = img.convert("RGB")

        img.thumbnail((FOTO_MAX_LADO, FOTO_MAX_LADO), Image.Resampling.LANCZOS)
        buf = BytesIO()
        img.save(buf, format="WEBP", quality=FOTO_QUALIDADE, method=4)

    nome = _nome_seguro(getattr(arquivo, "name", None))
    return ContentFile(buf.getvalue(), name=nome)


def gerar_variantes(nome_foto: str) -> None:
    """Gera variantes 40/80/128 px a partir da foto principal já gravada."""
    if not nome_foto or not default_storage.exists(nome_foto):
        return

    with default_storage.open(nome_foto, "rb") as f:
        with Image.open(f) as img:
            img = ImageOps.exif_transpose(img)
            if img.mode != "RGB":
                img = img.convert("RGB")
            base = img.copy()

    for tamanho in FOTO_VARIANTES:
        variante = base.copy()
        variante.thumbnail((tamanho, tamanho), Image.Resampling.LANCZOS)
        buf = BytesIO()
        variante.save(buf, format="WEBP", quality=FOTO_QUALIDADE, method=4)
        caminho = caminho_variante(nome_foto, tamanho)
        if default_storage.exists(caminho):
            default_storage.delete(caminho)
        default_storage.save(caminho, ContentFile(buf.getvalue()))


def apagar_foto_e_variantes(nome_foto: str | None) -> None:
    if not nome_foto:
        return
    caminhos = [nome_foto, *[caminho_variante(nome_foto, s) for s in FOTO_VARIANTES]]
    for caminho in caminhos:
        if default_storage.exists(caminho):
            default_storage.delete(caminho)
