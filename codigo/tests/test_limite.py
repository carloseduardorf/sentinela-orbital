"""Testes de rate limiting / anti-DDoS (V3)."""

import unittest

from sentinela import limite


class TestLimite(unittest.TestCase):
    def test_rajada_barra_excedente(self):
        balde = limite.TokenBucket(capacidade=3, taxa_por_s=1)
        resultados = [balde.permitir(agora=0) for _ in range(5)]
        self.assertEqual(resultados, [True, True, True, False, False])

    def test_reabastece_com_o_tempo(self):
        balde = limite.TokenBucket(capacidade=1, taxa_por_s=1)
        self.assertTrue(balde.permitir(agora=0))    # gasta a única ficha
        self.assertFalse(balde.permitir(agora=0))   # sem ficha no mesmo instante
        self.assertTrue(balde.permitir(agora=1))    # 1s depois reabasteceu 1 ficha

    def test_limitador_por_chave_isola_clientes(self):
        lim = limite.LimitadorPorChave(capacidade=1, taxa_por_s=0)
        self.assertTrue(lim.permitir("ip-A", agora=0))
        self.assertFalse(lim.permitir("ip-A", agora=0))  # A estourou
        self.assertTrue(lim.permitir("ip-B", agora=0))   # B é independente


if __name__ == "__main__":
    unittest.main()
