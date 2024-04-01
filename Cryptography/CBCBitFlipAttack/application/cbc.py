from binascii import hexlify

from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad


class AesCbc:
    def __init__(self, key, iv):
        """
        Initializes an instance of AesCbc with the provided key and IV.

        :param key: (bytes) The encryption key.
        :param iv: (bytes) The initialization vector.
        """
        self.iv = iv
        self.bs = AES.block_size
        self.key = key
        self.cipher = None

    def cbc_encrypt(self, plaintext):
        """
        Encrypts the given plaintext using AES in Cipher Block Chaining (CBC) mode.

        :param plaintext: (bytes) The input plaintext to be encrypted.
        :return: (bytes) The encrypted ciphertext.
        :raises ValueError: If the input plaintext is not of type 'bytes'.
        :raises Exception: If an error occurs during encryption.
        """
        if not isinstance(plaintext, bytes):
            raise ValueError("Input plaintext must be bytes")

        try:
            cipher = AES.new(self.key, AES.MODE_CBC, self.iv)
            padded_data = pad(plaintext, self.bs)
            encrypted_data = cipher.encrypt(padded_data)
            return self.iv + encrypted_data
        except Exception as e:
            print(f"Encryption error: {e}")
            raise

    def cbc_decrypt(self, ciphertext):
        """
        Decrypts the given ciphertext using AES in Cipher Block Chaining (CBC) mode.

        :param ciphertext: (bytes) The input ciphertext to be decrypted.
        :return: (bytes) The decrypted plaintext.
        :raises ValueError: If the input ciphertext is not of type 'bytes'.
        :raises Exception: If an error occurs during decryption.
        """
        if not isinstance(ciphertext, bytes):
            raise ValueError("Input ciphertext must be bytes")

        try:
            data, iv = ciphertext[self.bs:], ciphertext[:self.bs]
            cipher = AES.new(self.key, AES.MODE_CBC, iv)
            decrypted_data = cipher.decrypt(data)
            return unpad(decrypted_data, self.bs)
        except Exception as e:
            print(f"Decryption error: {e}")
            raise


def bit_flipping(ciphertext, position, xor_value):
    """
    Modifies the encrypted text by XORing a specified value at a specified position.

    :param ciphertext: (bytes) The input ciphertext.
    :param position: (int) The position in the ciphertext where XOR should be applied.
    :param xor_value: (int) The value to XOR at the specified position.
    :return: (bytes) The modified ciphertext.
    :raises ValueError: If the position or xor_value is not of type 'int' or if the position is invalid.
    :raises Exception: If an error occurs during bit flipping.
    """
    try:
        byte_list = bytearray(ciphertext)
        if not isinstance(position, int) or not isinstance(xor_value, int):
            raise ValueError("Position and xor_value must be integers")

        if position < 0 or position >= len(byte_list[16:]):
            raise ValueError("Invalid position")
        print(hex(byte_list[position]))
        byte_list[position] ^= xor_value
        return bytes(byte_list)
    except Exception as e:
        print(f"Bit flipping error: {e}")
        raise
