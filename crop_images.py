from PIL import Image
import os

img2_path = r"template_images/slide_2.png"
img1_path = r"template_images/slide_1.png"

if not os.path.exists(img2_path) or not os.path.exists(img1_path):
    print("Error: Background images not found.")
else:
    try:
        # Load slide 2 to extract the black header bar and bottom footer
        img2 = Image.open(img2_path)
        w, h = img2.size
        print(f"Slide image dimensions: {w}x{h}")

        # Crop header: top 1.05 inches of 7.5 inches height
        header_h = int(h * (1.05 / 7.5))
        header = img2.crop((0, 0, w, header_h))
        header.save(r"template_images/cropped_header.png")
        print("Successfully cropped header.png")

        # Crop footer: bottom 0.6 inches of 7.5 inches height
        footer_top = int(h * (6.9 / 7.5))
        footer = img2.crop((0, footer_top, w, h))
        footer.save(r"template_images/cropped_footer.png")
        print("Successfully cropped footer.png")

        # Crop Slide 1 banner: top 4.0 inches of 7.5 inches height
        img1 = Image.open(img1_path)
        banner_h = int(h * (4.0 / 7.5))
        banner = img1.crop((0, 0, w, banner_h))
        banner.save(r"template_images/cropped_banner.png")
        print("Successfully cropped banner.png")
        
    except Exception as e:
        print("Error during image cropping:", e)
