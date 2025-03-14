import cv2
import numpy as np
from PIL import Image, ImageEnhance
from io import BytesIO
from django.core.files.base import ContentFile
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.shortcuts import render
from .forms import VideoUploadForm
from django.contrib.auth.decorators import login_required

# Denoise a frame
def apply_denoising(frame):
    return cv2.bilateralFilter(frame, d=9, sigmaColor=75, sigmaSpace=75)

# Sharpen a frame using Unsharp Masking
def apply_sharpening(frame):
    kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]], dtype=np.float32)
    return cv2.filter2D(frame, -1, kernel)

# Adjust contrast and brightness of a frame
def adjust_contrast_brightness(frame, contrast=1.5, brightness=7):
    return cv2.convertScaleAbs(frame, alpha=contrast, beta=brightness)

# Enhance color saturation of a frame
def enhance_color(frame):
    pil_image = Image.fromarray(frame)
    enhancer = ImageEnhance.Color(pil_image)
    enhanced_image = enhancer.enhance(1.2)  # Increase saturation by 50%
    return np.array(enhanced_image)

# Upscale a frame using interpolation
def upscale_frame(frame, scale_factor=2):
    height, width = frame.shape[:2]
    new_height, new_width = int(height * scale_factor), int(width * scale_factor)
    return cv2.resize(frame, (new_width, new_height), interpolation=cv2.INTER_LANCZOS4)

# Function to enhance frame quality
def enhance_frame_quality(frame):
    # Step 1: Upscale the frame
    frame = upscale_frame(frame, scale_factor=3)

    # Step 2: Denoise the frame (skip if the frame is too large)
    height, width = frame.shape[:2]
    if height * width <= 2000 * 2000:  # Skip denoising for very large frames
        frame = apply_denoising(frame)

    # Step 3: Sharpen the frame
    frame = apply_sharpening(frame)

    # Step 4: Adjust contrast and brightness
    frame = adjust_contrast_brightness(frame)

    # Step 5: Enhance color saturation
    frame = enhance_color(frame)

    return frame

# Function to enhance video quality
from moviepy.editor import VideoFileClip, AudioFileClip

# Function to enhance video quality
def enhance_video_quality(input_video_path, output_video_path):
    # Open the video file
    cap = cv2.VideoCapture(input_video_path)
    if not cap.isOpened():
        raise ValueError("Could not open the video file.")

    # Get video properties
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # Codec for .mp4

    # Create a temporary file for the video without audio
    temp_video_path = output_video_path.replace('.mp4', '_temp.mp4')
    out = cv2.VideoWriter(temp_video_path, fourcc, fps, (frame_width * 3, frame_height * 3))

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Convert frame from BGR to RGB (OpenCV uses BGR by default)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Enhance the frame quality
        enhanced_frame = enhance_frame_quality(frame)

        # Convert frame back to BGR for saving
        enhanced_frame = cv2.cvtColor(enhanced_frame, cv2.COLOR_RGB2BGR)

        # Write the enhanced frame to the temporary video file
        out.write(enhanced_frame)

    # Release resources
    cap.release()
    out.release()

    # Add audio from the original video to the enhanced video
    original_video = VideoFileClip(input_video_path)
    enhanced_video = VideoFileClip(temp_video_path)
    enhanced_video_with_audio = enhanced_video.set_audio(original_video.audio)
    enhanced_video_with_audio.write_videofile(output_video_path, codec='libx264', audio_codec='aac')

    # Clean up the temporary video file
    enhanced_video.close()
    original_video.close()
    import os
    os.remove(temp_video_path)


# Django view for uploading and enhancing video
@login_required
@csrf_exempt
def upload_video(request):
    if request.method == 'POST':
        form = VideoUploadForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_video = form.save(commit=False)
            uploaded_video.user = request.user  # Associate the logged-in user
            uploaded_video.save()
            print("Uploade")
            # Paths for original and enhanced videos
            input_video_path = uploaded_video.original_video.path
            output_video_path = input_video_path.replace('.mp4', '_enhanced.mp4')
            print("increasing the video quality")
            # Enhance the video quality
            enhance_video_quality(input_video_path, output_video_path)
            print("eady to go")
            # Save the enhanced video to the model
            with open(output_video_path, 'rb') as f:
                uploaded_video.high_quality_video.save(
                    f'high_quality_{uploaded_video.original_video.name}',
                    ContentFile(f.read()),
                    save=False
                )
            uploaded_video.save()

            # Return the URLs of the original and enhanced videos
            return JsonResponse({
                'original_video_url': uploaded_video.original_video.url,
                'high_quality_video_url': uploaded_video.high_quality_video.url
            })
    else:
        form = VideoUploadForm()
    return render(request, 'upload_video.html', {'form': form})