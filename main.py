#!/usr/bin/env python3
"""
██████╗░███████╗    ██████╗░░█████╗░████████╗
██╔══██╗██╔════╝    ██╔══██╗██╔══██╗╚══██╔══╝
██████╔╝█████╗░░    ██████╦╝██║░░██║░░░██║░░░
██╔══██╗██╔══╝░░    ██╔══██╗██║░░██║░░░██║░░░
██║░░██║██║░░░░░    ██████╦╝╚█████╔╝░░░██║░░░
╚═╝░░╚═╝╚═╝░░░░░    ╚═════╝░░╚════╝░░░░╚═╝░░░

█╗░░░██╗  ██╗  ██╗ █████╗  ██████╗██╗  ██╗███████╗██████╗ 
██║░░██╔╝  ██║  ██║██╔══██╗██╔════╝██║ ██╔╝██╔════╝██╔══██╗
██║░██╔╝   ███████║██║░░██║██║░░░░░█████╔╝ █████╗  ██████╔╝
██║██╔╝    ██╔══██║██║░░██║██║░░░░░██╔═██╗ ██╔══╝  ██╔══██╗
╚███╔╝     ██║░░██║╚█████╔╝╚██████╗██║░░██╗███████╗██║░░██║
░╚══╝░     ╚═╝░░╚═╝░╚════╝░░╚═════╝╚═╝░░╚═╝╚══════╝╚═╝░░╚═╝

Free Fire Security Assessment — Authorized Pentest Bot
████████████████████████████████████████████████████
"""

import os, sys, json, time, random, requests, threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from colorama import init, Fore, Style

init(autoreset=True)

# ─── ASCII BANNER ───────────────────────────────────
BANNER = Fore.RED + Style.BRIGHT + """
██╗░░██╗████████╗░█████╗░██╗░░██╗██╗░█████╗░
╚██╗██╔╝╚══██╔══╝██╔══██╗╚██╗██╔╝██║██╔══██╗
░╚███╔╝░░░░██║░░░██║░░██║░╚███╔╝░██║██║░░╚═╝
░██╔██╗░░░░██║░░░██║░░██║░██╔██╗░██║██║░░██╗
██╔╝╚██╗░░░██║░░░╚█████╔╝██╔╝╚██╗██║╚█████╔╝
╚═╝░░╚═╝░░░╚═╝░░░░╚════╝░╚═╝░░╚═╝╚═╝░╚════╝░
""" + Fore.CYAN + """
██╗░░░██╗██╗░░██╗░█████╗░████████╗██████╗░░█████╗░░██████╗
╚██╗░██╔╝╚██╗██╔╝██╔══██╗╚══██╔══╝╚════██╗██╔══██╗██╔════╝
░╚████╔╝░░╚███╔╝░███████║░░░██║░░░░░███╔═╝██║░░██║██║░░██╗
░░╚██╔╝░░░██╔██╗░██╔══██║░░░██║░░░██╔══╝░░██║░░██║██║░░╚██╗
░░░██║░░░██╔╝╚██╗██║░░██║░░░██║░░░███████╗╚█████╔╝╚██████╔╝
░░░╚═╝░░░╚═╝░░╚═╝╚═╝░░╚═╝░░░╚═╝░░░╚══════╝░╚════╝░░╚═════╝░
""" + Fore.YELLOW + """
╔══════════════════════════════════════════════════════════╗
║   Free Fire Security Assessment — Authorized Pentest     ║
║   Bot System v4.0 — Guild Domination Toolkit             ║
╚══════════════════════════════════════════════════════════╝
""" + Style.RESET_ALL


# ─── API ENDPOINTS ───────────────────────────────────
ENDPOINTS = {
    "register_guest": "https://grant-access-token.deno.dev/get_token",
    "jwt_token": "https://jwt-gen-api-v2.onrender.com/token",
    "change_nickname": "https://change-nick-api-lkteam.onrender.com/changenick",
    "change_bio": "https://change-bio-api-lkteam.onrender.com/changebio",
    "guild_info": "https://freefireinfo-zy9l.onrender.com/api/v1/guildInfo",
    "guild_join": "https://guild-api-lkteam.onrender.com/guild/join",
    "guild_approve": "https://guild-api-lkteam.onrender.com/guild/approve",
    "send_like": "https://likes-api-lkteam-v3.onrender.com/like",
    "equip_items": "https://equip-api-lkteam.onrender.com/equip",
    "player_info": "https://freefireinfo-zy9l.onrender.com/api/v1/player-profile",
}

# Bundle item IDs
BUNDLE_ITEMS = [
    5001001, 5001002, 5001003,  # Golden Sakuna (top, bottom, shoes)
    5002001, 5002002, 5002003,  # Golden Hip Hop (top, bottom, shoes)
    5003001, 5003002, 5003003, 5003004,  # Prime 8 (top, bottom, shoes, mask)
]

# Default bio with the ASCII
DEFAULT_BIO = """██╗░░██╗████████╗░█████╗░██╗░░██╗██╗░█████╗░
╚██╗██╔╝╚══██╔══╝██╔══██╗╚██╗██╔╝██║██╔══██╗
░╚███╔╝░░░░██║░░░██║░░██║░╚███╔╝░██║██║░░╚═╝
░██╔██╗░░░░██║░░░██║░░██║░██╔██╗░██║██║░░██╗
██╔╝╚██╗░░░██║░░░╚█████╔╝██╔╝╚██╗██║╚█████╔╝
╚═╝░░╚═╝░░░╚═╝░░░░╚════╝░╚═╝░░╚═╝╚═╝░╚════╝░

free fire is hack all the api is in my undercontrol"""


def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')


def print_header():
    clear_screen()
    print(BANNER)


def log(msg, color=Fore.CYAN):
    ts = datetime.now().strftime('%H:%M:%S')
    print(f"{Fore.WHITE}[{ts}] {color}{msg}{Style.RESET_ALL}")


def api_request(method, url, params=None, headers=None, data=None, retries=3):
    for attempt in range(retries):
        try:
            if method.upper() == "GET":
                resp = requests.get(url, params=params, headers=headers, timeout=20)
            elif method.upper() == "POST":
                resp = requests.post(url, params=params, headers=headers, json=data, timeout=20)
            else:
                return None
            if resp.status_code == 200:
                try:
                    return resp.json()
                except:
                    return {"raw": resp.text}
            elif resp.status_code == 429:
                time.sleep(2 ** attempt)
                continue
            else:
                time.sleep(1)
                continue
        except Exception:
            time.sleep(2 ** attempt)
            continue
    return None


# ═══════════════════════════════════════════════════════
#  CORE FUNCTIONS
# ═══════════════════════════════════════════════════════

def create_guest_account():
    resp = api_request("GET", ENDPOINTS["register_guest"])
    if resp and resp.get("uid") and resp.get("password"):
        uid = resp["uid"]
        password = resp["password"]
        # Get JWT
        token_resp = api_request("GET", ENDPOINTS["jwt_token"],
                                params={"uid": uid, "password": password})
        token = token_resp.get("token") if token_resp else None
        return uid, password, token
    return None, None, None


def set_nickname(uid, password, nickname, region):
    resp = api_request("GET", ENDPOINTS["change_nickname"],
                      params={"uid": uid, "password": password,
                              "newnick": nickname, "region": region})
    return resp is not None


def set_bio(uid, password, bio, region):
    resp = api_request("GET", ENDPOINTS["change_bio"],
                      params={"uid": uid, "password": password,
                              "newbio": bio, "region": region})
    return resp is not None


def join_guild(uid, password, token, guild_id, region):
    resp = api_request("GET", ENDPOINTS["guild_join"],
                      params={"uid": uid, "password": password,
                              "guild_id": guild_id, "region": region,
                              "token": token or ""})
    if resp:
        status = resp.get("status", resp.get("code", 0))
        return status in [200, "200", "success", True]
    return False


def approve_member(target_uid, owner_token, guild_id, region):
    resp = api_request("GET", ENDPOINTS["guild_approve"],
                      params={"uid": target_uid, "token": owner_token,
                              "guild_id": guild_id, "region": region})
    if resp:
        status = resp.get("status", resp.get("code", 0))
        return status in [200, "200", "success", True]
    return False


def send_like(sender_uid, sender_password, sender_token, target_uid, region):
    resp = api_request("GET", ENDPOINTS["send_like"],
                      params={"uid": sender_uid, "password": sender_password,
                              "token": sender_token or "",
                              "target_uid": target_uid, "region": region})
    if resp:
        status = resp.get("status", resp.get("code", 0))
        return status in [200, "200", "success", True]
    return False


def equip_bundles(uid, password, token, region):
    resp = api_request("POST", ENDPOINTS["equip_items"],
                      params={"uid": uid, "password": password,
                              "token": token or "", "region": region,
                              "items": json.dumps(BUNDLE_ITEMS)})
    if resp:
        status = resp.get("status", resp.get("code", 0))
        return status in [200, "200", "success", True]
    return False


def fetch_guild_info(guild_id, region):
    resp = api_request("GET", ENDPOINTS["guild_info"],
                      params={"guildID": guild_id, "region": region})
    return resp


# ═══════════════════════════════════════════════════════
#  BOT WORKER
# ═══════════════════════════════════════════════════════

def create_and_setup_bot(bot_num, guild_id, region, owner_token=None):
    nickname = f"XBOT_{bot_num}"
    bio = DEFAULT_BIO

    log(f"  [{nickname}] Creating guest account...", Fore.BLUE)
    uid, password, token = create_guest_account()
    if not uid:
        log(f"  [{nickname}] FAILED to create account", Fore.RED)
        return None

    log(f"  [{nickname}] UID: {uid} | Token: {'✓' if token else '✗'}", Fore.BLUE)

    # Set nickname
    time.sleep(random.uniform(0.3, 1.0))
    if set_nickname(uid, password, nickname, region):
        log(f"  [{nickname}] Nickname set → {nickname}", Fore.GREEN)
    else:
        log(f"  [{nickname}] Nickname failed", Fore.RED)

    # Set bio
    time.sleep(random.uniform(0.3, 1.0))
    if set_bio(uid, password, bio, region):
        log(f"  [{nickname}] Bio set ✓", Fore.GREEN)
    else:
        log(f"  [{nickname}] Bio failed", Fore.RED)

    # Join guild
    time.sleep(random.uniform(0.5, 1.5))
    joined = join_guild(uid, password, token, guild_id, region)
    if joined:
        log(f"  [{nickname}] Joined guild ✓", Fore.GREEN)
    else:
        log(f"  [{nickname}] Join request sent, awaiting approval...", Fore.YELLOW)
        # Auto-approve if owner token provided
        if owner_token:
            time.sleep(random.uniform(1, 2))
            if approve_member(uid, owner_token, guild_id, region):
                joined = True
                log(f"  [{nickname}] Approved into guild ✓", Fore.GREEN)

    # Equip bundles
    time.sleep(random.uniform(0.5, 1.5))
    if equip_bundles(uid, password, token, region):
        log(f"  [{nickname}] Bundles equipped: Golden Sakuna + Hip Hop + Prime 8", Fore.CYAN)

    return {
        "uid": uid, "password": password, "token": token,
        "nickname": nickname, "in_guild": joined
    }


# ═══════════════════════════════════════════════════════
#  MAIN — INTERACTIVE MENU
# ═══════════════════════════════════════════════════════

def main():
    print_header()
    
    # ── Get Guild ID ──────────────────────────────────
    print(Fore.YELLOW + Style.BRIGHT + "\n╔══════════════════════════════════════════════╗")
    print("║           INITIAL SETUP                     ║")
    print("╚══════════════════════════════════════════════╝" + Style.RESET_ALL)
    
    while True:
        guild_id = input(Fore.WHITE + "\n[?] Enter GUILD ID: " + Fore.GREEN).strip()
        if guild_id.isdigit() and len(guild_id) >= 5:
            break
        print(Fore.RED + "[-] Invalid Guild ID (must be numeric, 5+ digits)")
    
    # ── Region — always IND ───────────────────────────
    region = "IND"
    log(f"[+] Region set to: IND (India)", Fore.GREEN)
    
    # ── Guild Owner Token (optional) ──────────────────
    print(Fore.YELLOW + "\n[?] Guild Owner Token (for auto-approve bots, optional):")
    owner_token = input(Fore.WHITE + "    Enter token or press Enter to skip: " + Fore.GREEN).strip()
    if owner_token == "":
        owner_token = None
        log("[!] No owner token — bots will send join requests (manual approve needed)", Fore.YELLOW)
    else:
        log("[+] Owner token provided — auto-approve enabled", Fore.GREEN)
    
    # ── Bot Count ─────────────────────────────────────
    while True:
        try:
            count_input = input(Fore.WHITE + "\n[?] Number of bots to create (1-9999): " + Fore.GREEN).strip()
            num_bots = int(count_input)
            if 1 <= num_bots <= 9999:
                break
            print(Fore.RED + "[-] Enter a number between 1 and 9999")
        except ValueError:
            print(Fore.RED + "[-] Invalid number")
    
    # ── Start ID ──────────────────────────────────────
    start_id = 1
    
    # ── Target UID for /like ──────────────────────────
    target_uid = input(Fore.WHITE + "\n[?] Target UID to /like (receive likes): " + Fore.GREEN).strip()
    
    # ── Like all guild members? ───────────────────────
    like_all = input(Fore.WHITE + "\n[?] /like ALL guild members too? (y/n): " + Fore.GREEN).strip().lower()
    like_all_members = like_all.startswith('y')
    
    # ── Auto matches for glory? ───────────────────────
    auto_matches = input(Fore.WHITE + "\n[?] Run auto matches for glory? (y/n): " + Fore.GREEN).strip().lower()
    run_matches = auto_matches.startswith('y')
    
    if run_matches:
        while True:
            try:
                matches_per = int(input(Fore.WHITE + "    Matches per bot (1-20): " + Fore.GREEN).strip())
                if 1 <= matches_per <= 20:
                    break
            except ValueError:
                pass
    
    # ── Concurrent workers ────────────────────────────
    while True:
        try:
            workers = int(input(Fore.WHITE + "\n[?] Concurrent workers (threads, 1-50): " + Fore.GREEN).strip())
            if 1 <= workers <= 50:
                break
        except ValueError:
            pass
    
    # ── CONFIRMATION ──────────────────────────────────
    print_header()
    print(Fore.CYAN + Style.BRIGHT + "\n╔══════════════════════════════════════════════╗")
    print("║           OPERATION SUMMARY                  ║")
    print("╚══════════════════════════════════════════════╝" + Style.RESET_ALL)
    print(f"  Guild ID:       {Fore.GREEN}{guild_id}{Style.RESET_ALL}")
    print(f"  Region:         {Fore.GREEN}{region}{Style.RESET_ALL}")
    print(f"  Bot Count:      {Fore.GREEN}{num_bots}{Style.RESET_ALL}")
    print(f"  Bot Names:      {Fore.GREEN}XBOT_{start_id} → XBOT_{start_id + num_bots - 1}{Style.RESET_ALL}")
    print(f"  Owner Token:    {Fore.GREEN}{'Provided ✓' if owner_token else 'None (manual approve)'}{Style.RESET_ALL}")
    print(f"  Target UID:     {Fore.GREEN}{target_uid}{Style.RESET_ALL}")
    print(f"  Like Members:   {Fore.GREEN}{'Yes' if like_all_members else 'No'}{Style.RESET_ALL}")
    print(f"  Auto Matches:   {Fore.GREEN}{'Yes (' + str(matches_per) + ' each)' if run_matches else 'No'}{Style.RESET_ALL}")
    print(f"  Workers:        {Fore.GREEN}{workers}{Style.RESET_ALL}")
    
    confirm = input(Fore.YELLOW + Style.BRIGHT + "\n[!] Start operation? (y/n): " + Fore.GREEN).strip().lower()
    if not confirm.startswith('y'):
        print(Fore.RED + "\n[-] Aborted by user.")
        sys.exit(0)
    
    # ══════════════════════════════════════════════════
    #  PHASE 1: CREATE BOTS
    # ══════════════════════════════════════════════════
    print_header()
    log("╔══════════════════════════════════════════════╗", Fore.CYAN)
    log("║  PHASE 1: CREATING BOT ACCOUNTS              ║", Fore.CYAN)
    log("╚══════════════════════════════════════════════╝", Fore.CYAN)
    
    bots = []
    succeeded = 0
    failed = 0
    
    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = {
            executor.submit(create_and_setup_bot, i, guild_id, region, owner_token): i
            for i in range(start_id, start_id + num_bots)
        }
        
        for future in as_completed(futures):
            bot = future.result()
            if bot:
                bots.append(bot)
                succeeded += 1
            else:
                failed += 1
            
            # Live progress
            total = succeeded + failed
            pct = (succeeded / total) * 100 if total > 0 else 0
            sys.stdout.write(f"\r{Fore.WHITE}[LIVE] Created: {Fore.GREEN}{succeeded}{Fore.WHITE} | Failed: {Fore.RED}{failed}{Fore.WHITE} | Total: {total} ({pct:.0f}%){Style.RESET_ALL}  ")
            sys.stdout.flush()
    
    print()
    log(f"\n[✓] Phase 1 Complete: {succeeded} bots created, {failed} failed", Fore.GREEN + Style.BRIGHT)
    
    if not bots:
        log("[-] No bots available. Aborting.", Fore.RED + Style.BRIGHT)
        return
    
    # Save progress
    with open("bots_data.json", "w") as f:
        json.dump(bots, f, indent=2)
    log("[+] Bot data saved to bots_data.json", Fore.GREEN)
    
    # ══════════════════════════════════════════════════
    #  PHASE 2: FETCH GUILD MEMBERS
    # ══════════════════════════════════════════════════
    print()
    log("╔══════════════════════════════════════════════╗", Fore.CYAN)
    log("║  PHASE 2: FETCHING GUILD MEMBER DATA         ║", Fore.CYAN)
    log("╚══════════════════════════════════════════════╝", Fore.CYAN)
    
    log("[*] Fetching guild info...", Fore.BLUE)
    guild_data = None
    for attempt in range(3):
        guild_data = fetch_guild_info(guild_id, region)
        if guild_data:
            break
        time.sleep(2)
    
    if guild_data:
        log(f"[+] Guild data received", Fore.GREEN)
        
        # Extract members 
        members = []
        data_section = guild_data.get("data", guild_data)
        if isinstance(data_section, dict):
            members = data_section.get("members", data_section.get("playerList", []))
        elif isinstance(data_section, list):
            members = data_section
        members = guild_data.get("members", members)
        
        if members:
            # Save guild members
            with open("guild_members.json", "w") as f:
                json.dump(members, f, indent=2)
            
            with open("guild_members.txt", "w") as f:
                for m in members:
                    muid = m.get("uid", m.get("account_id", m.get("id", "?")))
                    mname = m.get("nickname", m.get("name", "?"))
                    mlvl = m.get("level", "?")
                    f.write(f"UID: {muid} | {mname} | Lv.{mlvl}\n")
            
            # Display
            print(Fore.CYAN + "\n╔═══ GUILD MEMBERS ═══╗")
            for idx, m in enumerate(members[:25], 1):
                muid = m.get("uid", m.get("account_id", m.get("id", "?")))
                mname = m.get("nickname", m.get("name", "?"))
                mlvl = m.get("level", "?")
                print(f"  {idx:3d}. {muid} | {mname} (Lv.{mlvl})")
            if len(members) > 25:
                print(f"  ... +{len(members)-25} more")
            print("╚═══════════════════════╝")
            
            log(f"[+] Saved {len(members)} members to guild_members.txt & guild_members.json", Fore.GREEN)
        else:
            log(f"[!] No members array found in response, saving raw data", Fore.YELLOW)
            with open("guild_raw_data.json", "w") as f:
                json.dump(guild_data, f, indent=2)
            members = []
    else:
        log("[-] Failed to fetch guild data (API may be rate-limited)", Fore.RED)
        members = []
    
    # ══════════════════════════════════════════════════
    #  PHASE 3: SEND /LIKE TO TARGET
    # ══════════════════════════════════════════════════
    print()
    log("╔══════════════════════════════════════════════╗", Fore.CYAN)
    log("║  PHASE 3: SENDING /LIKE TO TARGET            ║", Fore.CYAN)
    log("╚══════════════════════════════════════════════╝", Fore.CYAN)
    
    like_count = 0
    like_fail = 0
    
    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = {
            executor.submit(send_like, b["uid"], b["password"], b.get("token", ""), target_uid, region): b
            for b in bots
        }
        for future in as_completed(futures):
            if future.result():
                like_count += 1
            else:
                like_fail += 1
            sys.stdout.write(f"\r{Fore.WHITE}[LIVE] Likes sent: {Fore.GREEN}{like_count}{Fore.WHITE} | Failed: {Fore.RED}{like_fail}{Style.RESET_ALL}")
            sys.stdout.flush()
    
    print()
    log(f"[✓] Likes to {target_uid}: {like_count} sent, {like_fail} failed", Fore.GREEN + Style.BRIGHT)
    
    # ══════════════════════════════════════════════════
    #  PHASE 3b: /LIKE ALL GUILD MEMBERS
    # ══════════════════════════════════════════════════
    if like_all_members and members:
        print()
        log("╔══════════════════════════════════════════════╗", Fore.CYAN)
        log("║  PHASE 3b: LIKING ALL GUILD MEMBERS          ║", Fore.CYAN)
        log("╚══════════════════════════════════════════════╝", Fore.CYAN)
        
        # Use non-guild bots (or all bots) to like guild members
        like_senders = [b for b in bots if not b.get("in_guild")] or bots
        
        member_likes = 0
        member_fails = 0
        total_jobs = min(len(like_senders), 30) * min(len(members), 60)
        
        with ThreadPoolExecutor(max_workers=min(workers, 20)) as executor:
            futures = {}
            for sender in like_senders[:30]:
                for member in members[:60]:
                    muid = member.get("uid", member.get("account_id", member.get("id")))
                    if muid and str(muid) != target_uid:
                        futures[executor.submit(
                            send_like, sender["uid"], sender["password"],
                            sender.get("token", ""), muid, region
                        )] = (sender["nickname"], muid)
            
            for future in as_completed(futures):
                if future.result():
                    member_likes += 1
                else:
                    member_fails += 1
                total_done = member_likes + member_fails
                sys.stdout.write(f"\r{Fore.WHITE}[LIVE] Guild member likes: {Fore.GREEN}{member_likes}{Fore.WHITE} | Failed: {Fore.RED}{member_fails}{Fore.WHITE} / {total_jobs}{Style.RESET_ALL}")
                sys.stdout.flush()
        
        print()
        log(f"[✓] Total guild member likes: {member_likes}", Fore.GREEN + Style.BRIGHT)
    
    # ══════════════════════════════════════════════════
    #  PHASE 4: AUTO MATCHES FOR GLORY
    # ══════════════════════════════════════════════════
    if run_matches and bots:
        print()
        log("╔══════════════════════════════════════════════╗", Fore.CYAN)
        log("║  PHASE 4: AUTO MATCHES FOR GUILD GLORY       ║", Fore.CYAN)
        log("╚══════════════════════════════════════════════╝", Fore.CYAN)
        
        match_bots = bots[:20]  # Use up to 20 bots for matches
        log(f"[*] Running {matches_per} matches each on {len(match_bots)} bots...", Fore.BLUE)
        
        def run_bot_matches(bot, n):
            uid, pwd, token = bot["uid"], bot["password"], bot.get("token", "")
            for i in range(n):
                try:
                    # Simulate match via sending start_match request
                    resp = api_request("GET", "https://match-api-lkteam.onrender.com/start",
                                      params={"uid": uid, "password": pwd,
                                              "token": token or "", "region": region,
                                              "mode": "ranked"})
                    time.sleep(random.uniform(2, 5))
                    # Submit result (random win/loss for glory)
                    api_request("GET", "https://match-api-lkteam.onrender.com/result",
                               params={"uid": uid, "password": pwd,
                                       "token": token or "", "region": region,
                                       "match_id": f"m_{int(time.time())}_{i}",
                                       "won": random.choice(["true", "false"]),
                                       "kills": random.randint(0, 8),
                                       "placement": random.randint(1, 18)})
                except:
                    pass
                time.sleep(random.uniform(3, 8))
        
        match_threads = []
        for bot in match_bots:
            t = threading.Thread(target=run_bot_matches, args=(bot, matches_per))
            t.start()
            match_threads.append(t)
        
        for t in match_threads:
            t.join()
        
        log(f"[✓] Auto matches completed on {len(match_bots)} bots", Fore.GREEN + Style.BRIGHT)
    
    # ══════════════════════════════════════════════════
    #  FINAL SUMMARY
    # ══════════════════════════════════════════════════
    print()
    print(Fore.CYAN + Style.BRIGHT + "╔══════════════════════════════════════════════╗")
    print("║           OPERATION COMPLETE               ║")
    print("╚══════════════════════════════════════════════╝" + Style.RESET_ALL)
    print(f"  {Fore.GREEN}Bots Created:{Style.RESET_ALL}     {succeeded}")
    print(f"  {Fore.GREEN}Bots in Guild:{Style.RESET_ALL}   {sum(1 for b in bots if b.get('in_guild'))}")
    print(f"  {Fore.GREEN}Likes to Target:{Style.RESET_ALL}  {like_count}")
    print(f"  {Fore.GREEN}Guild Members:{Style.RESET_ALL}   {len(members) if members else 0}")
    print(f"  {Fore.GREEN}Files Saved:{Style.RESET_ALL}")
    print(f"    • bots_data.json")
    print(f"    • guild_members.json")
    print(f"    • guild_members.txt")
    print()
    print(Fore.YELLOW + Style.BRIGHT + "  [✓] All systems operational. Guild domination in progress.")
    print(Fore.YELLOW + "      Push to Top 1 region — bots farming glory 24/7" + Style.RESET_ALL)
    print(Fore.CYAN + "╚══════════════════════════════════════════════╝" + Style.RESET_ALL)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(Fore.RED + "\n\n[!] Interrupted by user. Exiting.")
        sys.exit(0)
    except Exception as e:
        print(Fore.RED + f"\n[!] Error: {e}")
        sys.exit(1)
