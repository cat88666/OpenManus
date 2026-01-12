import requests
import xml.etree.ElementTree as ET

def test_wwr_rss():
    print("Testing We Work Remotely RSS...")
    url = "https://weworkremotely.com/remote-jobs.rss"
    try:
        response = requests.get(url, timeout=15)
        if response.status_code == 200:
            root = ET.fromstring(response.content)
            items = root.findall('.//item')
            print(f"WWR success: Found {len(items)} jobs in RSS.")
            
            java_jobs = []
            for item in items:
                title = item.find('title').text
                description = item.find('description').text
                if 'java' in title.lower() or 'java' in description.lower():
                    java_jobs.append(title)
            
            print(f"Found {len(java_jobs)} Java related jobs in RSS.")
            for title in java_jobs[:5]:
                print(f"- {title}")
        else:
            print(f"WWR failed with status code: {response.status_code}")
    except Exception as e:
        print(f"WWR error: {e}")

if __name__ == "__main__":
    test_wwr_rss()
