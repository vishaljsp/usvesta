import os
from PIL import Image

# 📁 Folder path
FOLDER_PATH = "static"

# 🎯 Settings
MAX_SIZE = 800        # max width/height
QUALITY = 80          # compression quality (0–100)
EXTENSIONS = (".png", ".jpg", ".jpeg")


def optimize_image(image_path):
    try:
        img = Image.open(image_path)

        # Convert to RGB (important for PNG transparency issues)
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")

        # Resize (maintain aspect ratio)
        img.thumbnail((MAX_SIZE, MAX_SIZE))

        # Output path
        output_path = os.path.splitext(image_path)[0] + ".webp"

        # Save as WebP
        img.save(output_path, "WEBP", quality=QUALITY, method=6)

        # Delete original file
        os.remove(image_path)

        print(f"✅ Optimized & Deleted: {image_path} → {output_path}")

    except Exception as e:
        print(f"❌ Error: {image_path} → {e}")


def process_folder(folder):
    for root, dirs, files in os.walk(folder):
        for file in files:
            if file.lower().endswith(EXTENSIONS):
                file_path = os.path.join(root, file)
                optimize_image(file_path)


if __name__ == "__main__":
    process_folder(FOLDER_PATH)