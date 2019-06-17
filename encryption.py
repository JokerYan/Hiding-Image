import cv2
import numpy as np
##from cryptography.fernet import Fernet

#setting of the size of each block the encrypted image is sliced into, better be power of 2
serial_block_size = 4
#order is the number of blocks needed to represent one color of a pixel
order = 0
total = 1
while total < 256:
    order += 1
    total *= serial_block_size

#helper function to convert a decimal to a number of specific base
def convert_base(num, base):
    result = []
    for i in range(order):
        result.insert(0, num % base)
        num = num // base
    return result

#convert back to decimal
def reverse_base(array, base):
    result = 0
    for digit in array:
        result = result * base + digit
    return result

#convert the image into a string
def serialize(image):
    result = []
    for row in image:
        for pixel in row:
            for color in pixel:
                result += convert_base(color, serial_block_size)
    print("serialize completed: ", len(result))
    return result

#reserve some space in the base image to store the information
def prepare_base_image(image):
    for x in np.nditer(image, op_flags=['readwrite']):
        if x > 255 - serial_block_size - 1:
            x[...] = 255 - serial_block_size - 1

#combine the base image and the encrypted image
def combine_image(serial_image, base_image):
    counter = 0
    combined_image = base_image.copy()
    for i in range(len(combined_image)):
        for j in range(len(combined_image[i])):
            for k in range(len(combined_image[i][j])):
                if counter < len(serial_image):
                    #simply add the pixel color of base image and the serialized block of encrypted image
                    combined_image[i][j][k] += serial_image[counter]
                    counter += 1
                elif counter == len(serial_image):
                    #ending symbol
                    combined_image[i][j][k] += serial_block_size + 1
                    counter += 1
    
    return combined_image

#separate the image from the combined image, with the comparison to the base image
def separate_image(combined_image, base_image):
    serialized = []
    finished = False
    for i in range(len(combined_image)):
        for j in range(len(combined_image[i])):
            for k in range(len(combined_image[i][j])):
                difference = combined_image[i][j][k] - base_image[i][j][k]
                if difference == serial_block_size + 1:
                    finished = True
                    break
                else:
                    serialized.append(difference)
            if finished:
                break
        if finished:
            break
    return serialized

#deserialize the information retrieved from the separation
def reconstruct_image(serialized, width, height):
    result_image = np.zeros((width, height, 3), dtype=np.uint8)
    for i in range(len(serialized) // order):
        color = reverse_base(serialized[i*order: (i+1)*order], serial_block_size)
        result_image[i // 3 // width][i // 3 % width][i % 3] = color
    return result_image

###reserved for further encryption
##key = Fernet.generate_key()
##cipher_suite = Fernet(key)

#encryption process
img = cv2.imread("icon.jpg", cv2.IMREAD_COLOR)
base = cv2.imread("wallpaper.jpg",  cv2.IMREAD_COLOR)

prepare_base_image(base)
cv2.imwrite("base.jpg", base)
serialized = serialize(img)

combined = combine_image(serialized, base)
cv2.imwrite("combined.jpg",combined)

#decryption process
separated_serial = separate_image(combined, base)
print(separated_serial == serialized)

decrypted_image = reconstruct_image(separated_serial, len(img), len(img[0]))
print(img[150:200])
print("\n-------------------------------\n")
print(decrypted_image[150:200])

cv2.imshow("img", img)
cv2.imshow("decrypted", decrypted_image)



