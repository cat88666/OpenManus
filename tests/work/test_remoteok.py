import requests

def test_remoteok():
    print("Testing Remote OK API...")
    # Remote OK API returns JSON
    url = "https://remoteok.com/api"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    try:
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code == 200:
            data = response.json()
            # First element is usually a legal notice or meta info
            jobs = data[1:] if isinstance(data, list) else []
            print(f"Remote OK success: Found {len(jobs)} jobs.")
            
            java_jobs = []
            for job in jobs:
                title = job.get('position', '')
                description = job.get('description', '')
                if 'java' in title.lower() or 'java' in description.lower():
                    java_jobs.append(f"{title} at {job.get('company', '')}")
            
            print(f"Found {len(java_jobs)} Java related jobs.")
            for job_info in java_jobs[:5]:
                print(f"- {job_info}")
        else:
            print(f"Remote OK failed with status code: {response.status_code}")
    except Exception as e:
        print(f"Remote OK error: {e}")

if __name__ == "__main__":
    test_remoteok()
