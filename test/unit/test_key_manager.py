import random


def test_shift_left():
    n = random.randint(1, 100)
    my_list = [random.randint(1, 100) for _ in range(n)]
    my_list_before = my_list.copy()
    for i in range(n):
        my_list.append(my_list.pop(0))
    assert my_list_before == my_list


# def test_key_schedule_core():
#     pass

# def test_expand_key():
#     pass