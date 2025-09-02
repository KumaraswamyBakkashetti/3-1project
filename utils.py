# utils.py
import time
import google.api_core.exceptions

def safe_score(judge, content):
    while True:
        try:
            return judge.score(content)
        except google.api_core.exceptions.ResourceExhausted:
            print("⚠️ Rate limit hit. Waiting 60s...")
            time.sleep(60)
