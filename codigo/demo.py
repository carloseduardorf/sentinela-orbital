"""Demonstração end-to-end dos controles de segurança da Sentinela Orbital.

Mostra cada controle FUNCIONANDO e, em seguida, um ATAQUE sendo bloqueado.

Uso:
    cd codigo
    python demo.py
"""

from __future__ import annotations

import secrets
import sys

from sentinela import acesso, limite, privacidade, senhas, telemetria

# Garante saída em UTF-8 (acentos corretos) em qualquer console do Windows.
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:  # pragma: no cover
    pass


def titulo(t: str) -> None:
    print("\n" + "=" * 66 + f"\n  {t}\n" + "=" * 66)


def ok(m: str) -> None:
    print(f"  [ OK ]  {m}")


def bloq(m: str) -> None:
    print(f"  [BLOQ]  {m}")


def main() -> None:
    chave_tel = secrets.token_bytes(32)  # chave HMAC dos sensores
    chave_tok = secrets.token_bytes(32)  # chave de assinatura dos tokens
    chave_pii = secrets.token_bytes(32)  # chave de pseudonimização

    # ------------------------------------------------------------------ #
    titulo("1) Integridade da telemetria  (vetores V1 / V2)")
    leitura = telemetria.assinar(
        {"sensor": "SP-zona-leste-07", "temp_c": 41.2, "regiao": "SP-LESTE"}, chave_tel
    )
    print(f"  Sensor envia leitura assinada: temp_c=41.2  assinatura={leitura['assinatura'][:16]}…")
    telemetria.verificar(leitura, chave_tel)
    ok("Ingestão aceitou a leitura íntegra.")

    adulterada = dict(leitura)
    adulterada["temp_c"] = 22.0  # atacante "esfria" a leitura para suprimir o alerta
    try:
        telemetria.verificar(adulterada, chave_tel)
    except telemetria.TelemetriaInvalida as e:
        bloq(f"Leitura adulterada (41.2 -> 22.0) REJEITADA: {e}")

    # ------------------------------------------------------------------ #
    titulo("2) Controle de acesso + RBAC  (privilégio mínimo)")
    tok_cidadao = acesso.emitir_token("cidadao:maria", "cidadao", chave_tok)
    tok_ana = acesso.emitir_token("op:ana", "operador", chave_tok)
    acesso.autorizar(tok_ana, "monitorar", chave_tok)
    ok("Operadora Ana autorizada a 'monitorar'.")
    try:
        acesso.autorizar(tok_cidadao, "monitorar", chave_tok)
    except acesso.AcessoNegado as e:
        bloq(f"Cidadã tentou 'monitorar': {e}")
    try:
        acesso.validar_token(tok_ana[:-3] + "xxx", chave_tok)
    except acesso.TokenInvalido as e:
        bloq(f"Token adulterado REJEITADO: {e}")

    # ------------------------------------------------------------------ #
    titulo("3) Alerta em massa — regra das duas pessoas  (vetor V4)")
    tok_bruno = acesso.emitir_token("op:bruno", "operador", chave_tok)
    try:
        acesso.disparar_alerta_massa([tok_ana], chave_tok)
    except acesso.AcessoNegado as e:
        bloq(f"Alerta com 1 aprovador BLOQUEADO: {e}")
    resultado = acesso.disparar_alerta_massa([tok_ana, tok_bruno], chave_tok)
    ok(f"Alerta disparado com 2 aprovadores distintos: {resultado['aprovadores']}")

    # ------------------------------------------------------------------ #
    titulo("4) Rate limiting / anti-DDoS  (vetor V3)")
    balde = limite.TokenBucket(capacidade=5, taxa_por_s=1)
    permitidas = sum(1 for _ in range(8) if balde.permitir(agora=0))
    ok(f"De 8 requisições em rajada, {permitidas} permitidas e {8 - permitidas} barradas.")

    # ------------------------------------------------------------------ #
    titulo("5) Hashing de senha")
    h = senhas.hash_senha("Sup3rS3nh4!")
    print(f"  Hash armazenado: {h[:40]}…")
    ok(f"Senha correta verifica  -> {senhas.verificar_senha('Sup3rS3nh4!', h)}")
    bloq(f"Senha errada verifica   -> {senhas.verificar_senha('senha-errada', h)}")

    # ------------------------------------------------------------------ #
    titulo("6) Privacidade / LGPD  (vetor V5)")
    print(f"  Pseudônimo de 'cpf:123.456.789-00' : {privacidade.pseudonimizar('cpf:123.456.789-00', chave_pii)}")
    print(f"  Local exato (-23.5610, -46.6560)   -> grade {privacidade.coarsen_local(-23.5610, -46.6560)}")
    print(f"  Contato mascarado                  : {privacidade.mascarar_contato('maria.silva@email.com')}")
    ok("Dados pessoais minimizados / pseudonimizados.")

    print("\n  >> Todos os controles funcionando. Ataques bloqueados. <<\n")


if __name__ == "__main__":
    main()
