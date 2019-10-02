# python-aes

Implementation of AES256. So far it's only possible to encrypt text.
I implemented this project originally as part of the Cryptography Course at the Högskolan Dalarna in 2015. Although it can be used in practice, it's main purpose was to learn the algorithm and practice my python.

To encrypt / decrypt a file use the following code in the main.py file:

```
filename = "../res/test.txt"
key = get_key("../keys/gKey")
encrypt_file(key=key, filename=filename, output_file='../res/encrypted')
print(decrypt_file(key=key, filename="../res/encrypted"))
```
After reading the predifined key from gKey, it is expanded and the encrypted Text is saved to encrypted. The decrypt_file command takes care of the decryption of the file. For a real-world application, you woudln't use the same key all over again, but rather create for each encryption, you want to make. For this, you can use the rand\_key() function in python\_aes/helper.



