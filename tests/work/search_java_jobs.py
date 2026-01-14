import requests
import json

def search_remotive(query):
    url = f"https://remotive.com/api/remote-jobs?search={query}"
    try:
        response = requests.get(url, timeout=15)
        if response.status_code == 200:
            return response.json().get('jobs', [])
    except:
        pass
    return []

def main():
    queries = ["java", "spring boot", "backend"]
    all_jobs = []
    seen_ids = set()

    for q in queries:
        print(f"Searching Remotive for: {q}")
        jobs = search_remotive(q)
        for job in jobs:
            if job['id'] not in seen_ids:
                # Filter for 10 years experience or senior roles
                title = job.get('title', '').lower()
                desc = job.get('description', '').lower()
                if 'java' in title or 'java' in desc:
                    if any(word in title for word in ['senior', 'lead', 'staff', 'principal', 'sr.']):
                        all_jobs.append(job)
                        seen_ids.add(job['id'])
    
    print(f"\nFound {len(all_jobs)} senior Java related remote jobs on Remotive.")
    for job in all_jobs[:10]:
        print(f"[{job.get('publication_date')}] {job.get('title')} @ {job.get('company_name')}")
        print(f"Location: {job.get('candidate_required_location')} | URL: {job.get('url')}\n")

if __name__ == "__main__":
    main()
