import unittest

def detectar_franquicia(numero):
    numero = numero.replace(' ', '').replace('-', '')
    if len(numero) == 16:
        if numero[0] == '4':
            return 'VISA'
        if 51 <= int(numero[:2]) <= 55:
            return 'MASTERCARD'
    if len(numero) == 15:
        if numero[:2] in ['34', '37']:
            return 'AMEX'
    return 'DESCONOCIDA'

class TestFranquicia(unittest.TestCase):
    def test_visa(self):
        self.assertEqual(detectar_franquicia('4111111111111111'), 'VISA')

    def test_mastercard(self):
        self.assertEqual(detectar_franquicia('5411111111111111'), 'MASTERCARD')

    def test_amex_34(self):
        self.assertEqual(detectar_franquicia('341111111111111'), 'AMEX')

    def test_amex_37(self):
        self.assertEqual(detectar_franquicia('371111111111111'), 'AMEX')

    def test_desconocida(self):
        self.assertEqual(detectar_franquicia('1234567890123456'), 'DESCONOCIDA')

if __name__ == '__main__':
    unittest.main(verbosity=2)
