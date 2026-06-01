"""Testes de controle de acesso, RBAC e regra das duas pessoas (V4)."""

import unittest

from sentinela import acesso


class TestAcesso(unittest.TestCase):
    def setUp(self):
        self.chave = b"chave-de-assinatura-de-tokens-0123456"

    def test_token_valido(self):
        tok = acesso.emitir_token("op:ana", "operador", self.chave, ttl_s=900, agora=0)
        payload = acesso.validar_token(tok, self.chave, agora=10)
        self.assertEqual(payload["sub"], "op:ana")
        self.assertEqual(payload["papel"], "operador")

    def test_token_forjado_rejeitado(self):
        tok = acesso.emitir_token("op:ana", "operador", self.chave, agora=0)
        with self.assertRaises(acesso.TokenInvalido):
            acesso.validar_token(tok[:-3] + "xxx", self.chave, agora=10)

    def test_token_expirado_rejeitado(self):
        tok = acesso.emitir_token("op:ana", "operador", self.chave, ttl_s=60, agora=0)
        with self.assertRaises(acesso.TokenInvalido):
            acesso.validar_token(tok, self.chave, agora=120)

    def test_rbac_permissoes(self):
        self.assertTrue(acesso.tem_permissao("operador", "monitorar"))
        self.assertFalse(acesso.tem_permissao("cidadao", "monitorar"))
        self.assertFalse(acesso.tem_permissao("operador", "gerir_acessos"))

    def test_autorizar_nega_sem_permissao(self):
        tok = acesso.emitir_token("cidadao:maria", "cidadao", self.chave, agora=0)
        with self.assertRaises(acesso.AcessoNegado):
            acesso.autorizar(tok, "monitorar", self.chave, agora=10)

    def test_duas_pessoas_bloqueia_um_aprovador(self):
        tok = acesso.emitir_token("op:ana", "operador", self.chave, agora=0)
        with self.assertRaises(acesso.AcessoNegado):
            acesso.disparar_alerta_massa([tok], self.chave, agora=10)

    def test_duas_pessoas_bloqueia_mesmo_aprovador_repetido(self):
        tok = acesso.emitir_token("op:ana", "operador", self.chave, agora=0)
        with self.assertRaises(acesso.AcessoNegado):
            acesso.disparar_alerta_massa([tok, tok], self.chave, agora=10)

    def test_duas_pessoas_permite_dois_distintos(self):
        t1 = acesso.emitir_token("op:ana", "operador", self.chave, agora=0)
        t2 = acesso.emitir_token("op:bruno", "operador", self.chave, agora=0)
        res = acesso.disparar_alerta_massa([t1, t2], self.chave, agora=10)
        self.assertEqual(res["status"], "alerta_disparado")
        self.assertEqual(res["aprovadores"], ["op:ana", "op:bruno"])

    def test_duas_pessoas_nega_papel_sem_permissao(self):
        t1 = acesso.emitir_token("op:ana", "operador", self.chave, agora=0)
        t2 = acesso.emitir_token("cidadao:maria", "cidadao", self.chave, agora=0)
        with self.assertRaises(acesso.AcessoNegado):
            acesso.disparar_alerta_massa([t1, t2], self.chave, agora=10)


if __name__ == "__main__":
    unittest.main()
