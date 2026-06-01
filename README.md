# Sentinela Orbital — Sprint Cybersecurity (Global Solution)

## Integrantes do grupo

| Nome | RM |
|---|---|
| Carlos Eduardo | 556785 |
| Giulia Rocha | 558084 |
| Caio Rossini | 555084 |
| Gabriel Danius | 555747 |

---

Capítulo de **Cybersecurity** da Global Solution (3ES — 1º semestre/2026, FIAP)
sobre a **Sentinela Orbital**: plataforma de monitoramento e alerta precoce de
**ondas de calor extremo** que combina dados orbitais (satélites de temperatura
de superfície) com sensores IoT terrestres para avisar Defesa Civil, saúde e
população. Esta entrega é a **camada de segurança** que dá longevidade e
confiança ao projeto.

A entrega tem duas partes que se reforçam:

- **Análise de segurança** completa nos 4 pilares do enunciado, em [`docs/seguranca/`](docs/seguranca).
- **PoC em Python** (sem dependências) que **implementa e testa** os controles, em [`codigo/`](codigo) — provando que cada vetor de ataque é bloqueado.

> Mapeamento item-a-item dos pilares com documentos e testes: ver [SECURITY.md](SECURITY.md).

---

## Cobertura da rubrica (4 pilares — 10 pts)

| # | Pilar | Pts | Análise | Evidência em código |
|---|---|:--:|---|---|
| 1 | Threat Modeling (ativos + ameaças STRIDE) | 2 | [01-threat-modeling.md](docs/seguranca/01-threat-modeling.md) | toda a suíte (cada teste = 1 ataque) |
| 2 | Arquitetura de Segurança (acesso, dados, infra) | 3 | [02-arquitetura-de-seguranca.md](docs/seguranca/02-arquitetura-de-seguranca.md) | `telemetria` · `acesso` · `senhas` · `limite` |
| 3 | Governança & Compliance (ISO 27001 + LGPD) | 2 | [03-governanca-e-compliance.md](docs/seguranca/03-governanca-e-compliance.md) | `privacidade` |
| 4 | Resiliência (resposta a incidentes NIST) | 3 | [04-plano-de-resposta-a-incidentes.md](docs/seguranca/04-plano-de-resposta-a-incidentes.md) | regra das duas pessoas em `acesso` |
| | **Total** | **10** | + [05-red-team-blue-team.md](docs/seguranca/05-red-team-blue-team.md) | **29 testes** |

---

## Arquitetura de defesa em profundidade

```
Fontes de dados                                     Consumo
  Satélites LST  --\                          /-->  App / Web do cidadão
  Sensores IoT   --|                          |-->  Defesa Civil & Saúde (API)
                   v                          ^
        +--------------------------------------------------+
        | Borda (Zero Trust)                               |
        |   API Gateway + WAF  ->  rate limit         (V3) |
        |   Ingestão: verifica HMAC/assinatura        (V1) |
        |--------------------------------------------------|
        |   AuthN/AuthZ: tokens assinados + RBAC default-deny
        |   Alerta em massa: regra das duas pessoas   (V4) |
        |   Dados: AES-256 em repouso + cripto de campo    |
        |   Privacidade: pseudonimização (LGPD)       (V5) |
        |   Logs centralizados + SIEM + auditoria (WORM)   |
        +--------------------------------------------------+
                   |                          |
                   v                          v
        Banco geoespacial (TLS)        Motor de Alertas (fail-safe)
```

A ordem é deliberada: a requisição passa por **tamanho/rate-limit** antes do
parser; a telemetria só entra se a **assinatura conferir**; o disparo em massa
exige **duas aprovações**; na dúvida, o sistema **degrada com segurança** (não
silencia um alerta real, não dispara um falso).

---

## Decisões de segurança (e por quê)

| Decisão | Alternativa rejeitada | Motivo |
|---|---|---|
| HMAC-SHA256 na telemetria do sensor | confiar só no TLS | Integridade fim-a-fim; rejeita sensor falso / dado adulterado (V1/V2). |
| HMAC sobre `payload + ts` + janela 5 min | assinar só o dado | Anti-replay. |
| `hmac.compare_digest` | comparação `==` | Evita timing attack. |
| Regra das duas pessoas p/ alerta em massa | um operador dispara sozinho | 1 conta comprometida não vira pânico (V4). |
| RBAC default-deny (privilégio mínimo) | papel amplo por padrão | Cidadão nunca opera o Motor de Alertas. |
| Argon2id (produção) / scrypt (PoC) | MD5 · SHA1 · bcrypt | KDF memória-dura: caro em GPU/ASIC. |
| AES-256-GCM em repouso | AES-CBC + HMAC | Confidencialidade + integridade num passo, sem padding oracle. |
| Pseudonimização HMAC | SHA-256 puro | Sem o salt não dá pra reverter por rainbow table (LGPD). |
| Múltiplos canais de alerta (push/SMS/API) | canal único | Disponibilidade no pico do calor (V3). |
| Fail-safe no Motor de Alertas | fail-open | Erra para o lado seguro: há vida em jogo. |

---

## Estrutura

```
sentinela-orbital/
  README.md                este arquivo
  SECURITY.md              cobertura dos pilares -> docs -> testes
  LICENSE                  MIT
  docs/seguranca/          análise completa (4 pilares + Red/Blue)
    00-visao-geral.md
    01-threat-modeling.md
    02-arquitetura-de-seguranca.md
    03-governanca-e-compliance.md
    04-plano-de-resposta-a-incidentes.md
    05-red-team-blue-team.md
  codigo/                  PoC em Python (sem dependências)
    demo.py                cenário end-to-end (controles + ataques)
    sentinela/             telemetria · acesso · senhas · limite · privacidade
    tests/                 29 testes (unittest), um bloco por controle
```

> O "cérebro" do projeto (base de conhecimento com ~28 notas interligadas) é
> mantido em paralelo num vault **Obsidian**.

---

## Como executar (PoC)

Requer apenas **Python 3.10+** (sem `pip install`).

```bash
cd codigo
python demo.py                             # cenário end-to-end (controles + ataques)
python -m unittest discover -s tests -v    # 29 testes — todos passando
```

---

## Testes (verificação dos controles)

Cada arquivo cobre caminho feliz **e** ataque bloqueado:

| Arquivo | Controle | Vetor |
|---|---|---|
| `tests/test_telemetria.py` | Assinatura HMAC + anti-replay | V1, V2 |
| `tests/test_acesso.py` | Tokens, RBAC, regra das duas pessoas | V4 |
| `tests/test_senhas.py` | Hash scrypt + salt | credenciais |
| `tests/test_limite.py` | Rate limiting (token bucket) | V3 |
| `tests/test_privacidade.py` | Pseudonimização / minimização | V5 |

Resultado esperado: **29 passed**.

---

## Modelo de ameaças (STRIDE)

| Ameaça | Mitigação | Onde |
|---|---|---|
| **S**poofing | HMAC na telemetria; tokens assinados | `codigo/sentinela/telemetria.py`, `acesso.py` |
| **T**ampering | Assinatura rejeita dado alterado; AES-256 em repouso | `telemetria.py`, [02](docs/seguranca/02-arquitetura-de-seguranca.md) |
| **R**epudiation | Trilhas de auditoria imutáveis (WORM) | [02](docs/seguranca/02-arquitetura-de-seguranca.md) |
| **I**nformation Disclosure | Pseudonimização, minimização, criptografia | `privacidade.py`, [03](docs/seguranca/03-governanca-e-compliance.md) |
| **D**enial of Service | Rate limiting; canais redundantes | `limite.py`, [02](docs/seguranca/02-arquitetura-de-seguranca.md) |
| **E**levation of Privilege | RBAC default-deny; regra das duas pessoas | `acesso.py` |

---

## Operação e LGPD

- **Dados sensíveis:** localização + vulnerabilidade de saúde → tratados sob a **LGPD** (base legal de proteção da vida / política pública; consentimento no app).
- **Minimização:** alerta por região, não por indivíduo; localização reduzida a uma grade.
- **Pseudonimização:** dashboards e ML operam por pseudônimo, sem expor identidade.
- **Resposta a incidentes:** ciclo NIST 800-61; vazamento de PII notifica **ANPD** e titulares ([04](docs/seguranca/04-plano-de-resposta-a-incidentes.md)).
- **Fail-safe:** o Motor de Alertas prioriza **não silenciar** um alerta real.

---

## Stack

- **PoC:** Python 3.10+ — **somente biblioteca padrão** (`hmac`, `hashlib`/`scrypt`, `secrets`, `unittest`). Zero dependências: roda em qualquer máquina com Python.
- **Produção (arquitetura proposta):** identidade OIDC/OAuth2, AES-256-GCM, TLS 1.3/mTLS, WAF + CDN/anycast, SIEM, CI/CD com SAST/DAST/SCA — detalhado em [`docs/seguranca/02-arquitetura-de-seguranca.md`](docs/seguranca/02-arquitetura-de-seguranca.md).

---

## Licença

MIT — ver [LICENSE](LICENSE).
