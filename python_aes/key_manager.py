from python_aes.tables import rcon, sbox
from python_aes.text_to_number_conversion import xor_blocks

EXTENDED_KEY_SIZE = 240
WORD_LEN = 4


def key_schedule_core(word: list[int], iteration: int) -> list[int]:
    word.append(word.pop(0))
    word = apply_sbox(word)
    word[0] ^= rcon[iteration]
    return word


def apply_sbox(word: list[int]) -> list[int]:
    return [sbox[i] for i in word]


def expand_key(key: list[int]) -> list[int]:
    original_key_len = len(key)
    i = original_key_len
    expanded_key = [0] * EXTENDED_KEY_SIZE
    expanded_key[: len(key)] = key

    while i < EXTENDED_KEY_SIZE:
        word = expanded_key[i - WORD_LEN : i]
        if i % original_key_len == 0:
            iteration = (i % original_key_len) - 1
            word = key_schedule_core(word, iteration)
        if i % original_key_len == WORD_LEN:
            word = apply_sbox(word)
        start_of_word = i - original_key_len
        key_row = expanded_key[start_of_word : start_of_word + WORD_LEN]
        expanded_key[i : i + WORD_LEN] = xor_blocks(key_row, word)
        i += WORD_LEN
    return expanded_key
