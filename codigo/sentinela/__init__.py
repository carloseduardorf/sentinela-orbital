"""Sentinela Orbital — PoC dos controles de segurança.

Prova de conceito (sem dependências externas, apenas a biblioteca padrão do
Python) que implementa, de forma funcional, os controles de segurança
desenhados na análise da GS. Cada módulo mitiga um ou mais vetores do
modelo de ameaças:

- ``telemetria``  : integridade/autenticidade dos dados de sensores  (V1, V2)
- ``acesso``      : autenticação, RBAC e regra das duas pessoas        (V4)
- ``senhas``      : hashing forte de credenciais (scrypt)
- ``limite``      : rate limiting / anti-DDoS (token bucket)           (V3)
- ``privacidade`` : pseudonimização e minimização de dados (LGPD)      (V5)
"""

__all__ = ["telemetria", "acesso", "senhas", "limite", "privacidade"]
__version__ = "1.0.0"
