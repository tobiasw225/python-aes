import os
import filecmp
import unittest
from python_aes.aes_interface import AESString
from python_aes.aes_interface import AESBytes


class AESStringTest(unittest.TestCase):
    def test_if_dec_equal_original(self):
        test_string = "Ich bin ein kleiner Test String."
        my_aes = AESString()

        enc = my_aes.encrypt(test_string)
        dec_string = my_aes.decrypt(enc)
        self.assertEqual(test_string, dec_string)


class AESByteTest(unittest.TestCase):
    def test_if_dec_equal_original(self):
        my_aes = AESBytes()
        folder = "/home/tobias/mygits/python-aes/res/"
        original_file = os.path.join(folder, 'test.jpg')
        dec_file = os.path.join(folder, 'test.dec.jpg')
        enc_file = os.path.join(folder, 'test.enc.jpg')

        my_aes.encrypt(filename=original_file,
                       output_file=enc_file)
        my_aes.decrypt(filename=enc_file,
                       output_file=dec_file)
        self.assertTrue(filecmp.cmp(original_file, dec_file))


if __name__ == '__main__':
    unittest.main()
