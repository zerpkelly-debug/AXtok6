# -*- coding: utf-8 -*-
import requests
import threading
import time
import json
import urllib.parse
import datetime
import urllib3
import random
import os

# SSL Warnings বন্ধ করা
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ==========================================
# কনফিগারেশন (এখান থেকে স্পিড কন্ট্রোল করুন)
# ==========================================
ATOK_FILE_NAME = "accounts.txt"
PROXY_FILE_NAME = "proxies.txt"

CONCURRENT_ACCOUNTS = 20   # একসাথে ২০টি একাউন্ট চলবে
BOTS_PER_ACCOUNT = 20      # প্রতি একাউন্টে ২০টি বট থ্রেড
BASE_LIMIT = 930          # প্রতিটি একাউন্টের টার্গেট

# লাইভ লগিং ফাংশন (গিটহাবের জন্য অপ্টিমাইজড)
def safe_log(message):
    timestamp = datetime.datetime.now().strftime('%H:%M:%S')
    log_msg = f"[{timestamp}] {message}"
    print(log_msg, flush=True) # flush=True দিলে গিটহাবে সাথে সাথে লেখা আসবে


class AtokMultiBot:
    def __init__(self):
        self.account_list = []
        self.proxy_list = []

    def load_files(self):
        # Accounts.txt থেকে UserID | Email রিড করা
        if not os.path.exists(ATOK_FILE_NAME):
            safe_log("❌ Error: accounts.txt ফাইলটি পাওয়া যায়নি!")
            return False
            
        with open(ATOK_FILE_NAME, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                # লাইন ফাঁকা হলে বা '|' না থাকলে স্কিপ করবে
                if not line or "|" not in line: 
                    continue
                
                parts = line.split("|")
                if len(parts) >= 2:
                    uid = parts[0].strip()
                    email = parts[1].strip()
                    
                    if uid and email:
                        self.account_list.append({"email": email, "uid": uid})
        
        # Proxies.txt রিড করা (যদি থাকে)
        if os.path.exists(PROXY_FILE_NAME):
            with open(PROXY_FILE_NAME, "r") as f:
                for line in f:
                    p = line.strip().split(":")
                    if len(p) == 4:
                        u = f"http://{p[2]}:{p[3]}@{p[0]}:{p[1]}"
                        self.proxy_list.append({"http": u, "https": u})

        safe_log(f"✅ সিস্টেম রেডি! {len(self.account_list)} টি একাউন্ট পাওয়া গেছে।")
        return len(self.account_list) > 0

    def worker(self, uid, email, state):
        session = requests.Session()
        headers = {'User-Agent': 'Mozilla/5.0 (Linux; Android 15)', 'X-Requested-With': 'com.m2e.mobile'}
        ad_url = "https://googleads.g.doubleclick.net/mads/gma?submodel=sdk_gphone64_x86_64&adid_p=1&format=interstitial_mb&ini_pn=com.android.vending&ins_pn=com.android.vending&omid_v=a.1.5.2-google_20241009&client_purpose_one=true&dv=260480602&ev=23.6.0&gl=US&hl=en&js=afma-sdk-a-v260480999.244410000.1&lv=244410203&ms=CpgECoACXYpbkGV8iVOSftDAMekBcU_lc2znB9O2_33p3PNwuZHjeNqNwu7HnFKWyJG3rERwi2qIAVthEzc37CNpultvwup6bZzoOCwPw-PikaaFQvF9lLSk1xFPjyzV7_wx2fUHy84d8knN990UY_TzW_oqtf-UDELdQWK7Yj2uBjbZChUrKkDfQAfEbdlgXc5-bSZ4PczAwWRLD8dWcCDxRQ8jSvMm1Jk_sAEMoNK7LaeQvsqTEaVuLdAfs93qtLSICJtYerxNcYP6j7kpB_BHYpyMdzTY2mtUbxjCQ2vRUtrx_ExXdS5LqgXpv5B2vYDVnnY3x5HwD2VbVArHfLX7MkVJEQqAAik5dpcvk0fYk1JEr8godq3Im1WDntsTPBqmPLARb8s0h-yCUhbvdeBVaHKHUrhFuJ8_xJiqBEKwXkjtzibxJLnoo59GGbNbCPoQzLJwV8Kq1kw8TCjUm4MkzFwn9fKfIShF5uf7ue2u2beImjvXlExR6QqAwRpWkrWe8XPKMz3HT3_itEvCQ0AGrEv6EPUISfFs1gJJ1ysVb2_A5iJp5XQwAepbwZOQRe0XohfWg0pA8nzw1mENXrKRLDZtttiBXbEuSn4NwNNcFtDSCJQpa7LFHXrzyqVFj1uEWNlASasygI_zrxx_NRIkBeVOBPu0Bbz_Zy54NolvUw-3H7JchkwSEOOHs7e4hG5rTT4Vlylfqw0SmAQKgAJFz9-ZRHYlOj5ri1E2vJ9e-0vC9Kwjy3YBnTzvlF5O-EcllCD-fVtGkKUuBRNxcEclzxDahifIb9q5OSCoslnoa9jM5lWfEv8kYC7eMmAiQu9Rp959xGj1Vl4Dhkg51su87yvOCMyCSnn1JCwhJJ6q_rPLNB4ecA8Bl-M35JbWWsX6_ePG0r643dxAfYwonbJDqTRpoTF2uRAJIukEiRLxtrJvL2v2hwr7-zFOj5nxyg4cSOZdV4DdDLBzYnM4tD1rUBQ42nINm9BBogW0Tp3a4gOG6-nf4-4WakzslSLYQyaq9p3dWyETAemzg8JDcXnIGjZ9KU8FPTfb9-KNsLUOCoAC0pWCDZhN0COwZZ8-xyZFdjd6n-vsVrq-jM8jPd3B68maF2VXKtYSDw7GFJdD6CbUEn2nrvQAmm-P_hxWB9GLw3N3ebqcEFG34zgtg9eRK7S8kPxRzapRlEarXWqfjJcxMCkfLsza3R3_sD3vEnw6OY_NmvKnsekhqsTuMSApfMvNq9r9ftgiNRVmGfFuI1pJuEHq3yeecdPG2UJBW-xlWC4HP0dkh_570lijaAQ8ckG3QYOV_IKPG7u_g81p4SjM9TZ7SXgardtShPikt3eLlio2BSgQf5B_eHeDvULz2Hnn2dqNIt9GSOG1AgBjGbxP-AmBwxYrlSoze6PNr-euvxIQ94L2kDMkFp-8LHkg3Iatqg&mv=85101930.com.android.vending&lft=1&vnm=1.2.5&plbs=0&plcs=0&risd=1&u_sd=2&request_id=1475162851&sam_b=24&sam_l=0&sam_r=0&sam_t=24&target_api=35&carrier=310260&request_agent=Flutter-GMA-5.3.1&fbs_aeid=-1763672715495716590&fbs_aiid=ed84d026b2efb0c47b9e7545b45685cf&seq_num=65&eid=318500618%2C318486317%2C318491267%2C95389098%2C318509511%2C318514156%2C95388544%2C318483611%2C318484496%2C318484801%2C318526144&guci=0.0.0.0.0.0.0.0&adtest=on&sdk_apis=7%2C8&omid_p=Google%2Fafma-sdk-a-v260480999.244410000.1&u_w=360&u_h=640&msid=com.m2e.mobile&an=123.android.com.m2e.mobile&u_audio=4&net=wi&u_so=p&rbv=1&loeid=44766145%2C318502924&preqs_in_session=2&preqs=64&time_in_session=868530&pcc=0&dload=18229&sst=1777580280000&output=html&region=mobile_app&u_tz=360&client=ca-app-pub-9027478617840640&slotname=9952810315&gsb=wi&apm_app_id=1%3A849245294575%3Aandroid%3A17045a6282e9ba9ab4301a&gmp_app_id=1%3A849245294575%3Aandroid%3A17045a6282e9ba9ab4301a&apm_app_type=1&lite=0&app_wp_code=ca-app-pub-9027478617840640&app_code=9535506442&num_ads=1&vpt=8&vfmt=18&vst=0&sdkv=o.260480999.244410000.1&sdmax=0&dmax=1&sdki=3c4d&stbg=1&bisch=false&blev=0.41&canm=true&_mv=85101930.com.android.vending&heap_free=445936&heap_max=201326592&heap_total=122484208&wv_count=4&advertised_mem_tier=0&avail_mem_tier=0&avail_proc_tier=0&rdps=11650&_cv=261434038&session_idl=20&eo_idl=36&eo_id_tsl=10&is_lat=false&rdidl=36&idtypel=4&blob=ABPQqLEabfpQcA59MgaPX1wtuBt_y7faAofi3bbFnsTYMjvMHAol2Pfu2xBE1dyari8Tpukq3mJ6d3C43sBjZa9dgkovrTzr_REfOnLqNH3LNQqxMcy0HLPBUgNXIleKhnv2eaJhmmL4DQtRAjKR-LSq1ug7tFIY2Jds7YRFkzFQNsJw_gCr_lEBIqPPzZlugiqMctfkSbWSXvkrxRan0zjBb1s0aRHee0rkPybj_jg9vB6BkZhiGUU7DT0hkf8iCVDQvT8TLi0fDYWnxDMOhsdV2K9eGbkv7QhZkIdta3q0kpaCDeWJy_LB3KzUu__ZZbtEiCEOEmhSjMm3nJzntJoogPuVKkYOT116k0GGgrW1ZjVBOYOX1CNkjdj27UIc4tAyEufZUtpeQI4bYb6EIcnpFw_GBoZ759M6mUNj_z8ROzDFs9VCZiWq1nLxGg&capsbf=7FFFFFEE&mr_itag=4509016882487189237_140&jsv=sdk_20190107_RC02-production-sdk_20260423_RC00"

        while True:
            with state['lock']:
                if state['count'] >= state['target']: break
            
            proxy = random.choice(self.proxy_list) if self.proxy_list else None
            try:
                res = session.get(ad_url, headers=headers, proxies=proxy, timeout=15, verify=False)
                if res.status_code == 200:
                    ad = res.json()['ad_networks'][0]
                    # ইমপ্রেশন ও ভিডিও দেখা
                    session.get(ad['ad']['impression_urls'][0], headers=headers, proxies=proxy, timeout=10)
                    time.sleep(random.randint(6, 8))
                    
                    # ক্লেইম
                    ts = str(int(time.time() * 1000))
                    cdata = urllib.parse.quote(json.dumps({"key": f"{uid}{ts}", "type": "MISSION_AD", "missionType": "VIDEO"}))
                    claim_url = ad['video_reward_urls'][0].replace("@gw_rwd_userid@", uid).replace("@gw_tmstmp@", ts).replace("@gw_rwd_custom_data@", cdata)
                    
                    if session.get(claim_url, headers=headers, proxies=proxy, timeout=10).status_code == 200:
                        with state['lock']:
                            state['count'] += 1
                            if state['count'] % 50 == 0:
                                safe_log(f"⚡ [অ্যাক্টিভ] {email}: {state['count']}/{state['target']} ক্লেইম সফল।")
            except:
                # নেটওয়ার্ক এরর হলে ২ সেকেন্ড অপেক্ষা করে আবার চেষ্টা করবে
                time.sleep(2)
            time.sleep(random.randint(2, 4))

    def process_account(self, acc):
        target = BASE_LIMIT + random.randint(-30, 30)
        state = {'count': 0, 'target': target, 'lock': threading.Lock()}
        
        safe_log(f"▶️ একাউন্ট শুরু: {acc['email']} | UserID: {acc['uid']} | টার্গেট: {target}")
        
        threads = []
        for _ in range(BOTS_PER_ACCOUNT):
            t = threading.Thread(target=self.worker, args=(acc['uid'], acc['email'], state))
            t.start()
            threads.append(t)
        
        for t in threads: 
            t.join()
            
        safe_log(f"✅ একাউন্ট সম্পন্ন: {acc['email']} | মোট ক্লেইম: {state['count']}")

    def start_loop(self):
        cycle = 1
        while True:
            try:
                safe_log(f"\n{'#'*40}\n🚀 সাইকেল শুরু: {cycle}\n{'#'*40}")
                
                # একাউন্টগুলোকে ছোট ছোট গ্রুপে ভাগ করা (Parallel processing)
                accounts = self.account_list.copy()
                random.shuffle(accounts)
                
                for i in range(0, len(accounts), CONCURRENT_ACCOUNTS):
                    batch = accounts[i:i + CONCURRENT_ACCOUNTS]
                    batch_threads = []
                    for acc in batch:
                        t = threading.Thread(target=self.process_account, args=(acc,))
                        t.start()
                        batch_threads.append(t)
                    
                    for t in batch_threads: 
                        t.join()
                
                safe_log(f"🏁 সাইকেল {cycle} শেষ। ২ মিনিট বিরতির পর আবার শুরু হবে...")
                time.sleep(120)
                cycle += 1
            except Exception as e:
                safe_log(f"⚠️ সাইকেলে সমস্যা হয়েছে: {e}")
                time.sleep(10) # সমস্যা হলে 10 সেকেন্ড পর আবার ট্রাই করবে

# ==========================================
# মেইন এক্সিকিউশন (সারাজীবন চলার জন্য Auto-Restart লুপ)
# ==========================================
if __name__ == "__main__":
    while True:
        try:
            bot = AtokMultiBot()
            if bot.load_files():
                bot.start_loop()
            else:
                safe_log("❌ বট চালু করা সম্ভব হয়নি। 'accounts.txt' ফাইলে 'UserID | Email' এই ফরম্যাটে ডেটা রাখুন।")
                time.sleep(60) # ফাইল না পেলে ৬০ সেকেন্ড পর আবার চেক করবে
        except KeyboardInterrupt:
            safe_log("🛑 বট ম্যানুয়ালি বন্ধ করা হয়েছে।")
            break
        except Exception as e:
            safe_log(f"🔥 সিস্টেম ক্র্যাশ করেছে: {e}। ১০ সেকেন্ড পর অটোমেটিক রিস্টার্ট হচ্ছে...")
            time.sleep(10)
