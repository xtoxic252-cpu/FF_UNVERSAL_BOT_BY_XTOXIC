import requests
import json
import time
from typing import Optional, Dict, Tuple
from crypto_utils import FFCrypto, FFProtobufBuilder

class JWTGenerator:
    """
    Generates JWT tokens from guest account credentials.
    JWT is required for all authenticated Free Fire API calls.
    """
    
    LOGIN_URLS = {
        "major": "https://loginbp.ggblueshark.com/MajorLogin",
        "minor": "https://loginbp.ggblueshark.com/MinorLogin"
    }
    
    # Server URL mapping based on lockRegion
    SERVER_MAP = {
        "IND": "client.ind.freefiremobile.com",
        "BR":  "client.us.freefiremobile.com",
        "US":  "client.us.freefiremobile.com",
        "SAC": "client.us.freefiremobile.com",
        "NA":  "client.us.freefiremobile.com",
        "ID":  "clientbp.ggblueshark.com",
        "TH":  "clientbp.ggblueshark.com",
        "VN":  "clientbp.ggblueshark.com",
    }
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 10; SM-G975F)",
            "Accept-Encoding": "gzip",
            "Connection": "Keep-Alive"
        })
    
    def generate_jwt(self, open_id: str, login_token: str, 
                     platform: int = 1) -> Optional[Dict]:
        """
        Exchange open_id + login_token for JWT.
        
        Flow:
        1. Build LoginReq protobuf
        2. AES-CBC encrypt the protobuf
        3. POST encrypted payload to /MajorLogin
        4. Decrypt response to get JWT + server info
        """
        # Step 1: Build protobuf
        login_req = FFProtobufBuilder.build_login_req(open_id, login_token, platform)
        
        # Step 2: Encrypt with AES-CBC
        encrypted_payload = FFCrypto.encrypt_b64(login_req)
        
        # Step 3: POST to login endpoint
        payload = {
            "payload": encrypted_payload,
            "app_version": "1.99.2",
            "device_id": "a1b2c3d4e5f6a7b8"
        }
        
        try:
            resp = self.session.post(
                self.LOGIN_URLS["major"],
                json=payload,
                timeout=20
            )
            
            if resp.status_code == 200:
                result = resp.json()
                
                # Step 4: Decrypt response
                if "payload" in result:
                    decrypted = FFCrypto.decrypt_b64(result["payload"])
                    # Parse the protobuf response
                    jwt_info = self._parse_login_response(decrypted)
                    
                    if jwt_info:
                        jwt_info["raw_response"] = result
                        return jwt_info
                
                # Some endpoints return JSON directly
                return result
            else:
                print(f"[!] JWT generation failed: HTTP {resp.status_code}")
                print(f"    Response: {resp.text[:200]}")
                return None
                
        except Exception as e:
            print(f"[!] JWT generation error: {e}")
            return None
    
    def _parse_login_response(self, resp_data: bytes) -> Optional[Dict]:
        """
        Parse the LoginResponse protobuf.
        Contains: jwt, lockRegion, serverUrl, accountInfo
        """
        # Attempt to extract strings from protobuf response
        result = {}
        
        # Try direct JSON decode if applicable
        try:
            json_data = json.loads(resp_data.decode())
            return json_data
        except:
            pass
        
        # Parse protobuf fields (simplified)
        try:
            text = resp_data.decode('utf-8', errors='replace')
            
            # Extract JWT
            import re
            jwt_match = re.search(r'([A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+)', text)
            if jwt_match:
                result["jwt"] = jwt_match.group(1)
            
            # Extract region
            region_match = re.search(r'(IND|BR|US|SAC|NA|ID|TH|VN)', text)
            if region_match:
                result["lockRegion"] = region_match.group(1)
            
            # Extract server URL
            url_match = re.search(r'([a-z]+\.[a-z]+\.freefiremobile\.com)', text)
            if url_match:
                result["serverUrl"] = url_match.group(1)
            
        except:
            pass
        
        return result if result else None
    
    def get_server_for_region(self, region: str) -> str:
        """Get the API server URL for a region"""
        return self.SERVER_MAP.get(region, "clientbp.ggblueshark.com")
