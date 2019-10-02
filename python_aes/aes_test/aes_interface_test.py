import unittest
from python_aes.aes_interface import AESInterface


class AESInterfaceTest(unittest.TestCase):
    def test_something(self):
        test_string = "Ich bin ein kleiner Test String."
        my_aes = AESInterface()

        enc = my_aes.encrypt_string(test_string)
        dec_string = my_aes.decrypt_string(enc)

        self.assertEqual(test_string, dec_string)


if __name__ == '__main__':
    unittest.main()
