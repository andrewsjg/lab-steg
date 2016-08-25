from PIL import Image
from functools import partial


def read_binary_into_string(file_path):

    # Read a binary file into a string of 1's and 0's

    # This is a bit of fun so we can literally see the 1's and 0's by printing them
    # to the screen if we want to

    # To do this more 'practically' you might use a byte array instead,

    bit_count = 0

    # Open the binary file for reading (rb mode) and read it byte by byte

    with open(file_path, 'rb') as input_file:
        bin_string = ''


        for byte in iter(partial(input_file.read, 1), ''):
            if len(byte) > 0:

                # found on stackoverflow here: http://stackoverflow.com/questions/2872381/how-to-read-a-file-byte-by-byte-in-python-and-how-to-print-a-bytelist-as-a-binar
                bin_string += '{0:08b}'.format(ord(byte)) + '\n'
                bit_count += 8

    return bin_string, bit_count


def write_binary_from_string(big_binary_string, out_file):

    # Write out a string of 1's and 0's to a binary file

    # If we use wth wb mode for writing, python will write the data out to disk as raw bytes.

    # If we were to use a text mode to write this data to disk (no b option)
    # python may alter the raw bytes to encode it as text. Meaning
    # the file may contain extra data to tell the operating system and other programs how to handled the file as text.
    # We don't want any extra data in our file as it will mess up the encoding of the binary file.

    bin_output = open(out_file, 'wb')

    # Since python uses strings to encode binary data, we can simply iterate over our binary string
    # line by line then convert the binary string to an integer, which python will happily do for us
    # if we tell it we'd like the integer represented by that string (int(<string>)). Once we have the
    # integer value, we can ask python again to convert that to a character (chr(<int>)) which will give us
    # a binary character that we can then write to our file.

    for byte_string in big_binary_string.splitlines():
        bin_output.write(chr(int(byte_string,2)))

def max_hidable(input_image):

    img = input_image
    (width, height) = img.size

    # Maximum hideable size 9 in KB) if we use the 3 least significant bits
    max_hideable = width * height * 3.0 / 8 / 1024

    # return the width and hieght as a tuple and the max_hideable size as KB
    return (width, height), max_hideable


def size_required_to_hide(input_size_bits):

    return 3 * 8 * input_size_bits


def hide_file(binary_string, host_image):
    pass

def bits_from_bytes(byte_size):

    return byte_size * 1024 * 8

if __name__ == "__main__":

    bin_string, bit_count = read_binary_into_string('shakespeare.zip')
    input_image = Image.open('input.jpg')

    ((width,hieght), max_hideable_size) = max_hidable(input_image)


    if (bit_count / 8 / 1024) < max_hideable_size:
        print 'Can hide payload file in host image'

    else:
        print 'Host image is to small to contain the payload file'




    #print "Max Hideable: " + str(float(max_hidable(bit_count)) / 8 / 1024 / 1024)

    #print bits_from_bytes(5 * 1024)
    #print size_required_to_hide(bits_from_bytes(5 * 1024)) / 1024

    #write_binary(bin_string, 'out.png')