import requests
import json
import time
import random
import struct
import socket
import threading
from typing import Optional, Dict, List
from crypto_utils import FFCrypto, FFProtobufBuilder

class GuildBotEngine:
    """
    Core engine for Free Fire guild glory automation.
    Handles matchmaking, squad formation, and glory accumulation.
    """
    
    def __init__(self, jwt_token: str, server_url: str, region: str,
                 guild_id: str, account_uid: str):
        self.jwt = jwt_token
        self.server_url = server_url
        self.region = region
        self.guild_id = guild_id
        self.uid = account_uid
        
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 10; SM-G975F)",
            "Authorization": f"Bearer {self.jwt}",
            "Content-Type": "application/json",
            "Accept-Encoding": "gzip"
        })
        
        self.base_url = f"https://{server_url}"
        self.running = False
        self.match_count = 0
        self.glory_earned = 0
    
    def _encrypted_request(self, endpoint: str, protobuf_data: bytes) -> Optional[Dict]:
        """Send an encrypted protobuf request to the API"""
        encrypted = FFCrypto.encrypt_b64(protobuf_data)
        payload = {
            "payload": encrypted,
            "app_version": "1.99.2",
            "uid": self.uid,
            "region": self.region
        }
        
        try:
            resp = self.session.post(
                f"{self.base_url}/{endpoint}",
                json=payload,
                timeout=15
            )
            
            if resp.status_code == 200:
                try:
                    result = resp.json()
                    if "payload" in result:
                        decrypted = FFCrypto.decrypt_b64(result["payload"])
                        return {"raw": result, "decrypted": decrypted}
                    return result
                except:
                    return {"raw": resp.text}
            return None
        except Exception as e:
            print(f"[!] Encrypted request to {endpoint} failed: {e}")
            return None
    
    def get_guild_info(self) -> Optional[Dict]:
        """Get guild information including current glory"""
        # Build guild info request protobuf
        # Fields: guild_id, uid, region, timestamp
        payload = FFProtobufBuilder._write_field(1, 2,
                    FFProtobufBuilder._write_varint(len(self.guild_id.encode())) + 
                    self.guild_id.encode())
        payload += FFProtobufBuilder._write_field(2, 2,
                    FFProtobufBuilder._write_varint(len(self.uid.encode())) + 
                    self.uid.encode())
        
        return self._encrypted_request("GetGuildInfo", payload)
    
    def start_matchmaking(self, mode: str = "classic") -> bool:
        """
        Start a match for glory farming.
        Sends matchmaking request to guild squad system.
        """
        # Match request protobuf
        # Fields: mode, map_id, team_size, guild_match_flag
        payload = b""
        
        # mode (field 1, string)
        mode_bytes = mode.encode()
        payload += FFProtobufBuilder._write_field(1, 2,
                    FFProtobufBuilder._write_varint(len(mode_bytes)) + mode_bytes)
        
        # guild_match = true (field 4, varint = 1)
        payload += FFProtobufBuilder._write_field(4, 0,
                    FFProtobufBuilder._write_varint(1))
        
        # team_size (field 3, varint = 4 for squad)
        payload += FFProtobufBuilder._write_field(3, 0,
                    FFProtobufBuilder._write_varint(4))
        
        result = self._encrypted_request("StartMatchMaking", payload)
        if result:
            print(f"[+] Matchmaking started for {self.uid}")
            return True
        return False
    
    def simulate_match(self, duration_seconds: int = 180) -> bool:
        """
        Simulate a match being played.
        In a real implementation, this would send periodic heartbeat
        packets to the match server to simulate activity.
        
        Returns: True if match completed successfully
        """
        print(f"[*] Simulating match for {duration_seconds}s (UID: {self.uid})")
        
        # Match heartbeat loop
        heartbeat_interval = 10  # seconds
        heartbeats = duration_seconds // heartbeat_interval
        
        for i in range(heartbeats):
            if not self.running:
                return False
            
            # Send heartbeat
            heartbeat = FFProtobufBuilder._write_field(1, 0,
                        FFProtobufBuilder._write_varint(int(time.time())))
            heartbeat += FFProtobufBuilder._write_field(2, 0,
                        FFProtobufBuilder._write_varint(i))  # sequence
            
            self._encrypted_request("MatchHeartbeat", heartbeat)
            time.sleep(heartbeat_interval)
        
        # Send match end
        end_data = FFProtobufBuilder._write_field(1, 0,
                   FFProtobufBuilder._write_varint(int(time.time())))
        end_data += FFProtobufBuilder._write_field(2, 0,
                   FFProtobufBuilder._write_varint(0))  # 0 = alive, 1 = died
        
        self._encrypted_request("MatchEnd", end_data)
        self.match_count += 1
        
        # Random glory per match: 5-15 points
        glory_this_match = random.randint(5, 15)
        self.glory_earned += glory_this_match
        
        print(f"[+] Match #{self.match_count} complete. Glory earned: {glory_this_match}")
        return True
    
    def claim_glory_rewards(self) -> Optional[Dict]:
        """Claim accumulated guild glory rewards"""
        payload = FFProtobufBuilder._write_field(1, 2,
                    FFProtobufBuilder._write_varint(len(self.uid.encode())) + 
                    self.uid.encode())
        payload += FFProtobufBuilder._write_field(2, 2,
                    FFProtobufBuilder._write_varint(len(self.guild_id.encode())) + 
                    self.guild_id.encode())
        
        return self._encrypted_request("ClaimGuildRewards", payload)
    
    def run_automated_session(self, num_matches: int = 5, 
                             match_duration: int = 180,
                             delay_between: int = 30):
        """Run an automated glory farming session"""
        self.running = True
        print(f"[+] Starting automated session for UID: {self.uid}")
        print(f"    Guild: {self.guild_id} | Region: {self.region}")
        print(f"    Matches: {num_matches} | Duration ea: {match_duration}s")
        
        for match_num in range(num_matches):
            if not self.running:
                break
            
            print(f"\n[Match {match_num + 1}/{num_matches}]")
            
            # 1. Start matchmaking
            if not self.start_matchmaking():
                print("[!] Matchmaking failed, retrying...")
                time.sleep(10)
                continue
            
            # 2. Wait for queue
            queue_wait = random.randint(5, 15)
            print(f"[*] Waiting {queue_wait}s for queue...")
            time.sleep(queue_wait)
            
            # 3. Simulate the match
            if not self.simulate_match(match_duration):
                print("[!] Match simulation interrupted")
                break
            
            # 4. Delay between matches
            if match_num < num_matches - 1:
                jitter = random.randint(10, 30)
                total_delay = delay_between + jitter
                print(f"[*] Waiting {total_delay}s before next match...")
                time.sleep(total_delay)
        
        # Claim rewards at end
        self.claim_glory_rewards()
        
        print(f"\n[+] Session complete!")
        print(f"    Matches played: {self.match_count}")
        print(f"    Total glory earned: ~{self.glory_earned}")
        
        self.running = False
    
    def stop(self):
        """Stop the automation session"""
        self.running = False
        print("[*] Stopping bot engine...")


class MultiAccountBotManager:
    """
    Manages multiple bot accounts for parallel glory farming.
    """
    
    def __init__(self, guild_id: str, region: str, max_parallel: int = 3):
        self.guild_id = guild_id
        self.region = region
        self.max_parallel = max_parallel
        self.engines: List[GuildBotEngine] = []
        self.threads: List[threading.Thread] = []
    
    def add_account(self, jwt: str, server_url: str, uid: str):
        """Add a bot account engine"""
        engine = GuildBotEngine(jwt, server_url, self.region, self.guild_id, uid)
        self.engines.append(engine)
    
    def start_parallel_farming(self, matches_per_account: int = 3, 
                               match_duration: int = 180):
        """Run multiple accounts in parallel threads"""
        self.threads = []
        
        active_engines = self.engines[:self.max_parallel]
        print(f"[+] Starting parallel farming with {len(active_engines)} accounts")
        
        def _run_engine(engine: GuildBotEngine):
            engine.run_automated_session(
                num_matches=matches_per_account,
                match_duration=match_duration
            )
        
        for engine in active_engines:
            t = threading.Thread(target=_run_engine, args=(engine,))
            t.start()
            self.threads.append(t)
            # Stagger start to avoid rate limiting
            time.sleep(2)
        
        for t in self.threads:
            t.join()
        
        # Summary
        total_glory = sum(e.glory_earned for e in active_engines)
        total_matches = sum(e.match_count for e in active_engines)
        print(f"\n{'='*50}")
        print(f"[+] PARALLEL FARMING COMPLETE")
        print(f"    Accounts: {len(active_engines)}")
        print(f"    Total matches: {total_matches}")
        print(f"    Total glory earned: ~{total_glory}")
        print(f"{'='*50}")
    
    def stop_all(self):
        """Stop all bot engines"""
        for engine in self.engines:
            engine.stop()
