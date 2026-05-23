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

CONCURRENT_ACCOUNTS = 30   # একসাথে কতগুলো একাউন্টের কাজ চলবে (সার্ভার র‍্যাম অনুযায়ী দিন)
BOTS_PER_ACCOUNT = 30      # প্রতি একাউন্টে কতগুলো বট থ্রেড চলবে
BASE_LIMIT = 923           # প্রতিটি একাউন্টের টার্গেট রিওয়ার্ড

# ==========================================
# কুকিজ ও হেডার্স (আপনার অরিজিনাল কোড থেকে নেওয়া)
# ==========================================
DEFAULT_COOKIE = "IDE=AHWqTUlZXSTFFfvGmQ-vrIrS8IiVa4hINrpCmw7yWXXrqdd1yRDgHXfZUK0rrfdZkGM"
DRT_COOKIE = "DSID=AICoiYPOqf_PIJxg3uPdcrtpOOSk9Vz3Yj7pSJK3KcIKa4GXQxRK00-_AZzWlV3YHiJayIOv3BRwe8NSJXVDzoM0yYZlxG11li4fWlsc59dcaGCxs1Xvi85zthg_pVGpco9lvXC_tG2uoSaKypA_zmPYOXe5Aucc1pGo10aDBtPwQJ266RapHcbWbO0op75AxnJ2AGUk67O_ylUJJewqH7Lmx5SfXpRxwv2mF6y81KPT-Qfddc7V2tQ1VNoBqwscLgajyNXTtwbXhArf1HYGf4TpKuhIuwc-mA"
DRT_V2_COOKIE = "CqwCCqcCRFNJRD1BSUNvaVlQT3FmX1BJSnhnM3VQZGNydHBPT1NrOVZ6M1lqN3BTSkszS2NJS2E0R1hReFJLMDAtX0FaeldsVjNZSGlKYXlJT3YzQlJ3ZThOU0pYVkR6b00weVlabHhHMTFsaTRmV2xzYzU5ZGNhR0N4czFYdmk4NXp0aGdfcFZHcGNvOWx2WENfdEcydW9TYUt5cEFfem1QWU9YZTVBdWNjMXBHbzEwYURCdFB3UUoyNjZSYXBIY2JXYk8wb3A3NUF4bkoyQUdVazY3T195bFVKSmV3cUg3TG14NVNmWHBSeHd2Mm1GNnk4MUtQVC1RZmRkYzdWMnRRMVZOb0Jxd3NjTGdhanlOWFR0d2JYaEFyZjFIWUdmNFRwS3VoSXV3Yy1tQRgBCqoCCqcCRFNJRD1BSUNvaVlQenZMVmNxS0ljUlpCOHN6T25JT2M4RC1Fb29IbkJKX3otZEg0Q0lWZ0d3RGk5MkpOOFR5OXRjOFdsNjRxNkZpb3c5c1lXUWhVaWtENmxHQ3VrejBBaVBsRW55NlpFUnRhekhPbjRzNXdQc3VlYWY2YUIyX1hyaTV1REhBRHZtUkpmZVY0cGRSZjlaSlJBZlN3RTJOTXNLLUV1aU4yejd1VGlDZzBiRGI1ZDgwY0x2UUt5S1h3NDVaWFlicC1kZ2ZsMXhPUnBYLUNSYWphc1Mzenl6bnBVSkdpZnJaYS0xcWptaG8xUGExU3loZ2s2cnBxaHJOTGx5NFlNaTh3X0pNOHdBQjRiTlctcjZWQzh1eE50SU1ZRVY2amxxZwqqAgqnAkRTSUQ9QUlDb2lZTWNudG96VXpEblNCa1BLSERBaVRFcFVOdjc2b193ZzBNNjU2VFp3djFDdXV4anZVUnhqM2pBQ215cTE1dXM0bkhSWnJibXFwS3hDczVfdjcwaXgwcjhzZ2VaODIwYXFlWEI4RlRPVjFSclhGLTMxeWl3eGJ3V3pqdDQ5XzB5VnBpcjM3dHc3Q2JvQTJZOU9aZEUzM0Jtd3ZVWXpZWjB3VVdSZU9LM0RpQnNjb1JkamhBa096bnljbXFOTkt1RExLenpKdGtTMjFOVlFlTDZOWlp4SkpuRkZIWGlucmxCR1RNVVFfNDFnN01HTDBfZHFCR3JJY2xMb05hUktRcm5vZDh0U1dKVXZpMXNpb0JLLUdTQlZVX0ZuaEc3MVEKqgIKpwJEU0lEPUFJQ29pWVBNRVduYlhodE85LWJNZ0tWYkdNSEduMVJSeVpxTlFxQ2o1ajltd0NhT2dZdndjRWN1UVZSVXJ0dUVYRmU2eWZ4WGMyWUpNR2J4Wm1IQnBfVXowZDBpQldwQUdGNmlKd2d5cE1RRGpTcFp1ekRTOEY5TDF1OUh0VlR1MGViV3Fab0pJV295Y1UwUTRsRTllMDF3Z2tOamQ5YXBycmljZXpyZUZrQ0Nqanh5NnJmSVlhRzlqQl80ZVhneWpOaS1IZmR3ZzB1dXhjanBldk9qMkxSSjNRXzBrbThDUEYtUjU3bnQ3OV81Vkx1dXZtR0NoRy11T0ZHTGVlM0RNRUF0cmdQV3NmWlNJbk9xZkJsZTlvajZIT1JsbEZxRWZ3"
DEFAULT_AD_URL = "https://googleads.g.doubleclick.net/mads/gma?submodel=sdk_gphone64_x86_64&adid_p=1&format=interstitial_mb&ini_pn=com.android.vending&ins_pn=com.android.vending&omid_v=a.1.5.2-google_20241009&client_purpose_one=true&dv=260480602&ev=23.6.0&gl=US&hl=en&js=afma-sdk-a-v260480999.244410000.1&lv=244410203&ms=CpgECoACH6BR43YshjDxPt-AE5oceRyQYDXXYdKVzDvshqFjvYviDsCUgcTEpnOCzLm0zlFQ-GeGEBkbBx1EkD0SyERyiPkNd5TJGj1E0IL4ksaIQcMMnKjGxQxIhg7h-tVC1e502LQe-hie8PwGM_nzGO08tb28ARvsC23jAAa3TyXHFx9KO1DNYnnLbItPSL4OEid4L7bQmgQhD8x2JSWABgMpCMJQyesuiBF8woauXoS_uPuDMq9XLvUWs56er_zLRJ1hG8ZYAcH9gOsbR_xsU6eKBjSaxnM0aAHZAQXSStjg5QRVZyJJqCrgj_Agp8nX_2sMlazlNQYPQkiGHrriAC5HCAqAAo6inIz-XXC-VHAwsx6fA8rLNZwupgDeiOuEt5PFAJUFldTHejhatFvePwZL0sanoWY3oQBBl18St162mdNGYdnPEzI9zAYtkTJK9lzXq4NbDnurNdzjpAGWElKdKLaMBxKEF9atbUybKNVjrA1jiEBwnHCuK-EH8PS3Ckm-CNg4io1oARkJsWcj-H3wSGpbXm66R7LBhOWGNnl6QZuS2XXALGx8cU3L1b7d7EwyhBr4Ke19LAgyFO_9yE-n2nC_aODOJdKq5np2elnm8D6kcYVuzQpAG2ZmHYQrMse29fvD6Yq9YxiiFZdbDpYqJm5yzLfhAFtUt17cOxRmJKRXZnkSEAFuTLxAJrUH-KurqekWZhMSmAQKgAKD8qgewgKrgvBAMJas4do75AkqmThVjjfWBHRlkjcqMleLefja4ATdTXjPH6sDAI0DL7O-2j4T43VHgynm4yXhK_GeC6GnF1oLFMZghivN3EM-rfaChoH8dabZO-sILUruoEBCbjh-HM4mVQNqJputzlXaq6Yz_rXf0P3i2zYns3LJosKVIN8jd7xva9xYFB5ZufdMdsWYdVZT4ys0dudz6kmN_q5hHn5Btm-SLE2Gtkd1RHv04Pwr6Y1e6Rks77a2ln__S8H-HVvsd3f3KI9OI6SLhotUdwoFOPwPqHT8alE7_t7v9gh48R92Gic9XN-pPkMXko7H8B-bSKBw71A-CoACInv3jd8mwO2fOKKaJ0MjJBPmzDu18gLlNmzC_sW7x3rcAxMSLj3ZfIm5NFynMhviyI1Skrg41RVS2-qX2CUD7LyvvRtfGmmvo-7OpVD4-ZEqhe9HB0pngYI-J-q9cN5t7UbagV3JrcIXlBGvz6NCaIt36U5-5lpjTUmDkUkFFBOffmnPIFgU1jLFlZrhD7j7uyIKdczsSuu2KNg2r2wRmAOAB4X7np1bTiIqwuUUoZhiAnLsKw_0lBrTGgAVDwNIlNjc1fU5pwImJew0YM21NofxA8kdagqTIn1Yi1MoTNt5CnCUtvFoTfEK2rNSuNhna_TYbdOmGWNtwcZF3ls7bhIQHS6vyW8jbzcsxwhWx5P9Kw&mv=85141930.com.android.vending&lft=1&vnm=1.2.5&plbs=0&plcs=0&risd=1&u_sd=2&request_id=327727680&sam_b=24&sam_l=0&sam_r=0&sam_t=24&target_api=35&carrier=310260&request_agent=Flutter-GMA-5.3.1&fbs_aeid=2413418468896106116&fbs_aiid=ed84d026b2efb0c47b9e7545b45685cf&seq_num=13&eid=318500618%2C318486317%2C318491267%2C95391149%2C95388544%2C318483611%2C318484496%2C318484801%2C318526144&guci=0.0.0.0.0.0.0.0&adtest=on&sdk_apis=7%2C8&omid_p=Google%2Fafma-sdk-a-v260480999.244410000.1&u_w=360&u_h=640&msid=com.m2e.mobile&an=123.android.com.m2e.mobile&u_audio=4&net=wi&u_so=p&rbv=1&loeid=44766145%2C318502621&preqs_in_session=12&preqs=12&time_in_session=1332770&pcc=0&dload=2944&sst=1779383100000&output=html&region=mobile_app&u_tz=360&client=ca-app-pub-9027478617840640&slotname=2358016080&gsb=wi&apm_app_id=1%3A849245294575%3Aandroid%3A17045a6282e9ba9ab4301a&gmp_app_id=1%3A849245294575%3Aandroid%3A17045a6282e9ba9ab4301a&apm_app_type=1&lite=0&app_wp_code=ca-app-pub-9027478617840640&app_code=9535506442&num_ads=1&vpt=8&vfmt=18&vst=0&sdkv=o.260480999.244410000.1&sdmax=0&dmax=1&sdki=3c4d&stbg=1&bisch=false&blev=0.41&canm=true&_mv=85141930.com.android.vending&heap_free=22457104&heap_max=201326592&heap_total=61897344&wv_count=0&advertised_mem_tier=0&avail_mem_tier=0&avail_proc_tier=0&rdps=5450&_cv=261833038&session_idl=20&eo_idl=36&eo_id_tsl=10&is_lat=false&rdidl=36&idtypel=4&blob=ABPQqLHBEbDzaQtWMSseJlfnkOyaPMN_u5QdhHxoQ8uC425y4L5wBO1eBATYQCwgSw50HRq3ZE0NheR1fr4zVEY1lgMfUtWgcibm1E5plZ94E6HD-AJ3iCGx2qErnWKsYQGpHka6RavmsU3c1u6lHUcBuqPf9bOguQlLuGsu19vtKhOgnwDCt8nY6IwhqDplTi0JmcaS1bHvvm1xa1j8im5P7AQSiANcRoR6bn84YrW2MoVMqtdNXdZee4WdP07zdXOXT6BRgEkwjX72IZLHRMfURfdHeQICGhr6vkuABquqS2lYUE8SsJWFNwCrZVfSd_1F28ORiYzRe-zuRCSBkOIUkN07JuedKWLR9jgWDDofDrRCwHJY_cLhF_j10v3O9UtVshqI8k8m7MM2hBh3IgP7YonAtxWLkc-McQLGnC0OaxOA_9Ww4pj5DATlnw&capsbf=7FFFFFEE&mr_itag=479230527180312686_247~-438303185308675417_140~3508701495985525049_140_247~4509016882487189237_140~8487784177012742224_18~8661903036454621466_18~8744318498482049952_140_243~-3307436832703699534_140_247~-5315527393927264578_18~-8008616728241942675_18&jsv=sdk_20190107_RC02-production-sdk_20260514_RC00"

# লাইভ লগিং ফাংশন (গিটহাবের জন্য অপ্টিমাইজড)
def safe_log(message):
    timestamp = datetime.datetime.now().strftime('%H:%M:%S')
    log_msg = f"[{timestamp}] {message}"
    print(log_msg, flush=True)

class AtokMultiBot:
    def __init__(self):
        self.account_list = []
        self.proxy_list = []

    def load_files(self):
        # Accounts.txt থেকে UserID | Email রিড করা
        if not os.path.exists(ATOK_FILE_NAME):
            safe_log(f"❌ Error: {ATOK_FILE_NAME} ফাইলটি পাওয়া যায়নি!")
            return False
            
        with open(ATOK_FILE_NAME, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or "|" not in line: 
                    continue
                
                parts = line.split("|")
                if len(parts) >= 2:
                    uid = parts[0].strip()
                    email = parts[1].strip()
                    
                    if uid and email:
                        self.account_list.append({"email": email, "uid": uid})
        
        # Proxies.txt রিড করা (Format: IP:PORT:USER:PASS)
        if os.path.exists(PROXY_FILE_NAME):
            with open(PROXY_FILE_NAME, "r") as f:
                for line in f:
                    p = line.strip().split(":")
                    if len(p) == 4:
                        u = f"http://{p[2]}:{p[3]}@{p[0]}:{p[1]}"
                        self.proxy_list.append({"http": u, "https": u})

        safe_log(f"✅ সিস্টেম রেডি! {len(self.account_list)} টি একাউন্ট পাওয়া গেছে।")
        if self.proxy_list:
            safe_log(f"🌐 {len(self.proxy_list)} টি প্রক্সি লোড করা হয়েছে।")
        return len(self.account_list) > 0

    def get_atok_data(self, uid):
        now = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f")
        data = {"key": f"{uid}{now}", "type": "MISSION_AD", "missionType": "VIDEO"}
        return urllib.parse.quote(json.dumps(data))

    def worker(self, uid, email, state):
        session = requests.Session()
        headers = {
            'User-Agent': 'Mozilla/5.0 (Linux; Android 15; sdk_gphone64_x86_64 Build/AE3A.240806.036; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/147.0.7727.138 Mobile Safari/537.36 (Mobile; afma-sdk-a-v261833038.261833038.0)',
            'X-Requested-With': 'com.m2e.mobile',
            'Cookie': DEFAULT_COOKIE,
            'x-afma-drt-cookie': DRT_COOKIE,
            'x-afma-drt-v2-cookie': DRT_V2_COOKIE,
            'Accept-Encoding': 'gzip',
            'Connection': 'Keep-Alive'
        }

        while True:
            # টার্গেট পূরণ হলে থ্রেড বন্ধ করে দিবে
            with state['lock']:
                if state['count'] >= state['target']: break
            
            proxy = random.choice(self.proxy_list) if self.proxy_list else None
            
            try:
                # 1. Fetch Ad
                res = session.get(DEFAULT_AD_URL, headers=headers, proxies=proxy, timeout=20, verify=False)
                
                if res.status_code == 200:
                    data = res.json()
                    
                    try:
                        network = data['ad_networks'][0]
                        ad = network.get('ad', {})
                    except (KeyError, IndexError):
                        time.sleep(3)
                        continue

                    # Extract URLs
                    imp_url = ad.get('impression_urls', [''])[0] if ad.get('impression_urls') else ''
                    start_url = network.get('video_start_urls', [''])[0] if network.get('video_start_urls') else ''
                    complete_url = network.get('video_complete_urls', [''])[0] if network.get('video_complete_urls') else ''
                    reward_url = network.get('video_reward_urls', [''])[0] if network.get('video_reward_urls') else ''

                    # 2. Ping Impression
                    if imp_url:
                        session.get(imp_url, headers=headers, proxies=proxy, verify=False, timeout=15)
                    
                    # 3. Ping Start
                    if start_url:
                        session.get(start_url, headers=headers, proxies=proxy, verify=False, timeout=15)
                    
                    # 4. Wait for Video (ভিডিও দেখার সময়)
                    time.sleep(random.randint(17, 21))
                    
                    # 5. Ping Complete
                    if complete_url:
                        session.get(complete_url, headers=headers, proxies=proxy, verify=False, timeout=15)

                    # 6. Claim Reward
                    if reward_url:
                        ts = str(int(time.time() * 1000))
                        cdata = self.get_atok_data(uid)
                        claim_url = reward_url.replace("@gw_rwd_userid@", uid).replace("@gw_tmstmp@", ts).replace("@gw_rwd_custom_data@", cdata)
                        
                        claim_res = session.get(claim_url, headers=headers, proxies=proxy, verify=False, timeout=15)
                        
                        if claim_res.status_code == 200:
                            with state['lock']:
                                if state['count'] < state['target']:
                                    state['count'] += 1
                                    # গিটহাবে স্প্যাম কমানোর জন্য প্রতি ১০টা রিওয়ার্ড পরপর মেসেজ দিবে
                                    if state['count'] % 50 == 0 or state['count'] == state['target']:
                                        safe_log(f"⚡ [অ্যাক্টিভ] {email}: {state['count']}/{state['target']} রিওয়ার্ড সম্পন্ন।")

            except Exception as e:
                # নেটওয়ার্ক এরর হলে কিছুক্ষণ অপেক্ষা করে আবার চেষ্টা করবে
                time.sleep(3)
                
            time.sleep(random.randint(2, 4))

    def process_account(self, acc):
        # টার্গেট লিমিট সামান্য রেন্ডমাইজ করা হলো অ্যান্টি-ব্যানের জন্য
        variance = max(1, int(BASE_LIMIT * 0.10))
        target = BASE_LIMIT + random.randint(-variance, variance)
        
        state = {'count': 0, 'target': target, 'lock': threading.Lock()}
        safe_log(f"▶️ একাউন্ট শুরু: {acc['email']} | টার্গেট: {target}")
        
        threads = []
        for _ in range(BOTS_PER_ACCOUNT):
            t = threading.Thread(target=self.worker, args=(acc['uid'], acc['email'], state))
            t.start()
            threads.append(t)
        
        # একাউন্টের সব বটের কাজ শেষ হওয়া পর্যন্ত অপেক্ষা করবে
        for t in threads: 
            t.join()
            
        safe_log(f"✅ একাউন্ট সম্পন্ন: {acc['email']} | মোট ক্লেইম: {state['count']}")

    def start_loop(self):
        cycle = 1
        while True:
            try:
                safe_log(f"\n{'='*40}\n🚀 সাইকেল শুরু: {cycle}\n{'='*40}")
                
                # অ্যান্টি-ব্যানের জন্য লিস্ট এলোমেলো করে নেওয়া হলো
                accounts = self.account_list.copy()
                random.shuffle(accounts)
                
                # সম্পূর্ণ লিস্টের কাজ শেষ না হওয়া পর্যন্ত এই লুপ চলবে
                for i in range(0, len(accounts), CONCURRENT_ACCOUNTS):
                    batch = accounts[i:i + CONCURRENT_ACCOUNTS]
                    batch_threads = []
                    
                    for acc in batch:
                        t = threading.Thread(target=self.process_account, args=(acc,))
                        t.start()
                        batch_threads.append(t)
                    
                    # ব্যাচের সব একাউন্টের কাজ শেষ হওয়া পর্যন্ত অপেক্ষা করবে
                    for t in batch_threads: 
                        t.join()
                
                safe_log(f"🏁 সাইকেল {cycle} শেষ। লিস্টের সব একাউন্টে কাজ সম্পন্ন হয়েছে।")
                safe_log("⏳ ৫ মিনিট বিরতির পর নতুন সাইকেল শুরু হবে...")
                time.sleep(300) # ৫ মিনিটের বিরতি
                cycle += 1
                
            except Exception as e:
                safe_log(f"⚠️ সাইকেলে সমস্যা হয়েছে: {e}")
                time.sleep(15) # সমস্যা হলে 15 সেকেন্ড পর আবার ট্রাই করবে

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
