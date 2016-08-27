from PIL import Image
from functools import partial

# References:
# https://github.com/cyberinc/cloacked-pixel

def read_binary_into_string_array(file_path):

    # Read a binary file into a string of 1's and 0's

    # This is a bit of fun so we can literally see the 1's and 0's by printing them
    # to the screen if we want to

    # To do this more 'practically' you might use a byte array instead,

    bit_count = 0
    bin_string_array = []

    # Open the binary file for reading (rb mode) and read it byte by byte

    with open(file_path, 'rb') as input_file:
        bin_string = ''

        # TODO: Document partial
        for byte in iter(partial(input_file.read, 1), ''):
            if len(byte) > 0:

                # found on stackoverflow here: http://stackoverflow.com/questions/2872381/how-to-read-a-file-byte-by-byte-in-python-and-how-to-print-a-bytelist-as-a-binar
                #bin_string += '{0:08b}'.format(ord(byte)) + '\n'
                bin_string_array.append('{0:08b}'.format(ord(byte)))

                bit_count += 8

    return bin_string_array, bit_count


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
    return width, height, max_hideable


def size_required_to_hide(input_size_bits):

    return 3 * 8 * input_size_bits


def bits_from_bytes(byte_size):

    return byte_size * 1024 * 8


def lsb_encode_byte(bits_to_hide, target_byte,debug=False):

    # TODO: Show how to use a bit mask here?

    if debug:
        print 'input string: ' + target_byte
        print target_byte[:-3]
        print 'bits to hide: ' + bits_to_hide

    '''
    print target_byte
    print target_byte[3:]
    print
    print 'Bits to hide: ' + bits_to_hide
    print
    '''

    if target_byte[3:] == bits_to_hide:
        lsb_encode_byte_string = target_byte

    else:
        lsb_encode_byte_string = target_byte[:-3] + bits_to_hide

    if debug:
        print 'encoded: ' + lsb_encode_byte_string
        print

    return lsb_encode_byte_string, int(lsb_encode_byte_string, 2)


def hide_file(payload_file, host_image):

    print ('INFO: Reading in payload file')
    bin_string_array, bit_count = read_binary_into_string_array(payload_file)
    input_image = Image.open(host_image)

    (width, height, max_hideable_size) = max_hidable(input_image)

    print 'INFO: Checking capacity of host image for this payload'
    if (bit_count / 8 / 1024) < max_hideable_size:
        print 'INFO: Host image is able to embed payload'

    else:
        print 'ERROR: Host image is to small to contain the payload file'

        # return an error state
        return 1

    # get the RGBA image data from the host file
    rgba_image_data = input_image.convert("RGBA").getdata()

    # Create a new image that will contain the host image and the hidden data.
    # Make it the same width and height as the source image using the information retrieved via
    # the max_hideable function call above
    steg_image = Image.new('RGBA', (width, height))
    steg_image_data = steg_image.getdata()

    #for pixel_value in list(steg_image_data):
    #    print pixel_value

    print 'INFO: Embedding file'
    byte_index = 0
    for h in range(height):

        for w in range(width):
            (red, green, blue, alpha) = rgba_image_data.getpixel((w, h))

            #TODO: Figure out a better way of doing this part so I dont lose 1 bit of space on each encode step

            if byte_index < len(bin_string_array):
               # print 'hiding: ' + bin_string_array[byte_index]
                _, encoded_red_int   = lsb_encode_byte(bin_string_array[byte_index][:3],'{0:08b}'.format(red), debug=False)
                _, encoded_blue_int  = lsb_encode_byte(bin_string_array[byte_index][3:6],'{0:08b}'.format(blue), debug=False)

                # Pad the last part with a zero to fill out the byte.
                # This is just to make our lives easier, but it is wasteful

                _, encoded_green_int = lsb_encode_byte('0' + bin_string_array[byte_index][6:],'{0:08b}'.format(green), debug=False)

                #steg_image_data.putpixel((w,h),(encoded_red_int,encoded_blue_int,encoded_green_int, alpha))
                steg_image_data.putpixel((w, h), (red, blue, green, alpha))

            byte_index = byte_index + 1

    #steg_image.putdata(steg_image_data)
    steg_image.save('output.jpg', 'JPEG')

    print 'INFO: Embedding complete'


if __name__ == "__main__":

    hide_file('shakespeare.zip', 'input.jpg')

