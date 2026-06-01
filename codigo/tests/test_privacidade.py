"""Testes de privacidade / minimização de dados (V5, LGPD)."""

import unittest

from sentinela import privacidade


class TestPrivacidade(unittest.TestCase):
    def setUp(self):
        self.chave = b"pepper-de-pseudonimizacao-0123456789"

    def test_pseudonimo_estavel(self):
        a = privacidade.pseudonimizar("cpf:123", self.chave)
        b = privacidade.pseudonimizar("cpf:123", self.chave)
        self.assertEqual(a, b)  # determinístico

    def test_pseudonimo_difere_por_identificador(self):
        a = privacidade.pseudonimizar("cpf:123", self.chave)
        b = privacidade.pseudonimizar("cpf:999", self.chave)
        self.assertNotEqual(a, b)

    def test_pseudonimo_nao_revela_original(self):
        p = privacidade.pseudonimizar("cpf:123.456.789-00", self.chave)
        self.assertNotIn("123", p)
        self.assertEqual(len(p), 16)

    def test_pseudonimo_muda_com_a_chave(self):
        a = privacidade.pseudonimizar("cpf:123", self.chave)
        b = privacidade.pseudonimizar("cpf:123", b"outra-chave-pepper-987654321")
        self.assertNotEqual(a, b)

    def test_coarsen_local_reduz_precisao(self):
        self.assertEqual(privacidade.coarsen_local(-23.5612, -46.6566, casas=1), (-23.6, -46.7))

    def test_mascarar_contato(self):
        self.assertEqual(privacidade.mascarar_contato("maria@email.com"), "m****@email.com")
        self.assertEqual(privacidade.mascarar_contato("invalido"), "***")


if __name__ == "__main__":
    unittest.main()
