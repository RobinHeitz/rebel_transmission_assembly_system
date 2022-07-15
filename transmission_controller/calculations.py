GEAR_SCALE = 1031.11
GEAR_OFFSET = 0


def int_to_bytes(number, num_bytes=4, signed=True):
    bytes_ = int(number).to_bytes(num_bytes, "big", signed=signed)
    return list(bytes_)


def bytes_to_int(bytes_array, signed=True):
    return int.from_bytes(bytes_array,"big", signed=signed)



if __name__ == "__main__":

    my_number = -12345
    bytes_ = list(int_to_bytes(my_number, 4, True))
    number_again = bytes_to_int(bytes_,True)
    print(my_number == number_again)