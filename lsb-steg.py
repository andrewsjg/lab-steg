from functools import partial

def get_binary(file_path):

    bit_count = 0

    with open(file_path, 'rb') as input_file:
        bin_string = ''

        for byte in iter(partial(input_file.read, 1), ''):
            if len(byte) > 0:
                bin_string += '{0:08b}'.format(ord(byte)) + '\n'
                bit_count += 8

    return bin_string, bit_count


def write_binary(big_binary_string, out_file):

    bin_output = open(out_file, 'wb')

    for byte_string in big_binary_string.splitlines():
        bin_output.write(chr(int(byte_string,2)))

def max_hidable(available_bits):

    return (available_bits / 8 * 2)


def size_required_to_hide(input_bit_size):

    return 2 * 8 * input_bit_size


def bits_from_bytes(byte_size):

    return byte_size * 1024 * 8

if __name__ == "__main__":

    bin_string, bit_count = get_binary('/Users/james/Documents/Work/UM Docs/UMQ_5.3/doc/UME/UMP_Store_Architecture.png')

    print bits_from_bytes(5 * 1024)
    print size_required_to_hide(bits_from_bytes(5 * 1024)) / 1024
    write_binary(bin_string, 'out.png')