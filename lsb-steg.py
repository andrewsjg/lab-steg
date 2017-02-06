import struct

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

        # We can use the partial function to "freeze" the arguments for the input_file's read method, such that it returns an iterator object that
        # reads one byte at a time.

        # By doing this we create an object that can be passed to the built in iter() function and process the whole file 1 byte at a time in the for loop below

        file_reader = partial(input_file.read, 1)

        # Another way to write the for statement is shown below, however for the purposes of clarity and description, I think explicitly creating a function variable in this case
        # is easier to follow.

        #  for byte in iter(partial(input_file.read, 1), ''):
        for byte in iter(file_reader, ''):
            if len(byte) > 0:
                # Found on stackoverflow here: http://stackoverflow.com/questions/2872381/how-to-read-a-file-byte-by-byte-in-python-and-how-to-print-a-bytelist-as-a-binar

                # This builds an array of bytes represented as strings of 1's and 0's
                # What is being appended here? SInce the thing we are generating in a string we can use the format method from the string class to format the value
                # as an 8 bit (1 byte) binary value. We pass the ordinal value (the unicode value of the string) of the byte read from the file to the format method
                # The {0:08b} inserts the byte value into the string. It works like this:
                # - The {} tells the string object we are inserting a variable
                # - The first 0 tells format to use the first argument (ord(byte)) as the thing to format
                # - The : separates the formatting notation from the argument
                # - The 08 formats the variable with to 8 digits padded with zeros to the left
                # - The b converts the variable to binary

                bin_string_array.append('{0:08b}'.format(ord(byte)))

                # Keep track of the number of bits we have processed. Adds 8 to the bit_count variable for each iteration of the loop
                bit_count += 8

    # Finally we need to Add 4 bytes to the beginning of the array to store the size of the data the array holds
    # This is needed later when we extract the binary. We need to know this so we know how many bytes to read to get the
    # data out of the least significant bits

    # We  use the python struct module and the pack function to pack the data_size value byte by byte into an array of strings
    # We assume this will create an array of length 4. Since the value returned from len() will be at least 1 MB expressed as KB
    # There is certainly a better way of doing this!

    # Using struct.pack gives us a simple way of generating the binary values for the length.
    data_size = len(bin_string_array)
    output_array = ['{0:08b}'.format(ord(b)) for b in struct.pack("i", data_size)]


    # We then extend the output_array by adding on the bin_string_array we created above. This is done using the extend method available on Pythons array class
    output_array.extend(bin_string_array)

    print len(output_array)
    print output_array[:4]

    # Return the output array and the number of bits we encoded. The bit_count is not necessary really, but it could be used later.
    return output_array, bit_count


def write_binary_from_string_array(binary_string_array, out_file):

    # This is a helper function created to prove that you can take an array of strings
    # of 0's and 1's and create a valid binary file type out of it. This is the reverse of the read function above

    # NOTE: This particular implementation does not know about the extra 4 entries encoding the file length as generated above. To use
    # an array generated by the function above, you'd need to strip off the first four array items before passing to this function

    # If we use write binary (wb) mode for writing, python will write the data out to disk as raw bytes.
    # If we were to use a text mode to write this data to disk (no b option)
    # python may alter the raw bytes to encode it as text. Meaning the file may contain extra data to tell the operating system and other programs how to handled the file as text.
    # We don't want any extra data in our file as it will mess up the encoding of the binary file. We want python to simply write raw binary data

    bin_output = open(out_file, 'wb')

    # Since python uses strings to encode binary data, we can simply iterate over our binary array, convert each "binary" string
    # into the char that string represents. Then write that char out to a file.
    # Once we have iterated over out array and written all the 0's and 1's to disk as binary blobs represented by chars we will have a
    # complete binary file


    for byte_string in binary_string_array:
        bin_output.write(chr(int(byte_string,2)))

    bin_output.close()

def max_hidable(input_image):
    # Simple function to determine the maximum amount of data that can be hidden in
    # is given input image

    img = input_image
    (width, height) = img.size

    # Maximum hideable size 9 in KB) if we use the 3 least significant bits
    max_hideable = width * height * 3.0 / 8 / 1024

    # return the width and hieght as a tuple and the max_hideable size as KB
    return width, height, max_hideable


def size_required_to_hide(input_size_bits):
    # Simple function to determine what data size is required to hid the given input data
    return 3 * 8 * input_size_bits


def bits_from_bytes(byte_size):
    # Simple function to return the number of bits in a given quatity of bytes
    return byte_size * 1024 * 8


def lsb_encode_byte(bits_to_hide, target_byte,debug=False):

    # This function takes some bits to hide and a byte to hide them in
    # and hides them in the least significant bits of that byte
    # It assumes the "bits" to hide are a string of 1's and 0's
    # and the target byte is also a string of 8 1's and zeros

    # This function simply replaces the last x characters of the string (target_byte)
    # with the bits_to_hide string

    # To do this in reality you would operate on the actual bits
    # and use pythons bitwise operators to mask the target byte
    # and replace the least significant bits with the bits to hide
    # see: https://wiki.python.org/moin/BitwiseOperators

    if debug:
        print 'Target Byte: ' + target_byte
        print 'Bits to hide: ' + bits_to_hide

    # If the least significant bits of the target byte are the same as the bits we need to hide we do nothing.
    # Simply return the target_byte
    # Otherwise replace the least significant bits of the byte with the new bits passed.

    # Obviously the more bits we replace in the byte, the bigger the change to the end data (image in this case)
    # so we would tend to only replace the last 3 or 4 bits in the image data.

    if target_byte[len(bits_to_hide):] == bits_to_hide:
        lsb_encode_byte_string = target_byte

    else:
        lsb_encode_byte_string = target_byte[:-len(bits_to_hide)] + bits_to_hide

    if debug:
        print 'encoded: ' + lsb_encode_byte_string
        print

    return lsb_encode_byte_string, int(lsb_encode_byte_string, 2)


def hide_file(payload_file, host_image):
    # This function does the work of hiding the payload file inside an image file

    print ('INFO: Reading in payload file')
    # Read the binary we want to hide into the string bin_string_array. This function has returns two
    # values: a string representation of the binary and the count of the number of bits

    bin_string_array, bit_count = read_binary_into_string_array(payload_file)

    # Read in the image. Here we are using the pillow image library, which
    # will need to be installed to run this code see: https://python-pillow.org/, to read in the
    # host image.
    #
    # This is the on concession in this code. I dont manually read in and manipulate the image.
    # This is doable natively in python, however this code is above the LSB Steganography piece
    # and not reading and manipulating image files.
    # If this were a pure bitmap we could just read it directly and easily twiddle the image bits
    # However we want to use PNG files which have compression, headers and other metadata we need to
    # navigate to get at the image data (bits). So instead of getting bogged down in that, we let pillow
    # do the heavy lifting.
    input_image = Image.open(host_image)

    # Get the max hideable size so we can check if we can hide the data in the target file
    # This function returns three values. The width and height of the image as well as the max hideable size

    (width, height, max_hideable_size) = max_hidable(input_image)

    # Do the check to see if we can hide the file
    print 'INFO: Checking capacity of host image for this payload'
    if (bit_count / 8 / 1024) < max_hideable_size:
        print 'INFO: Host image is able to embed payload'

    else:
        print 'ERROR: Host image is to small to contain the payload file'

        # return an error state
        return 1

    # Get the Red, Green, Blue and Alpha (RGBA) image data from the host file
    rgba_image_data = input_image.convert("RGBA").getdata()

    # Create a new image that will contain the host image and the hidden data.
    # Make it the same width and height as the source image using the information retrieved via
    # the max_hideable function call above
    # The new image will have  Red, Green, Blue and Alpha (RGBA) channels and be the same height and width
    # as the host image. The RGB data for each pixel

    steg_image = Image.new('RGBA', (width, height))

    # Now extract out only the image data from the file. Not any headers or other metadata.
    # We can manipulate this data and only affect the image itself and not the overall integrity of the
    # entire file. For example if we changed some header information it would make the file
    # unreadable by image viewers so it would no longer look like or be a valid image.
    steg_image_data = steg_image.getdata()

    print 'INFO: Embedding file'

    # Lopp over the image data by height and width. For every iteration of the height (outer) loop
    # we get a bunch of bits making up one line in the image. Its the least significant bit of each red, green and blue byte
    # where we will hide our data.
    byte_index = 0
    for h in range(height):

        for w in range(width):
            (red, green, blue, alpha) = rgba_image_data.getpixel((w, h))

            #TODO: Figure out a better way of doing this part so I dont lose 1 bit of space on each encode step

            # Check to see if the number of bytes we have processed so far is still less than the number of bytes we need to hide
            # If it is then we do some hiding otherwise we just write he original data of the host image back out to the output
            # image

            if byte_index < len(bin_string_array):
               # This is where we hide our payload! We lsb encode the first 3 bits in the red byte, the next 3 bits in the blue byte
               # and another 3 bits in the green byte.
               # So we can hide 9 bits of our payload per line in our host image.

               # We could also hide things in the alpha channel, but this has a more adverse affect on the image, so
               # for this example I have steer clear and we just use the same alpha as the source.

               # Since the payload is encoded as 1's and 0's in a string, we can just silce the string up using the ranges / slices
               # see: https://docs.python.org/2/tutorial/introduction.html for some better examples
               # The {0:08b} bit is described above.
                _, encoded_red_int   = lsb_encode_byte(bin_string_array[byte_index][:3], '{0:08b}'.format(red), debug=False)
                _, encoded_blue_int  = lsb_encode_byte(bin_string_array[byte_index][3:6],'{0:08b}'.format(blue), debug=False)
                _, encoded_green_int = lsb_encode_byte(bin_string_array[byte_index][6:], '{0:08b}'.format(green), debug=False)

                # Write the encoded pixel (consisting of the red, green and blue elements) to our output image.

                steg_image_data.putpixel((w,h),(encoded_red_int,encoded_green_int, encoded_blue_int, alpha))

            else:
                steg_image_data.putpixel((w, h), (red, green, blue, alpha))

            # Increment the byte_index counter to keep track of how many bytes we have procesed.
            byte_index = byte_index + 1

    # Once we are done, save the image out as a PNG.
    steg_image.save('output.png', 'PNG')

    print 'INFO: Embedding complete'

def get_lsb(input_byte_string):
    return input_byte_string[-3:]

def unhide_file(host_image):
    steg_image = Image.open(host_image)

    image_data = steg_image.convert("RGBA").getdata()
    (width, height) = steg_image.size

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
                size_array.append(size_byte)
                size_str = size_str + chr(int(size_byte,2))

            elif byte_count == 4:

                data_size = struct.unpack("i", size_str[:4])[0]

                print data_size

                data_byte = get_lsb('{0:08b}'.format(red)) + get_lsb('{0:08b}'.format(blue)) + get_lsb('{0:08b}'.format(green))[-2:]
                data_array.append(data_byte)

            elif byte_count > 4 and byte_count <= data_size + 3:
                data_byte = get_lsb('{0:08b}'.format(red)) + get_lsb('{0:08b}'.format(blue)) + get_lsb('{0:08b}'.format(green))[-2:]
                data_array.append(data_byte)

            byte_count = byte_count + 1

    print len(data_array)
    write_binary_from_string_array(data_array, "output.zip")


if __name__ == "__main__":

    hide_file('shakespeare.zip', 'input.png')
    print 'INFO: UN HIDING!'
    unhide_file('output.png')

