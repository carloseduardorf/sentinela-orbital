"""Hashing forte de credenciais.

Senhas **nunca** são guardadas em texto puro. Usamos ``scrypt`` (KDF
memória-dura, disponível na biblioteca padrão) com *salt* aleatório por senha.
Em produção a recomendação é **Argon2id**; o scrypt é o substituto da stdlib
para manter este PoC sem dependências externas.

Formato armazenado: ``scrypt$n$r$p$salt_b64$hash_b64``.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import secrets

# Parâmetros de custo (n é potência de 2). ~16 MB de memória por verificação.
_N, _R, _P, _DKLEN = 2 ** 14, 8, 1, 32
_MAXMEM = 64 * 1024 * 1024


def hash_senha(senha: str, *, n: int = _N, r: int = _R, p: int = _P) -> str:
    """Gera o hash scrypt de uma senha, com salt aleatório de 16 bytes."""
    salt = secrets.token_bytes(16)
    dk = hashlib.scrypt(
        senha.encode("utf-8"), salt=salt, n=n, r=r, p=p, dklen=_DKLEN, maxmem=_MAXMEM
    )
    return f"scrypt${n}${r}${p}${base64.b64encode(salt).decode()}${base64.b64encode(dk).decode()}"


def verificar_senha(senha: str, armazenado: str) -> bool:
    """Verifica a senha contra o hash armazenado (comparação em tempo constante)."""
    try:
        algo, n, r, p, salt_b64, hash_b64 = armazenado.split("$")
        if algo != "scrypt":
            return False
        salt = base64.b64decode(salt_b64)
        esperado = base64.b64decode(hash_b64)
        dk = hashlib.scrypt(
            senha.encode("utf-8"),
            salt=salt,
            n=int(n),
            r=int(r),
            p=int(p),
            dklen=len(esperado),
            maxmem=_MAXMEM,
        )
    except (ValueError, TypeError):
        return False
    return hmac.compare_digest(dk, esperado)
