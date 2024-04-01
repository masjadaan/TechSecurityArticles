#!/usr/bin/env python

from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from binascii import hexlify, unhexlify
import secrets


def bit_flipping(ciphertext, position, xor_value):
    """
    Modifies the encrypted text by XORing the specified value at the specified position.
    :param ciphertext: (bytes) The hex-encoded ciphertext.
    :param position: (int) The position in the ciphertext where XOR should be applied.
    :param xor_value: (int) The value to XOR at the specified position.
    :return: (bytes) The modified hex-encoded ciphertext.
    """
    print(f"in bitFlipping; ciphertext: {hex(ciphertext[position])}")
    decoded_data = unhexlify(ciphertext)
    byte_list = bytearray(decoded_data)
    print(f"in bitFlipping: unhex ciphertext: {hex(byte_list[position])}")

    # Ensure position is within the bounds of the ciphertext
    if position < 0 or position >= 58:
        raise ValueError("Invalid position")

    # XOR the value at the specified position
    byte_list[position] ^= xor_value
    print(f"in bitFlipping: after xor: {hex(byte_list[position])}")
    # Return the hex-encoded modified ciphertext
    return hexlify(byte_list)


class AESCBC:
    def __init__(self):
        """
        Initializes an instance of AESCBC with a randomly generated IV and key.
        """
        # self.iv = secrets.token_bytes(AES.block_size)
        self.iv = b"1234567890123456"
        self.bs = AES.block_size
        # self.key = secrets.token_bytes(self.bs)
        self.key = b"abcdefghijklmnop"
        self.cipher = None

    def cbc_encrypt(self, plaintext):
        """
        Encrypts the given plaintext using AES in Cipher Block Chaining (CBC) mode.
        :param plaintext: (str) The input plaintext to be encrypted.
        :return: (bytes) The hex-encoded ciphertext.
        """
        self.cipher = AES.new(self.key, AES.MODE_CBC, self.iv)
        padded_data = pad(plaintext, self.bs)
        encrypted_data = self.cipher.encrypt(padded_data)
        return hexlify(self.iv + encrypted_data)

    def cbc_decrypt(self, ciphertext):
        """
        Decrypts the given ciphertext using AES in Cipher Block Chaining (CBC) mode.
        :param ciphertext: (bytes) The hex-encoded ciphertext.
        :return: (str) The decrypted plaintext.
        """
        decoded_data = unhexlify(ciphertext)
        data, iv = decoded_data[self.bs:], decoded_data[:self.bs]
        self.cipher = AES.new(self.key, AES.MODE_CBC, iv)
        decrypted_data = self.cipher.decrypt(data)
        return unpad(decrypted_data, AES.block_size)