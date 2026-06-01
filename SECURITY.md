# Política de Segurança — Sentinela Orbital

A Sentinela Orbital é uma plataforma de **alerta de emergência**. Tratamos segurança como requisito de **segurança pública** e de **proteção de dados pessoais** (LGPD), não como detalhe. Este documento define como relatar problemas e quais princípios seguimos.

## 🎯 Nossa filosofia

> Pense como atacante para encontrar as fraquezas; pense como defensor para blindá-las.

Adotamos **Zero Trust** ("nunca confie, sempre verifique"), **defesa em profundidade** e comportamento **fail-safe**: na dúvida, o sistema erra para o lado seguro — **não silencia** um alerta real e **não dispara** um falso.

## 📦 Versões suportadas

| Versão | Suporte de segurança |
|---|:--:|
| 1.x (atual) | ✅ |
| < 1.0 (protótipo) | ❌ |

## 🚨 Como relatar uma vulnerabilidade

**Não abra uma _issue_ pública** para falhas de segurança. Praticamos *responsible disclosure*:

1. Envie um e-mail para **security@sentinela-orbital.example** (ajuste para o canal real da equipe) com:
   - descrição da falha e do impacto;
   - passos para reproduzir (PoC, se houver);
   - componente afetado (ingestão, motor de alertas, API, app…).
2. Se possível, criptografe o conteúdo sensível.

### Prazos (SLA) que buscamos

| Etapa | Prazo-alvo |
|---|---|
| Confirmação de recebimento | 48 horas |
| Avaliação inicial de severidade | 5 dias úteis |
| Correção de severidade crítica | o mais rápido possível, com mitigação imediata |
| Retorno ao pesquisador | a cada etapa relevante |

Pedimos um prazo razoável para correção **antes** de qualquer divulgação pública.

## 🔭 Escopo

**Dentro do escopo:** APIs (pública, parceiros, admin), motor de alertas, pipeline de ingestão, app/web do cidadão, infraestrutura de nuvem do projeto.

**Fora do escopo:** sistemas de terceiros (provedores de satélite, operadoras), ataques de engenharia social a pessoas, testes que degradem o serviço de alerta em produção (DoS).

## 🛡️ Princípios de segurança aplicados

- **Controle de acesso:** MFA forte para operadores, RBAC com privilégio mínimo e **dupla aprovação** para alertas em massa.
- **Proteção de dados:** TLS 1.3 / mTLS em trânsito, AES-256 em repouso, criptografia de campo para dados sensíveis, segredos em cofre.
- **Integridade:** telemetria assinada (HMAC); a ingestão rejeita dados não verificados.
- **Infraestrutura:** WAF + anti-DDoS, microssegmentação, logs centralizados + SIEM, CI/CD com SAST/DAST/SCA.
- **Resposta a incidentes:** ciclo NIST 800-61 (ver [docs/seguranca/04-plano-de-resposta-a-incidentes.md](docs/seguranca/04-plano-de-resposta-a-incidentes.md)).
- **Privacidade:** conformidade com a **LGPD**; vazamento de dados pessoais dispara notificação à **ANPD** e aos titulares.

A análise técnica completa está em [`docs/seguranca/`](docs/seguranca/).

## 🙏 Reconhecimentos

Pesquisadores que relatarem falhas de forma responsável serão creditados aqui (com consentimento).
