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


def string_to_blocks(text: str) -> list:
    """

    :param text:
    :return:
    """
    blocks = [ord(c) for c in text]
    return reshape_blocks(blocks=blocks)


def reshape_blocks(blocks: list) -> list:
    """
        reshape blocks from simple list
        to list of lists.

    :param blocks:
    :return:
    """
    new_blocks = [blocks[i:i+16] for i in range(0, len(blocks), 16)]
    for block in new_blocks:
        if len(block) < 16:
            # if eof is reached the remaining places
            # are filled with pseudo random numbers
            for j in range(16-len(block)):
                #block.append(random.randint(0, 0xFF))
                block.append(32)  # 32 ~ whitespace
        assert len(block) == 16

    return new_blocks


def text_file_to_blocks(filename: str) -> list:
    """

    :param filename:
    :return:
    """
    with open(filename, "r") as fin:
        text = fin.read()
    blocks = [ord(c) for c in text]
    return reshape_blocks(blocks=blocks)


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
                yield ""


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
    encoded_letters = []
    end = 16
    if enc == "utf-16":
        end = 4
    for j in range(end):
        enc_l = bytes(letters[j], encoding=enc)
        for c in enc_l:
            encoded_letters.append(c)
    #assert len(encoded_letters) <= 16
    return encoded_letters[:16]  # das kann gar nicht sein. @todo


def decode_block(block: list, enc: str = 'utf-8'):
    """
        from numbers to letters

    :param block:
    :param enc:
    :return:
    """
    ga = []  # global array
    step = 2
    if enc == "utf-16":
        step = 4

    for i in range(0, 16, step):
        if i == 0:
            t = bytes(block[:step])
        else:
            t = bytes(block[i:i + step])
        try:
            t = t.decode(enc)
            ga.append(t)
        except UnicodeDecodeError:
            print("-")
    return ga


def text_to_utf(filename: str, enc: str = 'utf-8')-> list:
    """

    :param filename:
    :param enc:
    :return:
    """
    block_field = []
    end = 16
    if enc == "utf-16":
        end = 4

    with open(filename, "r", encoding=enc) as fobj:
        while True:
            letters = fobj.read(end)
            if len(letters) < end:
                break
            encoded_block = encode_block(letters, enc)

            if len(encoded_block) == 12 and enc == "utf-16":
                for j in range(11, 16):
                    encoded_block.append(0)

            if len(encoded_block) < 16 and enc == "utf-8":
                for j in range(len(encoded_block), 16):
                    encoded_block.append(0)

            assert len(encoded_block) == 16

            block_field.append(encoded_block)

        return block_field


def utf_to_text(blocks: list, enc: str):
    """

    :param blocks:
    :param enc:
    :return:
    """
    for block in blocks:
        db = decode_block(block, enc)
        for c in db:
            yield c



def get_blocks_of_file(filename):
    """

    :param filename:
    :return:
    """
    with open(filename, "rb") as f:
        nbf = []
        eof = False
        byte = f.read(16)  # first 16. signs
        nbf.append(byte)
        while byte and not eof:
            byte = f.read(16)
            lenthofbyte = len(byte)
            if lenthofbyte < 16:
                for i in range(lenthofbyte, 16):
                    byte += b'0'  # verbesserungswuerdig
                eof = True  # when you have to fill up, it means you've reached eof
            nbf.append(byte)
    return nbf


