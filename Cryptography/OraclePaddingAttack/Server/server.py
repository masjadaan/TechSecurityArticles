#!/usr/bin/env python3
from binascii import hexlify

from flask import Flask, request, jsonify
from cbc import AesCbc

app = Flask(__name__)

secret_key = b"abcdefghijklmnop"
secret_iv = b"1234567890123456"
aes_cbc = AesCbc(secret_key, secret_iv)


@app.route('/process', methods=['POST'])
def process_data():
    """
    Endpoint for processing data with CBC encryption/decryption.

    This Flask application defines an endpoint '/process' for handling POST requests. The received data is expected
    to be either plaintext or ciphertext, depending on the value of the 'Is-Encrypted' header. If 'Is-Encrypted' is
    'true', the received data is assumed to be ciphertext and is decrypted using AES-CBC. If 'Is-Encrypted' is 'false',
    the received data is assumed to be plaintext and is encrypted using AES-CBC.

    :return: A JSON response containing either the decrypted data or the encrypted data, along with appropriate HTTP
    status codes. In case of an error during processing, an error message is returned with a 500 status code.
    """
    try:
        data = request.get_data()
        is_encrypted = request.headers.get('Is-Encrypted') == 'true'

        if is_encrypted:
            decrypted_data = aes_cbc.cbc_decrypt(bytes.fromhex(data.decode()))
            return jsonify({'decrypted_data': decrypted_data.decode()})
        else:
            encrypted_data = aes_cbc.cbc_encrypt(data)
            return jsonify({'encrypted_data': encrypted_data.hex()})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000)
