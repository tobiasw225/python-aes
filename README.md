# python-aes

This is my simple implementation of the AES256 algorithm. 
I initially implemented this project originally as part of the Cryptography Course at the Högskolan Dalarna in 2015. Although it can be used in practice, it's main purpose was to learn the algorithm and practice my python. For better performance consider a C/C++ implementation.

To encrypt / decrypt a file use the following code in the main.py file:

```
filename = "../res/test.txt"
key = get_key("../keys/gKey")
encrypt_file(key=key, filename=filename, output_file='../res/encrypted')
print(decrypt_file(key=key, filename="../res/encrypted"))
```
After reading the predifined key from gKey, it is expanded and the encrypted Text is saved to encrypted. The decrypt_file command takes care of the decryption of the file. For a real-world application, you woudln't use the same key all over again, but rather create for each encryption, you want to make. For this, you can use the rand\_key() function in python\_aes/helper.

Usually, you would want to encrypt/ decrypt a string. To make this as easy as possible use the AESString class:


```
my_aes = AESString()
enc = my_aes.encrypt("nice and easy.")
dec = my_aes.decrypt(enc)
assert dec == "nice and easy."
print(dec)
```
...and of course you would also love to encrypt files, independent on their file format. For this you can use the AESBytes class. Both classes are derived from AESInterface.

```
my_aes = AESBytes()
filename = "~/Bilder/sample/octagon-nextcloud{}.png"
output_file = filename.format('.enc')
my_aes.encrypt(filename=filename.format(''),
                output_file=output_file)
dec_file = filename.format('.dec')
my_aes.decrypt(filename=output_file,
           output_file=dec_file)
```