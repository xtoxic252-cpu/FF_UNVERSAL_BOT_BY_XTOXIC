import base64
import hashlib
import os
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import json

# Reversed from Free Fire client - confirmed working constants
MAIN_KEY = b"Yg&tc%DEuh6%Zc^8"       # 16-byte AES-128 key
MAIN_IV  = b"6oyZDr22E3ychjM%"       # 16-byte IV
MAIN_KEY_B64 = "WWcmdGMlREV1aDYlWmNeOA=="
MAIN_IV_B64  = "Nm95WkRyMjJFM3ljaGpNJQ=="

class FFCrypto:
    """Free Fire AES-CBC encryption/decryption handler"""
    
    @staticmethod
    def encrypt(plaintext: bytes) -> bytes:
        """AES-128-CBC encrypt with PKCS7 padding"""
        cipher = AES.new(MAIN_KEY, AES.MODE_CBC, MAIN_IV)
        return cipher.encrypt(pad(plaintext, AES.block_size))
    
    @staticmethod
    def decrypt(ciphertext: bytes) -> bytes:
        """AES-128-CBC decrypt and unpad"""
        cipher = AES.new(MAIN_KEY, AES.MODE_CBC, MAIN_IV)
        return unpad(cipher.decrypt(ciphertext), AES.block_size)
    
    @staticmethod
    def encrypt_b64(plaintext: bytes) -> str:
        """Encrypt and return base64-encoded string"""
        return base64.b64encode(FFCrypto.encrypt(plaintext)).decode()
    
    @staticmethod
    def decrypt_b64(ciphertext_b64: str) -> bytes:
        """Decrypt from base64-encoded ciphertext"""
        return FFCrypto.decrypt(base64.b64decode(ciphertext_b64))


class FFProtobufBuilder:
    """
    Builds Protocol Buffer payloads for Free Fire internal API.
    Free Fire uses a custom protobuf-like serialization.
    Field format: (field_number << 3) | wire_type
    wire_type: 0=varint, 1=64-bit, 2=length-delimited, 5=32-bit
    """
    
    @staticmethod
    def _write_varint(value: int) -> bytes:
        """Encode a varint"""
        result = []
        while value > 0x7F:
            result.append((value & 0x7F) | 0x80)
            value >>= 7
        result.append(value & 0x7F)
        return bytes(result)
    
    @staticmethod
    def _write_field(field_num: int, wire_type: int, data: bytes) -> bytes:
        """Write a protobuf field: tag + data"""
        tag = (field_num << 3) | wire_type
        return FFProtobufBuilder._write_varint(tag) + data
    
    @staticmethod
    def build_login_req(open_id: str, login_token: str, platform: int = 1) -> bytes:
        """
        Build LoginReq protobuf for /MajorLogin
        Fields (reversed):
          1: open_id (string)
          2: login_token (string) 
          3: platform_type (int32)
          4: app_version (string)
          5: device_id (string)
        """
        payload = b""
        # Field 1: open_id
        open_id_bytes = open_id.encode()
        payload += FFProtobufBuilder._write_field(1, 2, 
                      FFProtobufBuilder._write_varint(len(open_id_bytes)) + open_id_bytes)
        # Field 2: login_token
        token_bytes = login_token.encode()
        payload += FFProtobufBuilder._write_field(2, 2,
                      FFProtobufBuilder._write_varint(len(token_bytes)) + token_bytes)
        # Field 3: platform_type (varint)
        payload += FFProtobufBuilder._write_field(3, 0,
                      FFProtobufBuilder._write_varint(platform))
        # Field 4: app_version
        ver_bytes = b"1.99.2"
        payload += FFProtobufBuilder._write_field(4, 2,
                      FFProtobufBuilder._write_varint(len(ver_bytes)) + ver_bytes)
        # Field 5: device_id
        dev_id = os.urandom(8).hex().encode()
        payload += FFProtobufBuilder._write_field(5, 2,
                      FFProtobufBuilder._write_varint(len(dev_id)) + dev_id)
        return payload
    
    @staticmethod
    def build_like_profile_req(uid: str, region: str) -> bytes:
        """
        Build LikeProfile protobuf
        Fields:
          1: target_uid (string)
          2: region (string)
          3: timestamp (int64)
        """
        payload = b""
        import time
        ts = int(time.time())
        # Field 1: uid
        uid_bytes = uid.encode()
        payload += FFProtobufBuilder._write_field(1, 2,
                      FFProtobufBuilder._write_varint(len(uid_bytes)) + uid_bytes)
        # Field 2: region
        reg_bytes = region.encode()
        payload += FFProtobufBuilder._write_field(2, 2,
                      FFProtobufBuilder._write_varint(len(reg_bytes)) + reg_bytes)
        # Field 3: timestamp (int64 = wire_type 1)
        ts_bytes = ts.to_bytes(8, 'little')
        payload += FFProtobufBuilder._write_field(3, 1, ts_bytes)
        return payload
