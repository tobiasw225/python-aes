from itertools import chain
from typing import List, Sequence, Iterable

from python_aes.tables import m2, m3, m14, m11, m13, m9
from python_aes.text_to_number_conversion import chunks


def mix_invert(block: Iterable[int], n: int) -> List[int]:
    """
    >>> _block = [  0,  17,  34,  51,  68,  85, 102, 119, 136, 153, 170, 187, 204, 221, 238, 255]
    >>> mix_invert(mix(_block), n=4) == block
    True
    """
    return list(
        chain.from_iterable(_mix_column_inv(row) for row in chunks(list(block), n=n))
    )


def mix(block: Sequence[int], n: int) -> List[int]:
    """
    >>> block = [  0,  17,  34,  51,  68,  85, 102, 119, 136, 153, 170, 187, 204, 221, 238, 255]
    >>> mix(block, n=4)
    [34, 119, 0, 85, 102, 51, 68, 17, 170, 255, 136, 221, 238, 187, 204, 153]
    """
    return list(chain.from_iterable(_mix_column(row) for row in chunks(block, n=n)))


def _mix_column(col: Sequence[int]) -> Sequence[int]:
    return [
        m2[col[0]] ^ m3[col[1]] ^ col[2] ^ col[3],
        col[0] ^ m2[col[1]] ^ m3[col[2]] ^ col[3],
        col[0] ^ col[1] ^ m2[col[2]] ^ m3[col[3]],
        m3[col[0]] ^ col[1] ^ col[2] ^ m2[col[3]],
    ]


def _mix_column_inv(col: Sequence[int]) -> Sequence[int]:
    return [
        m14[col[0]] ^ m11[col[1]] ^ m13[col[2]] ^ m9[col[3]],
        m9[col[0]] ^ m14[col[1]] ^ m11[col[2]] ^ m13[col[3]],
        m13[col[0]] ^ m9[col[1]] ^ m14[col[2]] ^ m11[col[3]],
        m11[col[0]] ^ m13[col[1]] ^ m9[col[2]] ^ m14[col[3]],
    ]