#Image Encryption with Image

##Abstract
The purpose of this project is to encrypt an image by combining it with another image, without being noticed by human eyes. The image being encrypted will be called a "encrypted image". The image that is used to carry the information of the encrypted image will be called the "base image", while the result of the combination is called the "combined image". The process is very much like the companding in telecommunication. 

This project iterates through 2 versions. The first version requires the users on the both ends have the same base image, with which they can compare to the combined image and aqcuire the information needed. The second version does not need the users to have any base image to decrypt, by replacing the least siginificant part of each block/byte of the base image with some information from the encrypted image. 

##Required Environment
The program is developed in `Python 3`, but it should be runnable `Python 2` with minimum twisting. 

The Image processing also make use of `OpenCV` and `NumPy`. 

Please configure these modules accordingly before using this project. 

##Additional Explaination
Although this project is called "Image Encryption", the project does not contain any encryption process in the common sense. It is mainly used to hide the information without being noticed that the information is even transferred. If encryption is really required, it can be easily implemented in the serialize and deserialize process of the project, where the encrypted image is represented in a plain string. This also means that any general information can be hided in the base image similarly after serailization. 

The data density of this method is limited, which means to hide an image of a certain size, a much larger image is needed without the anomoly in the combined image can be noticed. The ratio of the size of base image and encrypted image of the default implementation is as follow:
    Each color of one pixel of the base image is 8 bits
    2 bits of the encrypted image is hided in the 8 bits
    Thus the ration is 8 / 2 = 4
    Which means a base image of 4MB can hide a encrypted image of 1MB

The result of current implementation is quite satisfactory, which means the ration can be further reduced if needed. 