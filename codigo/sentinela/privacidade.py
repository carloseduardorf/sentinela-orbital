"""Privacidade e minimização de dados (LGPD).

Apoia a mitigação do vetor **V5** (vazamento de dados pessoais) e atende os
princípios de **minimização** e **pseudonimização** da LGPD:

- ``pseudonimizar`` : substitui um identificador por um pseudônimo estável e
  irreversível (HMAC) — permite análise sem expor a identidade real.
- ``coarsen_local`` : reduz a precisão da geolocalização a uma grade — para
  alertar uma *região* não é preciso a posição exata da pessoa.
- ``mascarar_contato`` : ofusca e-mail para exibição em telas/logs.
"""

from __future__ import annotations

import hashlib
import hmac


def pseudonimizar(identificador: str, chave: bytes, *, tamanho: int = 16) -> str:
    """Pseudônimo determinístico e irreversível via HMAC-SHA256.

    A mesma entrada gera sempre o mesmo pseudônimo (permite correlação para
    análise), mas não é possível voltar ao identificador original sem a chave.
    """
    digest = hmac.new(chave, identificador.encode("utf-8"), hashlib.sha256).hexdigest()
    return digest[:tamanho]


def coarsen_local(lat: float, lon: float, *, casas: int = 1) -> tuple[float, float]:
    """Reduz a precisão da localização (minimização de dados).

    Com ``casas=1`` a grade tem ~11 km — suficiente para alertar uma região
    sem rastrear o indivíduo.
    """
    return (round(float(lat), casas), round(float(lon), casas))


def mascarar_contato(email: str) -> str:
    """Mascara um e-mail para exibição: ``joao@x.com`` -> ``j***@x.com``."""
    nome, arroba, dominio = email.partition("@")
    if not arroba:
        return "***"
    visivel = nome[0] if nome else "*"
    return f"{visivel}{'*' * max(1, len(nome) - 1)}@{dominio}"
