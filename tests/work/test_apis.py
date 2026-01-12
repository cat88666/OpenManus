import requests
import json

def test_remotive():
    print("Testing Remotive API...")
    url = "https://remotive.com/api/remote-jobs?search=java&limit=5"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"Remotive success: Found {data.get('job-count', 0)} jobs.")
            for job in data.get('jobs', []):
                print(f"- {job.get('title')} at {job.get('company_name')}")
        else:
            print(f"Remotive failed with status code: {response.status_code}")
    except Exception as e:
        print(f"Remotive error: {e}")

def test_arbeitnow():
    print("\nTesting Arbeitnow API...")
    url = "https://www.arbeitnow.com/api/job-board-api"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            jobs = data.get('data', [])
            print(f"Arbeitnow success: Found {len(jobs)} jobs in the first page.")
            # Filter for Java in the results
            java_jobs = [j for j in jobs if 'java' in j.get('title', '').lower() or 'java' in j.get('description', '').lower()]
            print(f"Found {len(java_jobs)} Java related jobs on the first page.")
            for job in java_jobs[:5]:
                print(f"- {job.get('title')} at {job.get('company_name')}")
        else:
            print(f"Arbeitnow failed with status code: {response.status_code}")
    except Exception as e:
        print(f"Arbeitnow error: {e}")

if __name__ == "__main__":
    test_remotive()
    test_arbeitnow()
