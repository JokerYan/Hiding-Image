import cv2
import numpy as np
##from cryptography.fernet import Fernet

#size of each block that the encrypted image is sliced into, preferrably use the power of 2
serial_block_size = 4

#number of blocks that is reserved for one additional image, such as the width or height
reserve_size = 8 # 4 ^ 8 = 2 ^ 16, 2 bytes

#number of block that is needed to represent one color of one pixel
order = 0
total = 1
while total < 256:
    order += 1
    total *= serial_block_size

#helper function used to convert a decimal to a number of specific base
def convert_base(num, base, short = True):
    result = []
    while num > 0:
        result.insert(0, num % base)
        num = num // base
    if short:
        length = order
    else:
        length = reserve_size
    
    for i in range(length - len(result)):
        result.insert(0, 0)
    return result

#reverse of the convert_base function
def reverse_base(array, base):
    result = 0
    for digit in array:
        result = result * base + digit
    return result

#serialize the image into a plain string
def serialize(image):
    result = []
    for row in image:
        for pixel in row:
            for color in pixel:
                result += convert_base(color, serial_block_size)
    print("serialize completed: ", len(result))
    return result

#clear some space from the base image for later use, 2 least significant bit in the default representation
def prepare_base_image(image):
    for x in np.nditer(image, op_flags=['readwrite']):
        x[...] = x // serial_block_size * 4

#combine the base image and the serialzied string of the encrypted image
def combine_image(serial_image, base_image, width, height):
    counter = 0
    combined_image = base_image.copy()
    width_serial = convert_base(width, serial_block_size, False)
    height_serial = convert_base(height, serial_block_size, False)
    
    for i in range(len(combined_image)):
        for j in range(len(combined_image[i])):
            for k in range(len(combined_image[i][j])):
                if counter < reserve_size:  #place for width
                    combined_image[i][j][k] = width_serial[counter]
                elif counter < reserve_size * 2: #place for height
                    combined_image[i][j][k] = height_serial[counter - reserve_size]
                elif counter < len(serial_image) + reserve_size * 2: #place for colors
                    combined_image[i][j][k] += serial_image[counter - reserve_size * 2]
                counter += 1
    
    return combined_image

#separate the image from the combined image by extract the the least significant part of each block, 2 least significant bit of each byte in the default implementation
def separate_image(combined_image):
    serialized = []
    finished = False
    counter = 0
    width_array = []
    height_array = []

    #reverse of the combine image process, extract width and height first and then the colors
    for i in range(len(combined_image)):
        for j in range(len(combined_image[i])):
            for k in range(len(combined_image[i][j])):
                info = combined_image[i][j][k] - combined_image[i][j][k] // 4 * 4
                if counter >= reserve_size * 2: #width and height read finished
                    width = reverse_base(width_array, serial_block_size)
                    height = reverse_base(height_array, serial_block_size)
                if counter < reserve_size:
                    width_array.append(info)
                elif counter < reserve_size * 2:
                    height_array.append(info)
                elif counter == width * height * 3 * serial_block_size + reserve_size * 2:
                    finished = True
                    break
                else:
                    serialized.append(info)
                counter += 1
            if finished:
                break
        if finished:
            break

    print("width: ", width, " height: ", height)
    return serialized, width, height

#deserialize the string that is extracted from the combined image into the encrypted image
def reconstruct_image(serialized, width, height):
    result_image = np.zeros((width, height, 3), dtype=np.uint8)
    for i in range(len(serialized) // order):
        color = reverse_base(serialized[i*order: (i+1)*order], serial_block_size)
        result_image[i // 3 // width][i // 3 % width][i % 3] = color
    return result_image

###reserved for further encryption, not included in the default implementation
##key = Fernet.generate_key()
##cipher_suite = Fernet(key)

#encryption process
img = cv2.imread("icon.jpg", cv2.IMREAD_COLOR)
base = cv2.imread("wallpaper.jpg",  cv2.IMREAD_COLOR)

prepare_base_image(base)
cv2.imwrite("base.jpg", base)
serialized = serialize(img)

combined = combine_image(serialized, base, len(img), len(img[0]))
cv2.imwrite("combined.jpg",combined)

#decryption process
separated_serial, width, height = separate_image(combined)
print(separated_serial[:20], serialized[:20])
print(len(separated_serial), len(serialized))

decrypted_image = reconstruct_image(separated_serial, width, height)

cv2.imshow("img", img)
cv2.imshow("decrypted", decrypted_image)



