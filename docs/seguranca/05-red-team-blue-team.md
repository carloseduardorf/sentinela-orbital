# 05 · Red Team 🔴 vs Blue Team 🔵

> Pensar como **atacante** para achar as fraquezas; pensar como **defensor** para blindá-las. Esta é a coerência que liga o pilar 1 aos pilares 2–4.

## 🔴 Red Team — atacando a Sentinela

### Ataque A — "Apagar o alerta no calor mortal" (V1)
MITM no link de um sensor ou sensor falso reportando temperatura baixa → o modelo "vê" a região segura → **alerta não dispara**. Impacto: 🔴 risco à vida, silencioso.

### Ataque B — "Envenenar a inteligência" (V2)
Dados falsos sutis e persistentes na ingestão → o modelo aprende uma "normalidade" errada. Impacto: 🔴 subnotificação crônica ou fadiga de alerta.

### Ataque C — "Derrubar no pico" (V3)
Botnet aguarda uma onda de calor real e faz DDoS na API/dashboard. Impacto: 🔴 o alerta existe mas não chega.

### Ataque D — "Virar o megafone contra a cidade" (V4)
Phishing de um operador → disparo de alerta falso em massa (pânico) ou silenciar um real. Impacto: 🔴 caos + erosão de confiança.

### Ataque E — "Roubar os vulneráveis" (V5/V6)
Explorar API mal protegida ou credencial vazada → baixar base com localização + saúde. Impacto: 🟠 dano às pessoas + sanção LGPD.

## 🔵 Blue Team — blindando a Sentinela

| Ataque (Red) | Defesa (Blue) | Pilar |
|---|---|---|
| A — Apagar o alerta (V1) | mTLS + **HMAC/assinatura**; ingestão rejeita dado não assinado; detecção de anomalia | 2.2 / 2.3 |
| B — Envenenar IA (V2) | Validação estatística; detecção de outlier; reconciliação satélite × sensor; retreino auditável | 2.3 |
| C — Derrubar no pico (V3) | WAF + rate limit + CDN/anycast; autoescala; **canais redundantes** | 2.3 |
| D — Sequestrar o megafone (V4) | **MFA forte** + **dupla aprovação**; microssegmentação; *kill-switch* | 2.1 / 4 |
| E — Roubar vulneráveis (V5/V6) | Criptografia em repouso + campo; minimização; cofre de segredos; scan no CI/CD | 2.2 / 3.2 |

Princípios que sustentam: **Zero Trust**, **defesa em profundidade**, **fail-safe**, **detecção + resposta**.

---

## Matriz Ameaça-Controle

A peça que prova a **coerência**: toda ameaça tem controle preventivo **e** plano de resposta.

| Vetor | STRIDE | Ativo | Controle de mitigação | Resposta se ocorrer |
|---|---|---|---|---|
| **V1** Interceptação/spoofing | S, T | Links de ingestão | mTLS + HMAC; detecção de anomalia | Isolar fonte; descartar dado |
| **V2** Data poisoning | T | Modelo de IA | Validação de outliers; reconciliação; retreino auditável | Reverter modelo; quarentena |
| **V3** DDoS no pico | D | API de alertas | WAF, rate limit, CDN, autoescala, redundância | Mitigação DDoS; failover |
| **V4** Sequestro do motor | E, S | Motor de alertas | MFA forte + dupla aprovação; microssegmentação; kill-switch | Cenário Sev-1 do PRI |
| **V5** Vazamento de PII | I | PII sensível | AES-256 + cripto de campo; minimização; RBAC | Notificar ANPD/titulares |
| **V6** Credenciais/supply chain | S, T | Segredos, CI/CD | Cofre; scan de segredos/SCA; SBOM + assinatura | Rotacionar chaves; auditar pipeline |
| **(R)** Repúdio | R | Logs | Trilhas WORM imutáveis | Forense sobre logs íntegros |

> ✅ **100% dos vetores** identificados têm controle preventivo **e** plano de resposta. O risco residual é monitorado pelo SGSI (ISO 27001) no ciclo PDCA.
