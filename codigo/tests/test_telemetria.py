"""Testes de integridade da telemetria (V1/V2)."""

import unittest

from sentinela import telemetria


class TestTelemetria(unittest.TestCase):
    def setUp(self):
        self.chave = b"chave-secreta-do-sensor-0123456789"
        self.leitura = telemetria.assinar(
            {"sensor": "S1", "temp_c": 41.2, "regiao": "SP"}, self.chave, agora=1000
        )

    def test_assinatura_valida(self):
        self.assertTrue(telemetria.verificar(self.leitura, self.chave, agora=1000))

    def test_adulteracao_rejeitada(self):
        adulterada = dict(self.leitura)
        adulterada["temp_c"] = 22.0
        with self.assertRaises(telemetria.TelemetriaInvalida):
            telemetria.verificar(adulterada, self.chave, agora=1000)

    def test_chave_errada_rejeitada(self):
        with self.assertRaises(telemetria.TelemetriaInvalida):
            telemetria.verificar(self.leitura, b"chave-errada", agora=1000)

    def test_sem_assinatura_rejeitada(self):
        with self.assertRaises(telemetria.TelemetriaInvalida):
            telemetria.verificar({"sensor": "S1", "temp_c": 41.2}, self.chave, agora=1000)

    def test_replay_fora_da_janela_rejeitado(self):
        # leitura assinada em t=1000, verificada muito depois (> janela de 300s)
        with self.assertRaises(telemetria.TelemetriaInvalida):
            telemetria.verificar(self.leitura, self.chave, agora=5000, janela_s=300)

    def test_dentro_da_janela_aceito(self):
        self.assertTrue(telemetria.verificar(self.leitura, self.chave, agora=1200, janela_s=300))


if __name__ == "__main__":
    unittest.main()
