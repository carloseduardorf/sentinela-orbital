"""Testes de hashing de senha."""

import unittest

from sentinela import senhas

# Parâmetros leves para os testes rodarem rápido (custo real fica no padrão de produção).
_KW = {"n": 2 ** 12, "r": 8, "p": 1}


class TestSenhas(unittest.TestCase):
    def test_verifica_senha_correta(self):
        h = senhas.hash_senha("Sup3rS3nh4!", **_KW)
        self.assertTrue(senhas.verificar_senha("Sup3rS3nh4!", h))

    def test_rejeita_senha_errada(self):
        h = senhas.hash_senha("Sup3rS3nh4!", **_KW)
        self.assertFalse(senhas.verificar_senha("senha-errada", h))

    def test_nunca_armazena_texto_puro(self):
        h = senhas.hash_senha("minha-senha", **_KW)
        self.assertNotIn("minha-senha", h)
        self.assertTrue(h.startswith("scrypt$"))

    def test_salt_torna_hashes_diferentes(self):
        h1 = senhas.hash_senha("igual", **_KW)
        h2 = senhas.hash_senha("igual", **_KW)
        self.assertNotEqual(h1, h2)  # salts diferentes
        self.assertTrue(senhas.verificar_senha("igual", h1))
        self.assertTrue(senhas.verificar_senha("igual", h2))

    def test_armazenado_invalido_retorna_false(self):
        self.assertFalse(senhas.verificar_senha("x", "lixo-sem-formato"))
        self.assertFalse(senhas.verificar_senha("x", ""))


if __name__ == "__main__":
    unittest.main()
