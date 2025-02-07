from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
import os
from base64 import b64encode, b64decode


class KeyManage():
    # Function to generate a key and store it in a file
    def generate_key(self, file_path):
        # Generate a random 256-bit key for AES encryption
        key = os.urandom(32)
        
        # Save the key to a file
        with open(file_path, 'wb') as key_file:
            key_file.write(key)
        
        return key

    # Function to load an encryption key from a file
    def load_key(self, file_path):
        with open(file_path, 'rb') as key_file:
            key = key_file.read()
        
        return key


class Crypto():
    # Function to encrypt the password
    def encrypt_password(self, password, key):
        # Generate a random initialization vector (IV) for AES encryption
        iv = os.urandom(16)

        # Pad the password to make it a multiple of AES block size (16 bytes)
        padder = padding.PKCS7(128).padder()
        padded_data = padder.update(password.encode()) + padder.finalize()

        # Initialize the AES cipher
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        encryptor = cipher.encryptor()

        # Encrypt the password
        encrypted_password = encryptor.update(padded_data) + encryptor.finalize()

        # Return the encrypted password with the IV (both must be stored)
        return b64encode(iv + encrypted_password).decode()

    # Function to decrypt the password
    def decrypt_password(self, encrypted_password, key):
        # Decode the encrypted password from base64
        encrypted_data = b64decode(encrypted_password)

        # Extract the IV (first 16 bytes) and the encrypted password
        iv = encrypted_data[:16]
        encrypted_password_data = encrypted_data[16:]

        # Initialize the AES cipher
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        decryptor = cipher.decryptor()

        # Decrypt the password
        decrypted_padded_password = decryptor.update(encrypted_password_data) + decryptor.finalize()

        # Unpad the decrypted password
        unpadder = padding.PKCS7(128).unpadder()
        password = unpadder.update(decrypted_padded_password) + unpadder.finalize()

        return password.decode()
