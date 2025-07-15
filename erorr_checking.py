# Enhanced ELA-Based Image Forgery Detection with Features

from PIL import Image, ImageChops, ImageEnhance, ImageDraw, ImageFont
import numpy as np
import os
import datetime


def perform_ela_analysis(image_path, quality=90):
    original = Image.open(image_path).convert('RGB')
    temp_path = "temp_compressed.jpg"
    original.save(temp_path, "JPEG", quality=quality)
    compressed = Image.open(temp_path)

    diff = ImageChops.difference(original, compressed)
    extrema = diff.getextrema()
    max_diff = max([ex[1] for ex in extrema])
    scale = 255.0 / max_diff if max_diff != 0 else 1
    ela_image = ImageEnhance.Brightness(diff).enhance(scale)

    return ela_image, np.mean(np.array(diff))


def create_side_by_side(original_path, ela_image, verdict, score):
    original = Image.open(original_path).convert('RGB')
    ela_resized = ela_image.resize(original.size)
    combined = Image.new('RGB', (original.width * 2, original.height))
    combined.paste(original, (0, 0))
    combined.paste(ela_resized, (original.width, 0))

    draw = ImageDraw.Draw(combined)
    try:
        font = ImageFont.truetype("arial.ttf", 20)
    except:
        font = ImageFont.load_default()

    text = f"Result: {verdict} (ELA diff = {score:.2f})"
    draw.text((10, 10), text, fill="red" if verdict == 'FORGED' else "green", font=font)
    return combined


def is_forged(image_path, threshold=12):
    ela_img, diff_score = perform_ela_analysis(image_path)
    verdict = "FORGED" if diff_score > threshold else "ORIGINAL"

    final_image = create_side_by_side(image_path, ela_img, verdict, diff_score)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = f"ela_result_{timestamp}.jpg"
    final_image.save(output_path)

    print(f"📁 ELA result image saved: {output_path}")
    try:
        os.startfile(output_path)
    except Exception as e:
        print("⚠️ Could not auto-open image:", e)

    print(f"Result: {'⚠️ FORGED' if verdict == 'FORGED' else '✅ ORIGINAL'} (ELA diff = {diff_score:.2f})")


if __name__ == "__main__":
    print("\n🔍 Enhanced Image Forgery Detection using ELA")
    print("Enter full path to a JPEG image:")
    img_path = input(">>> ").strip()

    if not os.path.exists(img_path):
        print("❌ File not found.")
    elif not img_path.lower().endswith(('.jpg', '.jpeg')):
        print("❌ Only .jpg or .jpeg images are supported.")
    else:
        is_forged(img_path)
