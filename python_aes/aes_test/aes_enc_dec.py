import unittest

from readBlockFile import get_block
from python_aes.helper import get_key

from python_aes.AES256 import encrypt
from python_aes.AES256 import decrypt


class AESTest(unittest.TestCase):
    """
        Test with simple predefined block.

    """
    def test_something(self):

        key = get_key("/home/tobias/mygits/python-aes/res/testKey")
        test_block = get_block("/home/tobias/mygits/python-aes/res/testBlock")
        enc_block = encrypt(test_block, key)
        dec_block = decrypt(enc_block, key)
        self.assertEqual(dec_block, test_block)


if __name__ == '__main__':
    unittest.main()
