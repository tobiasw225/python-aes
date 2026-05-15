from python_aes.aes256 import AESBase

KNOWN_BLOCK = [
    0,
    17,
    34,
    51,
    68,
    85,
    102,
    119,
    136,
    153,
    170,
    187,
    204,
    221,
    238,
    255,
]
KEY = "00" * 32


def test_encrypt_decrypt_roundtrip():
    crypter = AESBase(KEY)
    enc = crypter.encrypt_block(KNOWN_BLOCK)
    dec = crypter.decrypt_block(enc)
    assert dec == KNOWN_BLOCK


def test_decrypt_encrypt_roundtrip():
    aes = AESBase(KEY)
    dec = aes.decrypt_block(KNOWN_BLOCK)
    enc = aes.encrypt_block(dec)
    assert enc == KNOWN_BLOCK
