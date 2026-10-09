import os
import urllib.request

def download():
    os.makedirs("videos", exist_ok=True)
    target_path = "videos/sample_traffic.mp4"

    # Direct CDN link to open-source traffic video
    url = "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/SubaruOutbackOnStreetAndDirt.mp4"

    print(f"[Download] Fetching real highway car video...")
    headers = {'User-Agent': 'Mozilla/5.0'}
    req = urllib.request.Request(url, headers=headers)
    
    with urllib.request.urlopen(req) as response, open(target_path, 'wb') as out_file:
        data = response.read()
        out_file.write(data)
    
    size_mb = os.path.getsize(target_path) / (1024 * 1024)
    print(f"[SUCCESS] Video saved: {target_path} ({size_mb:.2f} MB)")

if __name__ == "__main__":
    download()
    