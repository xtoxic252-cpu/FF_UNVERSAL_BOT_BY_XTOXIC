import requests
import json
import os
import time
import random
import string
from typing import Optional, Dict, Tuple

class GuestAccountManager:
    """
    Manages Free Fire guest accounts.
    Captures guest credentials and exchanges them for OAuth tokens.
    """
    
    GUEST_TOKEN_URL = "https://ffmconnect.live.gop.garenanow.com/oauth/guest/token/grant"
    
    def __init__(self, accounts_file: str = "guest_accounts.json"):
        self.accounts_file = accounts_file
        self.accounts = self._load_accounts()
        
    def _load_accounts(self) -> list:
        """Load existing guest accounts from file"""
        if os.path.exists(self.accounts_file):
            with open(self.accounts_file, 'r') as f:
                return json.load(f)
        return []
    
    def _save_accounts(self):
        """Save accounts to disk"""
        with open(self.accounts_file, 'w') as f:
            json.dump(self.accounts, f, indent=2)
    
    def generate_guest_credentials(self) -> Tuple[str, str]:
        """
        Generate random guest credentials.
        Real Free Fire guest accounts use uid + password format.
        Returns: (uid, password)
        """
        # Guest UIDs are typically 10-12 digit numbers
        uid = ''.join(random.choices(string.digits, k=11))
        # Guest passwords are alphanumeric
        password = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
        return uid, password
    
    def exchange_guest_token(self, uid: str, password: str) -> Optional[Dict]:
        """
        Exchange guest credentials for access_token + open_id.
        
        POST to guest/token/grant with:
        {
            "uid": "12345678901",
            "password": "abc123...",
            "device_id": "random_hex",
            "app_version": "1.99.2"
        }
        """
        payload = {
            "uid": uid,
            "password": password,
            "device_id": os.urandom(8).hex(),
            "app_version": "1.99.2"
        }
        
        headers = {
            "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 10; SM-G975F)",
            "Content-Type": "application/json",
            "Accept-Encoding": "gzip"
        }
        
        try:
            resp = requests.post(
                self.GUEST_TOKEN_URL,
                json=payload,
                headers=headers,
                timeout=15
            )
            if resp.status_code == 200:
                data = resp.json()
                account = {
                    "uid": uid,
                    "password": password,
                    "access_token": data.get("access_token"),
                    "open_id": data.get("open_id"),
                    "refresh_token": data.get("refresh_token"),
                    "created_at": time.time()
                }
                self.accounts.append(account)
                self._save_accounts()
                return account
            else:
                # Token grant failed - credentials may be invalid
                return None
        except Exception as e:
            print(f"[!] Guest token exchange failed: {e}")
            return None
    
    def create_fresh_account(self) -> Optional[Dict]:
        """Generate new guest credentials and exchange for token"""
        uid, password = self.generate_guest_credentials()
        return self.exchange_guest_token(uid, password)
    
    def get_active_accounts(self) -> list:
        """Get accounts with valid (non-expired) tokens"""
        now = time.time()
        # Guest tokens typically expire after ~24 hours
        return [a for a in self.accounts if now - a.get("created_at", 0) < 86400]
    
    def refresh_account(self, account: Dict) -> Optional[Dict]:
        """Refresh an expired account token"""
        if "refresh_token" in account:
            refresh_url = "https://ffmconnect.live.gop.garenanow.com/oauth/guest/token/refresh"
            payload = {
                "refresh_token": account["refresh_token"],
                "uid": account["uid"]
            }
            try:
                resp = requests.post(refresh_url, json=payload, timeout=15)
                if resp.status_code == 200:
                    data = resp.json()
                    account["access_token"] = data.get("access_token")
                    account["created_at"] = time.time()
                    self._save_accounts()
                    return account
            except:
                pass
        return None
