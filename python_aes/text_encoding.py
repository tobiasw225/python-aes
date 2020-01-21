#!/usr/bin/env python3
# -*- coding: iso-8859-15 -*-
#
# __filename__: text_encoding.py
#
# __description__: Functions to convert the given Text to numbers
#         and following that converting them to block of the
#         size of 16 numbers (numbersToFields)
#
#         Decoding Function which can be used to derive a text out of a given
#         (decoded) block.
#
# __remark__:
#
# __todos__:
#
# Created by Tobias Wenzel in December 2015
# Copyright (c) 2015 Tobias Wenzel

"""

"""

import numpy as np


def string_to_blocks(text: str) -> np.ndarray:
    """

    :param text:
    :return:
    """
    return reshape_blocks(blocks=[ord(c) for c in text])


def text_blocks(text: str, block_size: int):
    """

    :param text:
    :return:
    """
    my_chars = [c for c in text]
    i = 0
    while i < len(my_chars):
        yield "".join(my_chars[i:i+block_size])
        i += block_size


def reshape_blocks(blocks: list) -> np.ndarray:
    """
        reshape blocks from simple list
        to list of lists and add a default-value
        (whitespace)

    :param blocks:
    :return:
    """
    # add missing spaces.
    future_len = len(blocks) + 16-(len(blocks) % 16)
    n_rows = future_len // 16
    # 32 ~ whitespace
    new_blocks = np.full(future_len, dtype=int, fill_value=32)
    new_blocks[:len(blocks)] = blocks
    new_blocks = new_blocks.reshape((n_rows, 16))
    return new_blocks


def text_file_to_blocks(filename: str) -> np.ndarray:
    """

    :param filename:
    :return:
    """
    with open(filename, "r") as fin:
        text = fin.read()
    return reshape_blocks(blocks=[ord(c) for c in text])


def chr_decode(c) -> str:
    try:
        return chr(c)
    except:
        return ''


def decode_blocks_to_string(blocks: list):
    """

    :param blocks:
    :return:
    """
    for block in blocks:
        for i in range(16):
            try:
                yield chr(block[i])
            except:
                yield " "


def write_decoded_text(blocks: list, filename: str):
    """

    :param blocks:
    :param filename:
    :return:
    """
    with open(filename, "w") as fout:
        for block in decode_blocks_to_string(blocks):
            fout.write(block)


"""
    utf

"""


def encode_block(letters: str, enc: str = 'utf-8') -> list:
    """
        from letters to numbers
        -> 4 letters utf-16
        ->  8 for utf-8

    :param letters:
    :param enc:
    :return:
    """
    enc_letters = []
    end = 16
    if enc == "utf-16":
        end = 4

    for j in range(end):
        enc_l = bytes(letters[j], encoding=enc)
        enc_letters.extend(enc_l)
    # fill up rest with zeros.
    enc_letters.extend([0] * (16 - len(enc_letters)))

    #assert len(encoded_letters) <= 16
    return enc_letters[:16]  # das kann gar nicht sein. @todo


def decode_block(block: list, enc: str = 'utf-8'):
    """
        from numbers to letters

    :param block:
    :param enc:
    :return:
    """
    step = 2
    if enc == "utf-16":
        step = 4

    b_block = [bytes(block[i:i + step]) for i in range(0, 16, step)]
    signs = []
    for sign in b_block:
        # For some reason, I get extra \x00 signs,
        # when I call bytes() in this script. This
        # does not happen when called on the console.
        sign = sign.replace(b'\x00', b'')
        try:
            sign = sign.decode(enc)
        except UnicodeDecodeError:
            sign = ""
        signs.append(sign)

    return "".join(signs)


def text_to_utf(filename: str, enc: str = 'utf-8')-> list:
    """

    :param filename:
    :param enc:
    :return:
    """
    blocks = []
    end = 16
    if enc == "utf-16":
        end = 4

    with open(filename, "r", encoding=enc) as fin:
        while True:
            letters = fin.read(end)
            if len(letters) < end:
                break
            encoded_block = encode_block(letters, enc)

            assert len(encoded_block) == 16

            blocks.append(encoded_block)

        return blocks


def utf_to_text(blocks: list, enc: str):
    """

    :param blocks:
    :param enc:
    :return:
    """
    for block in blocks:
        yield decode_block(block, enc)
