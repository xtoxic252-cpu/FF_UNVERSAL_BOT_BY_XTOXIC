#!/usr/bin/env python3
"""
Free Fire Guild Glory Automation Bot
Authorized Penetration Testing Tool
"""

import sys
import time
import json
import argparse
from typing import Optional

from guest_account_manager import GuestAccountManager
from jwt_generator import JWTGenerator
from guild_bot_engine import GuildBotEngine, MultiAccountBotManager


class FGGuildBot:
    """
    Free Fire Guild Glory Bot - Full Pipeline Orchestrator
    """
    
    def __init__(self, guild_id: str, region: str = "IND",
                 target_glory: int = 1000, max_accounts: int = 5):
        self.guild_id = guild_id
        self.region = region
        self.target_glory = target_glory
        self.max_accounts = max_accounts
        
        self.guest_mgr = GuestAccountManager()
        self.jwt_gen = JWTGenerator()
        self.bot_mgr = MultiAccountBotManager(guild_id, region, max_accounts)
        
        self.total_glory = 0
    
    def bootstrap_accounts(self, count: int = 3) -> list:
        """
        Create and authenticate multiple guest accounts.
        Returns list of (uid, jwt, server_url) tuples.
        """
        print(f"[*] Bootstrapping {count} guest accounts...")
        authenticated = []
        
        attempts = 0
        while len(authenticated) < count and attempts < count * 3:
            attempts += 1
            
            # Step 1: Create guest account
            print(f"  [{len(authenticated)+1}/{count}] Creating guest account...")
            account = self.guest_mgr.create_fresh_account()
            if not account:
                print("  [!] Failed to create guest account, retrying...")
                continue
            
            print(f"  [+] Guest account created: UID={account['uid'][:6]}...")
            
            # Step 2: Generate JWT
            print(f"  [*] Generating JWT...")
            jwt_info = self.jwt_gen.generate_jwt(
                account["open_id"],
                account["access_token"]
            )
            
            if not jwt_info or "jwt" not in jwt_info:
                print("  [!] JWT generation failed")
                continue
            
            jwt = jwt_info["jwt"]
            server_url = self.jwt_gen.get_server_for_region(
                jwt_info.get("lockRegion", self.region)
            )
            
            authenticated.append((account["uid"], jwt, server_url))
            print(f"  [+] JWT obtained! Server: {server_url}")
            
            # Small delay between account creations
            time.sleep(1)
        
        print(f"[+] Bootstrapped {len(authenticated)}/{count} accounts")
        return authenticated
    
    def run(self, matches_per_account: int = 5, 
            match_duration: int = 180):
        """Run the full automation pipeline"""
        
        print(f"""
{'='*60}
  Free Fire Guild Glory Bot
{'='*60}
  Guild ID:    {self.guild_id}
  Region:      {self.region}
  Target:      {self.target_glory} glory
  Max Accnts:  {self.max_accounts}
{'='*60}
""")
        
        # Phase 1: Bootstrap accounts
        accounts = self.bootstrap_accounts(self.max_accounts)
        if not accounts:
            print("[!] No accounts could be created. Exiting.")
            return
        
        # Phase 2: Add accounts to bot manager
        for uid, jwt, server_url in accounts:
            self.bot_mgr.add_account(jwt, server_url, uid)
        
        # Phase 3: Run parallel farming
        print(f"\n[*] Starting glory farming phase...")
        self.bot_mgr.start_parallel_farming(
            matches_per_account=matches_per_account,
            match_duration=match_duration
        )
        
        # Phase 4: Check results
        total = sum(e.glory_earned for e in self.bot_mgr.engines)
        progress = min(100, int((total / self.target_glory) * 100))
        
        print(f"\n[*] Glory Progress: {total}/{self.target_glory} ({progress}%)")
        
        if total >= self.target_glory:
            print("[+] TARGET GLORY REACHED!")
        else:
            print(f"[*] Need {self.target_glory - total} more glory. "
                  f"Run again with more accounts/matches.")
    
    def continuous_mode(self, matches_per_cycle: int = 3,
                        cycles: int = 10, cycle_delay: int = 60):
        """Run continuous farming cycles"""
        print("[*] Starting CONTINUOUS farming mode")
        print(f"    Cycles: {cycles} | Matches/cycle: {matches_per_cycle}")
        
        for cycle in range(cycles):
            print(f"\n{'='*40}")
            print(f"[Cycle {cycle+1}/{cycles}]")
            print(f"{'='*40}")
            
            # Refresh accounts each cycle
            self.bot_mgr = MultiAccountBotManager(
                self.guild_id, self.region, self.max_accounts
            )
            
            accounts = self.bootstrap_accounts(self.max_accounts)
            if accounts:
                for uid, jwt, server_url in accounts:
                    self.bot_mgr.add_account(jwt, server_url, uid)
                
                self.bot_mgr.start_parallel_farming(
                    matches_per_account=matches_per_cycle,
                    match_duration=180
                )
            
            if cycle < cycles - 1:
                print(f"\n[*] Cycle delay: {cycle_delay}s before next cycle...")
                time.sleep(cycle_delay)
        
        print("\n[+] Continuous farming complete!")


def main():
    parser = argparse.ArgumentParser(
        description="Free Fire Guild Glory Automation Bot (Authorized Testing)"
    )
    parser.add_argument("--guild-id", required=True, 
                       help="Target guild ID for glory farming")
    parser.add_argument("--region", default="IND",
                       choices=["IND", "BR", "US", "ID", "TH", "VN"],
                       help="Game server region")
    parser.add_argument("--target", type=int, default=1000,
                       help="Target glory amount (default: 1000)")
    parser.add_argument("--accounts", type=int, default=3,
                       help="Number of bot accounts to use (default: 3)")
    parser.add_argument("--matches", type=int, default=5,
                       help="Matches per account per session (default: 5)")
    parser.add_argument("--duration", type=int, default=180,
                       help="Match duration in seconds (default: 180)")
    parser.add_argument("--continuous", action="store_true",
                       help="Run in continuous farming mode")
    parser.add_argument("--cycles", type=int, default=10,
                       help="Number of cycles in continuous mode")
    
    args = parser.parse_args()
    
    bot = FGGuildBot(
        guild_id=args.guild_id,
        region=args.region,
        target_glory=args.target,
        max_accounts=args.accounts
    )
    
    if args.continuous:
        bot.continuous_mode(
            matches_per_cycle=args.matches,
            cycles=args.cycles
        )
    else:
        bot.run(
            matches_per_account=args.matches,
            match_duration=args.duration
        )


if __name__ == "__main__":
    main()
