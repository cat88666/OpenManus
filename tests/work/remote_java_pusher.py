import requests
import xml.etree.ElementTree as ET
import json
import os
from datetime import datetime, timedelta

# Configuration
TELEGRAM_TOKEN = "8330652586:AAEwEv1R46T6Iw3aBlGO7HUmdbzwezVrNTs"
CHAT_ID = "742831201"
SENT_JOBS_FILE = "/home/ubuntu/sent_jobs.json"

def load_sent_jobs():
    if os.path.exists(SENT_JOBS_FILE):
        with open(SENT_JOBS_FILE, 'r') as f:
            return set(json.load(f))
    return set()

def save_sent_jobs(sent_jobs):
    with open(SENT_JOBS_FILE, 'w') as f:
        json.dump(list(sent_jobs), f)

def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "Markdown"
    }
    try:
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print(f"Error sending message: {e}")

def fetch_remotive():
    jobs = []
    url = "https://remotive.com/api/remote-jobs?search=java"
    try:
        response = requests.get(url, timeout=15)
        if response.status_code == 200:
            data = response.json()
            for job in data.get('jobs', []):
                title = job.get('title', '')
                if any(word in title.lower() for word in ['senior', 'lead', 'staff', 'principal', 'sr.', '10+']):
                    jobs.append({
                        'id': f"remotive_{job['id']}",
                        'title': title,
                        'company': job.get('company_name'),
                        'location': job.get('candidate_required_location', 'Worldwide'),
                        'url': job.get('url'),
                        'source': 'Remotive'
                    })
    except:
        pass
    return jobs

def fetch_wwr():
    jobs = []
    url = "https://weworkremotely.com/remote-jobs.rss"
    try:
        response = requests.get(url, timeout=15)
        if response.status_code == 200:
            root = ET.fromstring(response.content)
            for item in root.findall('.//item'):
                title = item.find('title').text
                desc = item.find('description').text
                link = item.find('link').text
                if 'java' in title.lower() or 'java' in desc.lower():
                    if any(word in title.lower() for word in ['senior', 'lead', 'staff', 'principal', 'sr.', '10+']):
                        jobs.append({
                            'id': f"wwr_{link}",
                            'title': title,
                            'company': 'WWR',
                            'location': 'Remote',
                            'url': link,
                            'source': 'We Work Remotely'
                        })
    except:
        pass
    return jobs

def fetch_remoteok():
    jobs = []
    url = "https://remoteok.com/api"
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code == 200:
            data = response.json()
            for job in data[1:]:
                title = job.get('position', '')
                desc = job.get('description', '')
                if 'java' in title.lower() or 'java' in desc.lower():
                    if any(word in title.lower() for word in ['senior', 'lead', 'staff', 'principal', 'sr.', '10+']):
                        jobs.append({
                            'id': f"remoteok_{job.get('id')}",
                            'title': title,
                            'company': job.get('company'),
                            'location': job.get('location', 'Remote'),
                            'url': f"https://remoteok.com/remote-jobs/{job.get('id')}",
                            'source': 'Remote OK'
                        })
    except:
        pass
    return jobs

def main():
    sent_jobs = load_sent_jobs()
    all_jobs = fetch_remotive() + fetch_wwr() + fetch_remoteok()
    
    new_jobs = [j for j in all_jobs if j['id'] not in sent_jobs]
    
    if not new_jobs:
        print("No new jobs found.")
        return

    message = "*🚀 每日远程 Java 资深岗位推送*\n\n"
    for job in new_jobs[:10]: # Limit to 10 per message to avoid length issues
        message += f"📍 *{job['title']}*\n"
        message += f"🏢 公司: {job['company']}\n"
        message += f"🌍 地区: {job['location']}\n"
        message += f"🔗 [查看详情]({job['url']})\n"
        message += f"📦 来源: {job['source']}\n\n"
        sent_jobs.add(job['id'])
    
    send_telegram_message(message)
    save_sent_jobs(sent_jobs)
    print(f"Sent {len(new_jobs[:10])} new jobs.")

if __name__ == "__main__":
    main()
