from python_aes.tables import rcon, sbox
from python_aes.text_to_number_conversion import xor_blocks

EXTENDED_KEY_SIZE = 240
WORD_LEN = 4


def key_schedule_core(word: list[int], iteration: int) -> list[int]:
    """

    :param word:
    :param iteration:
    :return:
    """
    # inserting the values to the new places
    # (shift left)
    word.append(word.pop(0))
    # apply sbox
    word = apply_sbox(word)
    # perform the rcon operation with i as the input,
    # and exclusive or the rcon output with the first byte of the output word
    word[0] ^= rcon[iteration]
    return word


def apply_sbox(word: list[int]) -> list[int]:
    return [sbox[i] for i in word]


def expand_key(key: list[int]) -> list[int]:
    """
    >>> key = [ 0,  1,  2,  3,  4,  5,  6,  7,  8,  9, 10, \
    11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26,\
     27, 28, 29, 30, 31]
    >>> res = expand_key(key)
    >>> res[:32] == key
    True

    :param key:
    :return:
    """
    original_key_len = len(key)
    i = original_key_len
    expanded_key = [0] * EXTENDED_KEY_SIZE
    # initialize extended key with key-elements.
    expanded_key[: len(key)] = key

    while i < EXTENDED_KEY_SIZE:
        # Copy the temporary variable.
        word = expanded_key[i - WORD_LEN : i]
        if i % original_key_len == 0:
            # Every eight sets, do a complex calculation.
            # this is like c + 1
            iteration = (i % original_key_len) - 1
            word = key_schedule_core(word, iteration)
        if i % original_key_len == WORD_LEN:
            # For 256-bit keys, we add an extra sbox to the calculation.
            word = apply_sbox(word)
        start_of_word = i - original_key_len
        key_row = expanded_key[start_of_word : start_of_word + WORD_LEN]
        expanded_key[i : i + WORD_LEN] = xor_blocks(key_row, word)
        i += WORD_LEN
    return expanded_key
