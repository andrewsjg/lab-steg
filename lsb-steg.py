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

        # Here we use a neat feature called partial functions to create a function on the fly to iterate through the input file one byte at a time and build a nice string array.

        # The functools module (https://docs.python.org/2/library/functools.html) provides high-order functions features in Python.
        # Higher Order functions is a fancy name for a function that acts on or returns another function. This is one of the pillars of functional programming
        # but that is a story for another day...

        # We want to process the file 1 byte at time to build up our byte array represented as strings of digits. To do this we need to iterate
        # over the file from beginning to end one byte at a time.

        # Python provides a way to do this using iterator objects: https://docs.python.org/2/glossary.html#term-iterator 

        file_reader = partial(input_file.read, 1)

        # Another way to write the for statement is shown below, however for the purposes of clarity and description, I think explicitly creating a function variable in this case
        # is easier to follow.

        #  for byte in iter(partial(input_file.read, 1), ''):
        for byte in iter(file_reader, ''):
            if len(byte) > 0:
                # found on stackoverflow here: http://stackoverflow.com/questions/2872381/how-to-read-a-file-byte-by-byte-in-python-and-how-to-print-a-bytelist-as-a-binar
                #bin_string += '{0:08b}'.format(ord(byte)) + '\n'
                bin_string_array.append('{0:08b}'.format(ord(byte)))

                bit_count += 8

    # Add 4 bytes to the beginning of the array to store the data size
    # this is needed later when we extract the binary

    data_size = len(bin_string_array) / 1024
    print data_size * 1024
    output_array = []

    for num in str(data_size):
        #print 'Number: ' + str(num) + ' ' + '{0:08b}'.format(int(num))
        output_array.append('{0:08b}'.format(int(num)))

    #output_array[1:1] = bin_string_array
    output_array.extend(bin_string_array)
    print len(bin_string_array)
    print len(output_array)
    return output_array, bit_count



def write_binary_from_string_array(binary_strin_array, out_file):

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

    for byte_string in binary_strin_array:
        bin_output.write(chr(int(byte_string,2)))

    bin_output.close()

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
        print 'Target Byte: ' + target_byte
        #print target_byte[:-3]
        print 'Bits to hide: ' + bits_to_hide

    '''
    print target_byte
    print target_byte[3:]
    print
    print 'Bits to hide: ' + bits_to_hide
    print
    '''


    if target_byte[len(bits_to_hide):] == bits_to_hide:
        lsb_encode_byte_string = target_byte

    else:
        lsb_encode_byte_string = target_byte[:-len(bits_to_hide)] + bits_to_hide

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

    print len(bin_string_array)

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
                _, encoded_red_int   = lsb_encode_byte(bin_string_array[byte_index][:3], '{0:08b}'.format(red), debug=False)
                _, encoded_blue_int  = lsb_encode_byte(bin_string_array[byte_index][3:6],'{0:08b}'.format(blue), debug=False)
                _, encoded_green_int = lsb_encode_byte(bin_string_array[byte_index][6:], '{0:08b}'.format(green), debug=False)


                steg_image_data.putpixel((w,h),(encoded_red_int,encoded_green_int, encoded_blue_int, alpha))
                #steg_image_data.putpixel((w, h), (red, green, blue, alpha))

            else:
                steg_image_data.putpixel((w, h), (red, green, blue, alpha))

            byte_index = byte_index + 1

    #steg_image.putdata(steg_image_data)
    steg_image.save('output.png', 'PNG')

    print 'INFO: Embedding complete'

def get_lsb(input_byte_string):
    return input_byte_string[-3:]

def unhide_file(host_image):
    steg_image = Image.open(host_image)

    image_data = steg_image.convert("RGBA").getdata()
    (width, height) = steg_image.size

    hidden_data = []

    # get the size of the hidden data from the first 4 bytes

    byte_count = 0
    size_array = []
    data_array = []
    size_str = ""
    data_size = 0

    for h in range(height):
        for w in range(width):

            (red, green, blue, alpha) = image_data.getpixel((w, h))

            if byte_count < 4:

                size_byte = get_lsb('{0:08b}'.format(red)) + get_lsb('{0:08b}'.format(blue)) + get_lsb('{0:08b}'.format(green))[-2:]
                #print 'Size byte: ' + size_byte
                size_array.append(size_byte)

            elif byte_count == 4:
                #print size_array

                for byte_str in size_array:
                    # convert byte string to integer then append to new string

                    #print byte_str
                    size_str += str(int(byte_str,2))

                data_size = (int(size_str) * 1024)
                print data_size

                data_byte = get_lsb('{0:08b}'.format(red)) + get_lsb('{0:08b}'.format(blue)) + get_lsb('{0:08b}'.format(green))[-2:]
                data_array.append(data_byte)

            elif byte_count > 4 and byte_count <= data_size + 142:
                data_byte = get_lsb('{0:08b}'.format(red)) + get_lsb('{0:08b}'.format(blue)) + get_lsb('{0:08b}'.format(green))[-2:]
                data_array.append(data_byte)


            byte_count = byte_count + 1

    print len(data_array)
    write_binary_from_string_array(data_array, "output.zip")


if __name__ == "__main__":

    hide_file('shakespeare.zip', 'input.png')
    print 'INFO: UN HIDING!'
    unhide_file('output.png')

