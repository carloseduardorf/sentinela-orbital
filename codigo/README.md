# 💻 PoC — Controles de Segurança da Sentinela Orbital

Prova de conceito **em Python puro (sem dependências externas)** que implementa,
de forma funcional e testada, os controles de segurança desenhados na
[análise da GS](../docs/seguranca/). Cada módulo mitiga um vetor do
[modelo de ameaças](../docs/seguranca/01-threat-modeling.md).

## Mapa código → ameaça → controle

| Módulo | Mitiga | O que faz |
|---|---|---|
| [`sentinela/telemetria.py`](sentinela/telemetria.py) | **V1, V2** | Assina (HMAC-SHA256) e verifica leituras de sensor; rejeita dado adulterado ou replay |
| [`sentinela/acesso.py`](sentinela/acesso.py) | **V4** | Tokens assinados, RBAC (privilégio mínimo) e regra das duas pessoas para alerta em massa |
| [`sentinela/senhas.py`](sentinela/senhas.py) | credenciais | Hash de senha com `scrypt` + salt (comparação em tempo constante) |
| [`sentinela/limite.py`](sentinela/limite.py) | **V3** | Rate limiting *token bucket* (anti-DDoS) |
| [`sentinela/privacidade.py`](sentinela/privacidade.py) | **V5** | Pseudonimização (HMAC) e minimização de localização (LGPD) |

## Como rodar

> Requer apenas **Python 3.10+** (nada de `pip install`).

```bash
cd codigo

# 1) Demonstração end-to-end (controles funcionando + ataques bloqueados)
python demo.py

# 2) Suíte de testes (caminho feliz E cenários de ataque)
python -m unittest discover -s tests -v
```

## Estrutura

```
codigo/
├── demo.py                  # cenário end-to-end narrado
├── sentinela/               # pacote com os controles
│   ├── telemetria.py
│   ├── acesso.py
│   ├── senhas.py
│   ├── limite.py
│   └── privacidade.py
└── tests/                   # testes unittest (happy path + ataques)
    ├── test_telemetria.py
    ├── test_acesso.py
    ├── test_senhas.py
    ├── test_limite.py
    └── test_privacidade.py
```

> ⚠️ **Escopo de PoC.** O foco é demonstrar os controles com primitivas
> corretas da stdlib (HMAC, scrypt, `secrets`, `compare_digest`). Em produção:
> Argon2id para senhas, **AES-256-GCM** para confidencialidade em repouso e um
> provedor de identidade (OIDC) — conforme descrito em
> [`02-arquitetura-de-seguranca.md`](../docs/seguranca/02-arquitetura-de-seguranca.md).
