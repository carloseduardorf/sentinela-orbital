"""Controle de acesso: autenticação, RBAC e regra das duas pessoas.

Mitiga o vetor **V4** (sequestro do Motor de Alertas):

- **Tokens assinados** (HMAC-SHA256) com expiração — não dá para forjar nem
  reaproveitar um token vencido.
- **RBAC** (privilégio mínimo): cada papel só tem as permissões necessárias.
- **Regra das duas pessoas** (*two-person rule*): disparar um alerta em massa
  exige a aprovação de **dois operadores distintos**.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import time
from typing import Any


class TokenInvalido(Exception):
    """Token mal formado, com assinatura inválida ou expirado."""


class AcessoNegado(Exception):
    """Identidade válida, mas sem permissão para a ação."""


# RBAC — privilégio mínimo. Cada papel recebe só o que precisa.
PERMISSOES: dict[str, set[str]] = {
    "cidadao": {"ver_dados_publicos", "gerir_proprio_perfil"},
    "parceiro": {"ver_dados_publicos", "consumir_api_alertas"},
    "operador": {"ver_dados_publicos", "consumir_api_alertas", "monitorar", "aprovar_alerta"},
    "admin": {
        "ver_dados_publicos",
        "consumir_api_alertas",
        "monitorar",
        "aprovar_alerta",
        "gerir_acessos",
    },
}


def _b64u(dados: bytes) -> str:
    return base64.urlsafe_b64encode(dados).rstrip(b"=").decode("ascii")


def _b64u_dec(texto: str) -> bytes:
    return base64.urlsafe_b64decode(texto + "=" * (-len(texto) % 4))


def emitir_token(sub: str, papel: str, chave: bytes, *, ttl_s: int = 900, agora: int | None = None) -> str:
    """Emite um token assinado (corpo.assinatura) para um sujeito e papel."""
    if papel not in PERMISSOES:
        raise ValueError(f"papel desconhecido: {papel!r}")
    agora = int(time.time()) if agora is None else int(agora)
    payload = {"sub": sub, "papel": papel, "exp": agora + ttl_s}
    corpo = _b64u(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8"))
    mac = _b64u(hmac.new(chave, corpo.encode("ascii"), hashlib.sha256).digest())
    return f"{corpo}.{mac}"


def validar_token(token: str, chave: bytes, *, agora: int | None = None) -> dict[str, Any]:
    """Valida assinatura e expiração; devolve o payload ou levanta TokenInvalido."""
    partes = token.split(".")
    if len(partes) != 2:
        raise TokenInvalido("formato inválido")
    corpo, mac = partes
    esperado = _b64u(hmac.new(chave, corpo.encode("ascii"), hashlib.sha256).digest())
    if not hmac.compare_digest(esperado, mac):
        raise TokenInvalido("assinatura inválida (token forjado ou chave errada)")
    payload = json.loads(_b64u_dec(corpo))
    agora = int(time.time()) if agora is None else int(agora)
    if agora >= int(payload.get("exp", 0)):
        raise TokenInvalido("token expirado")
    return payload


def tem_permissao(papel: str, permissao: str) -> bool:
    return permissao in PERMISSOES.get(papel, set())


def autorizar(token: str, permissao: str, chave: bytes, *, agora: int | None = None) -> dict[str, Any]:
    """Valida o token e checa a permissão. Levanta AcessoNegado se faltar."""
    payload = validar_token(token, chave, agora=agora)
    if not tem_permissao(payload["papel"], permissao):
        raise AcessoNegado(f"papel {payload['papel']!r} não pode {permissao!r}")
    return payload


def disparar_alerta_massa(aprovacoes: list[str], chave: bytes, *, agora: int | None = None) -> dict[str, Any]:
    """Regra das duas pessoas: exige >= 2 aprovadores DISTINTOS com a permissão
    ``aprovar_alerta``. Transforma "1 conta comprometida = pânico" em
    "2 contas comprometidas = pânico"."""
    aprovadores: set[str] = set()
    for token in aprovacoes:
        payload = autorizar(token, "aprovar_alerta", chave, agora=agora)
        aprovadores.add(payload["sub"])
    if len(aprovadores) < 2:
        raise AcessoNegado("alerta em massa exige 2 aprovadores distintos (regra das duas pessoas)")
    return {"status": "alerta_disparado", "aprovadores": sorted(aprovadores)}
