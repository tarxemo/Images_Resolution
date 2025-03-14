import cv2
import numpy as np
from PIL import Image, ImageEnhance
from skimage import restoration

# Denoise the image using Non-Local Means (optimized parameters)
def apply_denoising(image):
    # Use smaller patch_size and patch_distance for faster processing
    return restoration.denoise_nl_means(image, patch_size=5, patch_distance=3, h=0.1, fast_mode=True)

# Sharpen the image using Unsharp Masking
def apply_sharpening(image):
    kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]], dtype=np.float32)
    return cv2.filter2D(image, -1, kernel)

# Adjust contrast and brightness
def adjust_contrast_brightness(image, contrast=1.5, brightness=10):
    return cv2.convertScaleAbs(image, alpha=contrast, beta=brightness)

# Enhance color saturation
def enhance_color(image):
    pil_image = Image.fromarray(image)
    enhancer = ImageEnhance.Color(pil_image)
    enhanced_image = enhancer.enhance(1.5)  # Increase saturation by 50%
    return np.array(enhanced_image)

# Upscale the image using interpolation
def upscale_image(image, scale_factor=2):
    height, width = image.shape[:2]
    new_height, new_width = int(height * scale_factor), int(width * scale_factor)
    return cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_LANCZOS4)

# Main function to enhance image quality
def enhance_image_quality(image_path, output_path, scale_factor=2):
    # Load the image
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError("Image not found or unable to load.")

    # Convert to RGB (OpenCV loads images in BGR format)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # Step 1: Upscale the image
    print("Upscaling the image...")
    image = upscale_image(image, scale_factor)

    # Step 2: Denoise the image (skip if the image is too large)
    print("Applying denoising...")
    height, width = image.shape[:2]
    # if height * width > 2000 * 2000:  # Skip denoising for very large images
    #     print("Image is too large for denoising. Skipping this step.")
    # else:
    #     image = apply_denoising(image)

    # Step 3: Sharpen the image
    print("Applying sharpening...")
    # image = apply_sharpening(image)

    # Step 4: Adjust contrast and brightness
    print("Adjusting contrast and brightness...")
    image = adjust_contrast_brightness(image)

    # Step 5: Enhance color saturation
    print("Enhancing color...")
    image = enhance_color(image)

    # Save the enhanced image
    enhanced_image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    cv2.imwrite(output_path, enhanced_image)
    print(f"Enhanced image saved to {output_path}")

# Example usage
if __name__ == "__main__":
    input_image_path = "test/manyara1.jpeg"  # Replace with your input image path
    output_image_path = "enhanced_image.jpeg"  # Replace with your desired output path

    enhance_image_quality(input_image_path, output_image_path, scale_factor=2)