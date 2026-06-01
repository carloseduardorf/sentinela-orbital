"""Rate limiting (anti-DDoS) com algoritmo *token bucket*.

Mitiga o vetor **V3** (indisponibilidade/DDoS no pico): cada cliente tem um
"balde" de fichas que reabastece a uma taxa fixa. Sem ficha, a requisição é
recusada — absorvendo rajadas e protegendo a API de alertas no momento crítico.

O parâmetro ``agora`` permite testes determinísticos (relógio injetável).
"""

from __future__ import annotations

import time


class TokenBucket:
    """Balde de fichas: ``capacidade`` fichas, reabastecidas a ``taxa_por_s``/s."""

    def __init__(self, capacidade: float, taxa_por_s: float) -> None:
        self.capacidade = float(capacidade)
        self.taxa_por_s = float(taxa_por_s)
        self._tokens = float(capacidade)
        self._ultimo: float | None = None

    def permitir(self, *, agora: float | None = None, custo: float = 1.0) -> bool:
        """Tenta consumir ``custo`` fichas. Retorna True se permitido."""
        agora = time.monotonic() if agora is None else float(agora)
        if self._ultimo is None:
            self._ultimo = agora
        decorrido = max(0.0, agora - self._ultimo)
        self._tokens = min(self.capacidade, self._tokens + decorrido * self.taxa_por_s)
        self._ultimo = agora
        if self._tokens >= custo:
            self._tokens -= custo
            return True
        return False


class LimitadorPorChave:
    """Mantém um TokenBucket por chave (ex.: IP, token, sensor)."""

    def __init__(self, capacidade: float, taxa_por_s: float) -> None:
        self.capacidade = capacidade
        self.taxa_por_s = taxa_por_s
        self._baldes: dict[str, TokenBucket] = {}

    def permitir(self, chave: str, *, agora: float | None = None, custo: float = 1.0) -> bool:
        balde = self._baldes.get(chave)
        if balde is None:
            balde = TokenBucket(self.capacidade, self.taxa_por_s)
            self._baldes[chave] = balde
        return balde.permitir(agora=agora, custo=custo)
