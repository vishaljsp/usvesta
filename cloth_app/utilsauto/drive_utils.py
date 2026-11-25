import re
import requests
from django.core.files.base import ContentFile


def get_drive_image(image_url):
    try:
        if not image_url:
            return None

        image_url = str(image_url).strip()
        if "drive.google.com" not in image_url:
            return None

        match = re.search(r"/d/([^/]+)", image_url)
        if not match:
            return None

        file_id = match.group(1)
        download_url = f"https://drive.google.com/uc?export=download&id={file_id}"

        r = requests.get(download_url, timeout=30)

        # 🔥 IMPORTANT: NO content-type check
        if r.status_code == 200:
            return ContentFile(r.content, name=f"{file_id}.jpg")

    except Exception as e:
        print("Drive image error:", e)

    return None
