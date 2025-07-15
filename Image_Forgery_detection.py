from PIL import Image, ImageChops, ImageEnhance
import numpy as np
import os

def perform_ela_analysis(image_path, quality=90):
    # Step 1: Open original image
    original = Image.open(image_path).convert('RGB')

    # Step 2: Save compressed copy
    temp_path = "temp_compressed.jpg"
    original.save(temp_path, "JPEG", quality=quality)

    # Step 3: Open compressed image
    compressed = Image.open(temp_path)

    # Step 4: Get pixel-wise difference
    diff = ImageChops.difference(original, compressed)

    # Step 5: Enhance brightness for visibility
    extrema = diff.getextrema()
    max_diff = max([ex[1] for ex in extrema])
    scale = 255.0 / max_diff if max_diff != 0 else 1
    ela_image = ImageEnhance.Brightness(diff).enhance(scale)

    return ela_image, np.mean(np.array(diff))


def is_forged(image_path, threshold=12):
    ela_img, diff_score = perform_ela_analysis(image_path)

    # Save ELA result image
    output_path = "ela_result.jpg"
    ela_img.save(output_path)
    print(f"📁 ELA image saved as: {output_path}")

    # Try to auto-open image on Windows
    try:
        os.startfile(output_path)  # Only works on Windows
    except Exception as e:
        print("⚠️ Could not auto-open image:", e)

    # Print result
    if diff_score > threshold:
        print(f"⚠️ Image is likely FORGED (ELA diff = {diff_score:.2f})")
    else:
        print(f"✅ Image appears to be ORIGINAL (ELA diff = {diff_score:.2f})")


if __name__ == "__main__":
    print("🔍 Image Forgery Detection using ELA")
    print("Enter full path to JPEG image:")
    img_path = input(">>> ").strip()

    if not os.path.exists(img_path):
        print("❌ File not found.")
    elif not img_path.lower().endswith(('.jpg', '.jpeg')):
        print("❌ Please provide a .jpg or .jpeg image.")
    else:
        is_forged(img_path)
