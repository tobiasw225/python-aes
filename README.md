

# python-aes

![Tests](https://travis-ci.org/tobiasw225/python-aes.svg?branch=main
)


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


Usually, you would want to encrypt/ decrypt a string. 
To make this as easy as possible use the AESString class. 
The following code is copied of the doc-tests.

```
>>> my_aes = AESString()
>>> enc = "".join(s for s in my_aes.encrypt('test string'))
>>> dec_string = "".join(s for s in my_aes.decrypt(enc)).rstrip()
>>> print(dec_string)
test string
```
...and of course you would also love to encrypt files, 
independent on their file format. For this you can use the AESBytes class.
Both classes are derived from AESInterface.

```
>>> my_aes = AESBytes()
>>> filename = "res/test.png"
>>> output_file = "res/test.enc.png"
>>> dec_file = "res/test.dec.png"
>>> my_aes.encrypt(filename=filename, output_file=output_file)
>>> my_aes.decrypt(filename=output_file, output_file=dec_file)
>>> print(Path(filename).stat().st_size == Path(dec_file).stat().st_size)
True
```

With Counter-Mode, parallelization can be achieved without using the weak
EBC:
  
```
>>> my_aes = AESStringCTR()
>>> my_aes.set_key("8e81c9e1ff726e35655705c6f362f1c0733836869c96056e7128970171d26fe1")
>>> my_aes.set_nonce("b2e47dd87113a992")
>>> test_string = "123456sehr gut."
>>> enc = my_aes.encrypt(test_string)
>>> dec = "".join(s for s in my_aes.decrypt(enc))
>>> print(dec)
    123456sehr gut.
```

The same is possible for byte-files:

```
>>> my_aes = AESBytesCTR()
>>> filename = "res/test.png"
>>> output_file = "res/test.enc.png"
>>> dec_file = "res/test.dec.png"
>>> my_aes.set_key("8e81c9e1ff726e35655705c6f362f1c0733836869c96056e7128970171d26fe1")
>>> my_aes.set_nonce("b2e47dd87113a992")
>>> my_aes.encrypt(filename=filename, output_file=output_file)
>>> my_aes.decrypt(filename=output_file, output_file=dec_file)
>>> print(Path(filename).stat().st_size == Path(dec_file).stat().st_size)
True
```