

# python-aes


This is my simple implementation of the AES256 algorithm. 
I initially implemented this project originally as part of the
Cryptography Course at the Högskolan Dalarna in 2015. 
The concept of each function can be found on Wikipedia.

Although it can be used in practice, it's main purpose was
 to learn the algorithm and practice my python. For better performance
consider C/C++ implementations. 


`AESInterface` defines a minimum set of functions which an AES algorithm should
have. There are 

- `AESString` (implementing CBC)
- `AESBytes` (implementing CBC for file encryption)
- `AESStringCTR` (implementing Counter-Mode)
- `AESBytesCTR`(implementing Counter-Mode for file encryption)

For usage of the classes have a look at the tests.