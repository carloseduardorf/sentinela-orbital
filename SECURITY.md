# Sentinela Orbital — Capítulo de Cybersecurity (GS)

Documento de cobertura dos controles de segurança, mapeando cada item dos
**4 pilares** do enunciado da Global Solution para a análise (em
[`docs/seguranca/`](docs/seguranca)) e, quando há código, para o(s) módulo(s)
do PoC e o(s) teste(s) que o verificam.

> **Contexto:** Sentinela Orbital — plataforma de alerta de **ondas de calor
> extremo** com dados orbitais (economia espacial). É um sistema de **segurança
> pública** e trata dados pessoais **sensíveis** (localização + saúde):
> silenciar um alerta real ou forjar um falso é **risco à vida**.
>
> **Escopo:** a camada de segurança da plataforma — threat modeling, controles,
> governança/compliance e resiliência. Cobre **100% dos 4 pilares (10/10 pts)**.

## Integrantes do grupo

| Nome | RM |
|---|---|
| Carlos Eduardo | 556785 |
| Giulia Rocha | 558084 |
| Caio Rossini | 555084 |
| Gabriel Danius | 555747 |

---

## 1 · Análise de Riscos e Ameaças (Threat Modeling) — 2 pts

| Item da rubrica | Como cobrimos | Análise | Teste(s) |
|---|---|---|---|
| **Identificação de ativos** | Inventário classificado por **CIA** (telemetria IoT, dados orbitais, banco geoespacial, modelo de IA, **PII sensível**, segredos, logs) + definição das *joias da coroa* | [`01-threat-modeling.md`](docs/seguranca/01-threat-modeling.md) | — |
| **Modelo de ameaças (≥3 vetores)** | **6 vetores** mapeados em **STRIDE**: V1 interceptação/spoofing, V2 data poisoning, V3 DDoS, V4 sequestro do Motor de Alertas, V5 vazamento de PII, V6 cadeia de suprimentos | [`01-threat-modeling.md`](docs/seguranca/01-threat-modeling.md) | toda a suíte (cada teste = um ataque bloqueado) |

## 2 · Arquitetura de Segurança (Controles) — 3 pts

| Item da rubrica | Como cobrimos | Análise | Arquivo(s) | Teste(s) |
|---|---|---|---|---|
| **Controles de acesso** (MFA, privilégio mínimo) | Tokens assinados (HMAC) com expiração; **RBAC default-deny**; **regra das duas pessoas** para alerta em massa | [`02`](docs/seguranca/02-arquitetura-de-seguranca.md) | [`acesso.py`](codigo/sentinela/acesso.py) | `test_token_*`, `test_rbac_*`, `test_duas_pessoas_*` |
| **Proteção de dados** (trânsito e repouso) | **HMAC** na telemetria (integridade fim-a-fim, anti-replay); AES-256 em repouso (arquitetura); **scrypt** + salt para senhas | [`02`](docs/seguranca/02-arquitetura-de-seguranca.md) | [`telemetria.py`](codigo/sentinela/telemetria.py), [`senhas.py`](codigo/sentinela/senhas.py) | `test_adulteracao_rejeitada`, `test_replay_*`, `test_*_senha_*` |
| **Segurança da infraestrutura** (Zero Trust, WAF, logs) | Zero Trust + microssegmentação; WAF + **rate limiting** anti-DDoS; SIEM + auditoria WORM | [`02`](docs/seguranca/02-arquitetura-de-seguranca.md) | [`limite.py`](codigo/sentinela/limite.py) | `test_rajada_barra_excedente`, `test_reabastece_com_o_tempo` |

## 3 · Governança e Compliance — 2 pts

| Item da rubrica | Como cobrimos | Análise | Arquivo(s) | Teste(s) |
|---|---|---|---|---|
| **Alinhamento normativo (ISO 27001)** | SGSI com ciclo **PDCA**; gestão de riscos (identificar→avaliar→tratar); mapeamento ao Anexo A; SoA | [`03`](docs/seguranca/03-governanca-e-compliance.md) | — | — |
| **Privacidade (LGPD)** | Bases legais; minimização; **pseudonimização** (HMAC) e coarsening de localização; direitos do titular; notificação à ANPD | [`03`](docs/seguranca/03-governanca-e-compliance.md) | [`privacidade.py`](codigo/sentinela/privacidade.py) | `test_pseudonimo_*`, `test_coarsen_local_*`, `test_mascarar_contato` |

## 4 · Resiliência e Continuidade — 3 pts

| Item da rubrica | Como cobrimos | Análise | Arquivo(s) | Teste(s) |
|---|---|---|---|---|
| **Plano de resposta a incidentes** | Ciclo **NIST 800-61** (preparação → detecção → contenção → erradicação → recuperação → lições); cenário **Sev-1** (sequestro do Motor de Alertas); RTO 1h / RPO 15min; notificação à ANPD | [`04`](docs/seguranca/04-plano-de-resposta-a-incidentes.md) | [`acesso.py`](codigo/sentinela/acesso.py) (contenção: dupla aprovação + revogação) | `test_duas_pessoas_*`, `test_token_expirado_rejeitado` |

---

## Modelo de ameaças (resumo STRIDE)

| Ameaça | Mitigação principal | Onde |
|---|---|---|
| **S**poofing | HMAC na telemetria; tokens assinados com expiração | [`telemetria.py`](codigo/sentinela/telemetria.py), [`acesso.py`](codigo/sentinela/acesso.py) |
| **T**ampering | Assinatura rejeita dado alterado/replay; AES-256 em repouso; auditoria WORM | [`telemetria.py`](codigo/sentinela/telemetria.py), [`02`](docs/seguranca/02-arquitetura-de-seguranca.md) |
| **R**epudiation | Trilhas de auditoria imutáveis (WORM) + correlação | [`02`](docs/seguranca/02-arquitetura-de-seguranca.md) |
| **I**nformation Disclosure | Pseudonimização, minimização, criptografia em repouso | [`privacidade.py`](codigo/sentinela/privacidade.py), [`03`](docs/seguranca/03-governanca-e-compliance.md) |
| **D**enial of Service | Rate limit por bucket/IP; canais redundantes de alerta | [`limite.py`](codigo/sentinela/limite.py) |
| **E**levation of Privilege | RBAC default-deny; regra das duas pessoas | [`acesso.py`](codigo/sentinela/acesso.py) |

## Operações seguras e LGPD

- **Segredos por ambiente:** chaves de HMAC/token vivem em cofre (Vault), nunca no código; scanning de segredos no CI/CD.
- **Minimização & pseudonimização:** alerta por região (não por indivíduo); dashboards/ML por pseudônimo (LGPD).
- **Retenção:** prazo de expurgo para dado pessoal; histórico climático anonimizado.
- **Verificação de integridade:** telemetria assinada; auditoria em cadeia (WORM).
- **Notificação de incidente:** vazamento de PII (V5) aciona **ANPD** e titulares.

## Como executar a verificação local

```bash
cd codigo
python -m unittest discover -s tests -v
```

Resultado esperado: **29 testes passando**, cobrindo cada vetor do modelo de ameaças.
