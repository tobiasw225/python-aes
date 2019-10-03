import unittest

import numpy as np
from python_aes.AES256 import encrypt
from python_aes.AES256 import decrypt


from python_aes.keyManager import *
from python_aes.text_encoding import *
from python_aes.helper import get_key






class AsciiTestString(unittest.TestCase):
    """
        Test AES with ascii string.

    """
    def test_something(self):
        key = get_key("/home/tobias/mygits/python-aes/keys/gKey")

        text = "This is a test"
        blocks = string_to_blocks(text)
        expanded_key = expand_key(key)

        enc_blocks = [encrypt(block, expanded_key) for block in blocks]
        dec_blocks = [decrypt(block, expanded_key) for block in enc_blocks]
        self.assertEqual(True, np.allclose(dec_blocks, blocks))



class AsciiTestFile(unittest.TestCase):
    """
        Test AES with ascii file.

    """
    def test_something(self):
        key = get_key("/home/tobias/mygits/python-aes/keys/gKey")

        blocks = text_file_to_blocks(filename="/home/tobias/mygits/python-aes/res/test.txt")

        expanded_key = expand_key(key)

        enc_blocks = [encrypt(block, expanded_key) for block in blocks]
        dec_blocks = [decrypt(block, expanded_key) for block in enc_blocks]

        self.assertEqual(True, np.allclose(dec_blocks, blocks))


class UTF8TestFile(unittest.TestCase):
    """
        Test AES with utf-8 file.

    """
    def test_something(self):
        key = get_key("/home/tobias/mygits/python-aes/keys/gKey")

        blocks = text_to_utf(enc="utf-8", filename="/home/tobias/mygits/python-aes/res/test.txt")
        expanded_key = expand_key(key)

        enc_blocks = [encrypt(block, expanded_key) for block in blocks]
        dec_blocks = [decrypt(block, expanded_key) for block in enc_blocks]

        self.assertEqual(True, np.allclose(dec_blocks, blocks))



if __name__ == '__main__':
    unittest.main()
