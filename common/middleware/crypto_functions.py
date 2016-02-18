#!/usr/bin/env python

import os, time
import base64
from Crypto import Random
from Crypto.Cipher import AES
from Crypto.PublicKey import RSA


BLOCK_SIZE = 16
BLOCK_SZ = 32
def generate_container_key():
    """
    Generate a random AES key for the container
    """
    random_bytes = os.urandom(BLOCK_SIZE)
    secret = base64.b64encode(random_bytes).decode('utf-8')
    return secret


def encrypt_token(secret, sender, receiver):
    """
    Cipher the token for the catalog using either AES or RSA encryption
    """
    # sender = self.userID
    if sender == receiver:
        # AES encryption using the master key
        master_key = get_masterKey(sender)
        pad = lambda s: s + (BLOCK_SIZE - len(s) % BLOCK_SIZE) * chr(BLOCK_SIZE - len(s) % BLOCK_SIZE)
        secret = pad(secret)
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(master_key, AES.MODE_CBC, iv)
        result = base64.b64encode(iv + cipher.encrypt(secret))
    else:
        # RSA encryption using the sender's private key and the receiver's public one
        sender_priv_key = RSA.importKey(get_privateKey(sender))
        receiver_pub_key = RSA.importKey(get_publicKey(receiver))
        ciph1 = sender_priv_key.decrypt(secret)
        result = receiver_pub_key.encrypt(ciph1, 'x')[0]
    return result


def decrypt_token(secret, sender, receiver):
    """
    Decipher the token from the catalog.
    Returns:
        The plain token
    """
    # receiver = self.userID
    if sender == receiver:
        # AES decipher
        master_key = get_masterKey(sender)
        unpad = lambda s: s[: -ord(s[len(s) - 1:])]
        secret = base64.b64decode(secret)
        iv = secret[:BLOCK_SIZE]
        cipher = AES.new(master_key, AES.MODE_CBC, iv)
        result = unpad(cipher.decrypt(secret[BLOCK_SIZE:]))
    else:
        # RSA decipher
        sender_pub_key = RSA.importKey(get_publicKey(sender))
        receiver_priv_key = RSA.importKey(get_privateKey(receiver))
        deciph1 = receiver_priv_key.decrypt(secret)
        result = sender_pub_key.encrypt(deciph1, 'x')[0]
    return result

def encrypt_msg(info, secret, path=False):
    return "Encrypted String_" + info
    """ 
    
    Encrypt a message using AES
    """
    # padding : guarantee that the value is always MULTIPLE  of BLOCK_SIZE
    """PADDING = '{'
    pad = lambda s: s + (BLOCK_SIZE - len(s) % BLOCK_SIZE) * PADDING
    encodeAES = lambda c, s: base64.b64encode(c.encrypt(pad(s)))
    cipher = AES.new(secret,AES.MODE_CBC)
    encoded = encodeAES(cipher, info)
    if path:
        # Encoding base32 to avoid paths (names containing slashes /)
        encoded = base64.b32encode(encoded)
    return encoded"""
    pad = lambda s: s + (BLOCK_SIZE - len(s) % BLOCK_SIZE) * chr(BLOCK_SIZE - len(s) % BLOCK_SIZE)
    secret = pad(secret)
    iv = Random.new().read(AES.block_size)
    cipher = AES.new(secret, AES.MODE_CBC, iv)
    result = base64.b64encode(iv + cipher.encrypt(info))
    return result
    
def decrypt_msg(encryptedString, secret, path=False):
    return encryptedString[17:]
    """ 
    Decrypt a message using AES
    """
    """PADDING = '{'
    if path:
        encryptedString = base64.b32decode(encryptedString)
    decodeAES = lambda c, e: c.decrypt(base64.b64decode(e)).rstrip(PADDING)
    key = secret
    cipher = AES.new(key)
    decoded = decodeAES(cipher, encryptedString)
    return decoded"""
    unpad = lambda s: s[: -ord(s[len(s) - 1:])]
    encryptedString = base64.b64decode(encryptedString)
    iv = encryptedString[:BLOCK_SIZE]
    cipher = AES.new(secret, AES.MODE_CBC, iv)
    result = unpad(cipher.decrypt(encryptedString[BLOCK_SIZE:]))

    return result

def get_masterKey(userID):       # TODO: deprecate it
    """
    Get the master key from local file
    Returns:
        The master key
    """
    mk_filename = "obj_world/mk_%s.key" % userID
    with open(mk_filename, 'r') as f:
        master_key = f.read()
    return base64.b64decode(master_key)


def get_publicKey(userID):    # TODO: from barbican
    """
    Get the user's public key
    Returns:
        Public key from barbican
    """
    filename = 'obj_world/pub_%s.key' % userID
    with open(filename, 'r') as f:
        pubkey = f.read()
    return pubkey


def get_privateKey(userID):  # TODO: from barbican
    """
    Get the plain user's private key from barbican
    Returns:
        The plain private key
    """
    master_key = get_masterKey(userID)
    filename = 'obj_world/pvt_%s.key' % userID
    with open(filename, 'r') as f:
        private_key = f.read()
    unpad = lambda s: s[:-ord(s[len(s) - 1:])]
    private_key = base64.b64decode(private_key)
    iv = private_key[:BLOCK_SIZE]
    cipher = AES.new(master_key, AES.MODE_CBC, iv)
    return unpad(cipher.decrypt(private_key[BLOCK_SIZE:]))
