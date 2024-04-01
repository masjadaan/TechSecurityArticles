#!/usr/bin/env python
from binascii import hexlify
from flask import Flask, render_template
from cbc import AesCbc, bit_flipping

app = Flask(__name__)

KEY = b"abcdefghijklmnop"
IV = b"1234567890123456"


@app.route('/')
def index():
    try:
        original_text = b"Your userid: 9. Can you make it zero?"
        modified_iv = None

        crypto = AesCbc(KEY, IV)
        data = crypto.cbc_encrypt(original_text)
        original_iv = data[:16]
        original_encrypted_text = data[16:]

        data = bit_flipping(ciphertext=data,
                            position=7,
                            xor_value=7)

        modified_iv = data[:16]
        decrypted_text = crypto.cbc_decrypt(data)

        return render_template('index.html',
                               original_text=original_text.decode('utf-8'),
                               original_iv=original_iv.decode('utf-8'),
                               original_encrypted_text=hexlify(original_encrypted_text).decode('utf-8'),

                               modified_iv=modified_iv.decode('utf-8') if modified_iv is not None else None,
                               decrypted_text=decrypted_text.decode('utf-8'))
    except Exception as e:
        print(f"An error occurred: {e}")
        # Log the error or provide a user-friendly error message
        return render_template('error.html', error_message="An error occurred")


if __name__ == '__main__':
    app.run(debug=True)
