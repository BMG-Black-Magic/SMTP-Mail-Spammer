import smtplib
import time
import os
import secrets
import re
import sys
from tqdm import tqdm
from threading import Thread
from email.mime.text import MIMEText
from dotenv import load_dotenv

load_dotenv()

HIVE_SERVER = os.getenv('HIVE_SERVER')
NECTAR_PORT = int(os.getenv('NECTAR_PORT'))
WORKER_BEE_EMAIL = os.getenv('WORKER_BEE_EMAIL')
HONEY_PASSWORD = os.getenv('HONEY_PASSWORD')
QUEEN_BEE_EMAIL = os.getenv('QUEEN_BEE_EMAIL')
HONEYCOMB_FILE = os.getenv('HONEYCOMB_FILE', "Bee.txt")
POLLEN_DELAY = int(os.getenv('POLLEN_DELAY', 1))  # Seconds between emails
BATCH_SIZE = int(os.getenv('BATCH_SIZE', 400))   # Emails per connection session
MAX_RETRIES = int(os.getenv('MAX_RETRIES', 3))    # Connection attempts per batch

def harvest_honey_lines(script_text):
    lines = script_text.split("\n")
    honey_jar = []
    current_bee = None
    for line in lines:
        line = line.strip()
        if line.startswith("(") and line.endswith(")"):
            continue
        if re.match(r"^[A-Z\s]+:$", line):
            current_bee = line[:-1].strip()
        elif current_bee and line and line != ":":
            honey_jar.append(f"🐝 {current_bee}: {line}")
    return honey_jar

def create_hive_connection():
    hive = smtplib.SMTP(HIVE_SERVER, NECTAR_PORT)
    hive.starttls()
    hive.login(WORKER_BEE_EMAIL, HONEY_PASSWORD)
    return hive

def deliver_pollen(honey_jar):
    total_nectar = len(honey_jar)
    print(f"\n🍯 Preparing {total_nectar} honey drops in batches...")
    
    for batch_num, batch_start in enumerate(range(0, total_nectar, BATCH_SIZE), 1):
        batch = honey_jar[batch_start:batch_start + BATCH_SIZE]
        success = False
        retry_count = 0
        
        while not success and retry_count < MAX_RETRIES:
            try:
                with create_hive_connection() as hive:
                    with tqdm(total=len(batch), desc=f"🌸 Batch {batch_num}", unit="msg", 
                            bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]") as bar:
                        
                        for nectar in batch:
                            msg = MIMEText(nectar, _charset='utf-8')
                            msg['Subject'] = f"BzzMail [{os.urandom(2).hex()}] {int(time.time())}"
                            msg['From'] = f"worker.{secrets.token_hex(2)}@{HIVE_SERVER.split('.')[0]}.bee"
                            msg['To'] = QUEEN_BEE_EMAIL
                            
                            hive.sendmail(WORKER_BEE_EMAIL, QUEEN_BEE_EMAIL, msg.as_string())
                            bar.update(1)
                            time.sleep(POLLEN_DELAY)
                    
                    success = True
                    print(f"✓ Batch {batch_num} delivered to hive!")
                    
            except (smtplib.SMTPServerDisconnected, smtplib.SMTPResponseException) as e:
                print(f"\n🔥 Hive disruption: {str(e)[:100]}")
                retry_count += 1
                wait_time = 10 * retry_count
                print(f"🔄 Retry {retry_count}/{MAX_RETRIES} in {wait_time}s...")
                time.sleep(wait_time)
                
            except Exception as e:
                print(f"\n❌ Critical hive failure: {str(e)[:100]}")
                time.sleep(30)
                break

        if not success:
            print(f"☠️ Permanent failure on batch {batch_num} after {MAX_RETRIES} attempts")
            return False
    
    return True

def buzz_cycle():
    try:
        with open(HONEYCOMB_FILE, "r", encoding="utf-8") as file:
            script_text = file.read().strip()
        
        honey_jar = harvest_honey_lines(script_text)
        if not honey_jar:
            print("🆘 Empty hive! No nectar found.")
            return
        
        if deliver_pollen(honey_jar):
            print("\n✅ All honey stores delivered successfully!")
        else:
            print("\n⚠️ Partial delivery completed - check hive health")
            
    except FileNotFoundError:
        print(f"🆘 Missing honeycomb: {HONEYCOMB_FILE}")
    except Exception as e:
        print(f"💥 Killer hornet attack: {str(e)[:100]}")

def honey_countdown():
    print("\n\n🌸 Hive activity paused!")
    print("🐝 Press 'S' + Enter to hibernate")
    print("🌻 Auto-restart in 30 seconds...")
    
    user_input = None
    def get_input():
        nonlocal user_input
        user_input = sys.stdin.readline().strip().lower()
    
    input_thread = Thread(target=get_input)
    input_thread.daemon = True
    input_thread.start()

    for t in range(30, 0, -1):
        print(f"🕒 Next pollination swarm in {t}s...", end='\r')
        time.sleep(1)
        if not input_thread.is_alive():
            break

    if user_input == 's':
        print("\n\n🐻❄️ Entering honey-sleep forever...")
        return False
    print("\n\n🌼 New pollen wave incoming!")
    return True

if __name__ == "__main__":
    print("""\
    
    🐝🚀 BzzMail Delivery System 2.0
    
    """)
    
    while True:
        buzz_cycle()
        if not honey_countdown():
            break
            
    print("🐋 Farewell, much love from qmvt...")