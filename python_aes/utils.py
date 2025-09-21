async def async_enumerate(my_list):
    index = 0
    async for value in my_list:
        yield index, value
        index += 1
