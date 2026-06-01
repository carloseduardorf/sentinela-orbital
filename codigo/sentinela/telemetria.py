"""Integridade e autenticidade da telemetria dos sensores.

Mitiga os vetores **V1** (interceptação/spoofing) e **V2** (data poisoning):
cada leitura de sensor é assinada com **HMAC-SHA256**. A ingestão recompara a
assinatura e **rejeita** qualquer dado adulterado, forjado ou repetido (replay).

A assinatura cobre uma serialização *canônica* (chaves ordenadas) do payload,
de modo que mudar 1 bit do dado invalida a assinatura.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import time
from typing import Any


class TelemetriaInvalida(Exception):
    """Levantada quando a leitura falha na verificação de integridade."""


def _canonico(payload: dict[str, Any]) -> bytes:
    """Serialização determinística do payload, sem o campo de assinatura."""
    base = {k: v for k, v in payload.items() if k != "assinatura"}
    return json.dumps(
        base, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")


def assinar(payload: dict[str, Any], chave: bytes, *, agora: int | None = None) -> dict[str, Any]:
    """Assina uma leitura e devolve uma cópia com o campo ``assinatura``.

    Se o payload não tiver ``ts`` (timestamp), um é adicionado — ele entra na
    assinatura e serve para a proteção contra replay.
    """
    leitura = dict(payload)
    if "ts" not in leitura:
        leitura["ts"] = int(time.time()) if agora is None else int(agora)
    mac = hmac.new(chave, _canonico(leitura), hashlib.sha256).hexdigest()
    leitura["assinatura"] = mac
    return leitura


def verificar(
    leitura: dict[str, Any],
    chave: bytes,
    *,
    janela_s: int = 300,
    agora: int | None = None,
) -> bool:
    """Verifica a assinatura e a janela de tempo da leitura.

    Retorna ``True`` se válida; caso contrário levanta ``TelemetriaInvalida``.
    A comparação usa ``hmac.compare_digest`` (tempo constante) para evitar
    *timing attacks*.
    """
    if "assinatura" not in leitura:
        raise TelemetriaInvalida("leitura sem assinatura")

    esperado = hmac.new(chave, _canonico(leitura), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(esperado, str(leitura["assinatura"])):
        raise TelemetriaInvalida("assinatura não confere (dado adulterado ou chave inválida)")

    agora = int(time.time()) if agora is None else int(agora)
    try:
        ts = int(leitura.get("ts", 0))
    except (TypeError, ValueError):
        raise TelemetriaInvalida("timestamp inválido")
    if abs(agora - ts) > janela_s:
        raise TelemetriaInvalida("leitura fora da janela de tempo (possível replay)")

    return True
