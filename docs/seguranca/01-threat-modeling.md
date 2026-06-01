# 01 · Análise de Riscos e Ameaças (Threat Modeling)

> **Pilar 1 — 2 pontos** · Identificação de ativos + modelo de ameaças.

## 1.1 Identificação de Ativos

Classificados pela tríade **CIA** (Confidencialidade · Integridade · Disponibilidade).

### Dados

| Ativo | Descrição | C | I | D |
|---|---|:--:|:--:|:--:|
| Telemetria de sensores IoT | Leituras de temp/umidade urbanas | 🟡 | 🔴 | 🟠 |
| Dados orbitais (LST) | Temperatura de superfície dos satélites | 🟢 | 🔴 | 🟠 |
| Banco geoespacial + série temporal | Histórico e tempo real | 🟡 | 🔴 | 🔴 |
| Modelo de IA / limiares | Lógica de detecção e previsão | 🟠 | 🔴 | 🟠 |
| PII de cidadãos | Contato, **localização**, **vulnerabilidade de saúde** | 🔴 | 🟠 | 🟡 |
| Credenciais & segredos | Chaves de API, tokens, senhas | 🔴 | 🔴 | 🟠 |
| Logs & trilhas de auditoria | Eventos de segurança | 🟠 | 🔴 | 🟠 |

🔴 crítico · 🟠 alto · 🟡 médio · 🟢 baixo

### Infraestrutura

Links de ingestão (satélite/IoT) · API Gateway + WAF · **Motor de Alertas** · cluster de contêineres · pipeline CI/CD · provedor de identidade (OIDC).

### 💎 Joias da coroa
1. **Motor de Alertas** — se comprometido, permite suprimir um alerta real ou forjar um falso (risco à vida).
2. **Integridade do dado de origem** — "lixo entra, lixo sai".
3. **PII sensível** — vazamento gera dano às pessoas e sanção da LGPD.

---

## 1.2 Modelo de Ameaças (STRIDE)

Usamos o framework **STRIDE** para não deixar nenhuma categoria de fora.

### Vetores de ataque

| Vetor | STRIDE | Descrição | Impacto |
|---|---|---|:--:|
| **V1** Interceptação / spoofing de dados | S, T | MITM no link de um sensor, ou sensor falso, altera a leitura → alerta não dispara | 🔴 |
| **V2** Manipulação de telemetria / data poisoning | T | Injeção contínua de dados falsos envenena o modelo (subestima ou superestima o calor) | 🔴 |
| **V3** Indisponibilidade / DDoS no pico | D | Flood na API de alertas **durante** uma onda de calor real → o aviso não chega | 🔴 |
| **V4** Sequestro do Motor de Alertas | E, S | Acesso indevido (phishing) dispara alertas falsos em massa ou silencia um real | 🔴 |
| **V5** Vazamento de dados pessoais | I | Exfiltração de base com localização + saúde dos cidadãos | 🟠 |
| **V6** Comprometimento de credenciais / cadeia de suprimentos | S, T | Chave de API exposta ou dependência maliciosa no CI/CD | 🟠 |

### Cobertura STRIDE

| Letra | Ameaça | Coberta por |
|---|---|---|
| **S**poofing | Identidade falsa | V1, V4, V6 |
| **T**ampering | Adulteração | V1, V2, V6 |
| **R**epudiation | Negar uma ação | logs/auditoria (ver pilar 2) |
| **I**nformation Disclosure | Vazamento | V5 |
| **D**enial of Service | Indisponibilidade | V3 |
| **E**levation of Privilege | Escalar privilégio | V4 |

➡️ Cada vetor é tratado em [02 · Arquitetura de Segurança](02-arquitetura-de-seguranca.md) e rastreado na [matriz ameaça → controle](05-red-team-blue-team.md#matriz-ameaça-controle).
