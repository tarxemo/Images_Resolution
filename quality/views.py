from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from .forms import ImageUploadForm
from .models import *
from io import BytesIO
from django.core.files.base import ContentFile
from django.views.decorators.csrf import csrf_exempt
from PIL import Image, ImageEnhance
import cv2
import numpy as np
from skimage import restoration
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

# Create your views here.
def index(request):
    return render(request, 'index.html')

@login_required
def home_view(request):
    # Fetch the logged-in user's uploaded images
    images = UploadedImage.objects.filter(user=request.user)
    return render(request, 'home.html', {'images': images})

@login_required
def video_home_view(request):
    # Fetch the logged-in user's uploaded images
    videos = UploadedVideo.objects.filter(user=request.user)
    return render(request, 'video_home.html', {'videos': videos})


def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        if password1 != password2:
            messages.error(request, 'Passwords do not match.')
        elif User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
        elif User.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists.')
        else:
            user = User.objects.create_user(username=username, email=email, password=password1)
            user.save()
            messages.success(request, 'Account created successfully. Please login.')
            return redirect('login')
    return render(request, 'register.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, 'Login successfully!!!!!!!!!!.')
            return redirect('home')
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'login.html')


@login_required
def logout_view(request):
    logout(request)
    messages.info(request, 'Logout successfully!.')
    return redirect('login')



def apply_denoising(image):
    return cv2.bilateralFilter(image, d=9, sigmaColor=75, sigmaSpace=75)


# Sharpen the image using Unsharp Masking
def apply_sharpening(image):
    kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]], dtype=np.float32)
    return cv2.filter2D(image, -1, kernel)

# Adjust contrast and brightness
def adjust_contrast_brightness(image, contrast=1.5, brightness=7):
    return cv2.convertScaleAbs(image, alpha=contrast, beta=brightness)

# Enhance color saturation
def enhance_color(image):
    pil_image = Image.fromarray(image)
    enhancer = ImageEnhance.Color(pil_image)
    enhanced_image = enhancer.enhance(1.2)  # Increase saturation by 50%
    return np.array(enhanced_image)

# Upscale the image using interpolation
def upscale_image(image, scale_factor=2):
    height, width = image.shape[:2]
    new_height, new_width = int(height * scale_factor), int(width * scale_factor)
    return cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_LANCZOS4)

# Function to enhance image quality
def enhance_image_quality(image):
    # Convert PIL Image to OpenCV format
    image = np.array(image)
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

    # Step 1: Upscale the image
    print("Upscaling the image...")
    image = upscale_image(image, scale_factor=3)

    # Step 2: Denoise the image (skip if the image is too large)
    print("Applying denoising...")
    height, width = image.shape[:2]
    if height * width > 2000 * 2000:  # Skip denoising for very large images
        print("Image is too large for denoising. Skipping this step.")
    else:
        image = apply_denoising(image)

    # Step 3: Sharpen the image
    print("Applying sharpening...")
    image = apply_sharpening(image)

    # Step 4: Adjust contrast and brightness
    print("Adjusting contrast and brightness...")
    image = adjust_contrast_brightness(image)

    # Step 5: Enhance color saturation
    print("Enhancing color...")
    image = enhance_color(image)

    # Convert back to PIL Image
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    return Image.fromarray(image)

@login_required
@csrf_exempt
def upload_image(request):
    if request.method == 'POST':
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_image = form.save(commit=False)
            uploaded_image.user = request.user  # Associate the logged-in user
            uploaded_image.save()

            # Open the uploaded image
            img = Image.open(uploaded_image.original_image)
            img = img.convert('RGB')

            # Enhance the image quality
            enhanced_img = enhance_image_quality(img)

            # Save the enhanced image to a BytesIO object
            output = BytesIO()
            enhanced_img.save(output, format='JPEG', quality=95)
            output.seek(0)

            # Save the enhanced image to the model
            uploaded_image.high_quality_image.save(
                f'high_quality_{uploaded_image.original_image.name}',
                ContentFile(output.read()),
                save=False
            )
            uploaded_image.save()

            # Return the URLs of the original and enhanced images
            return JsonResponse({
                'original_image_url': uploaded_image.original_image.url,
                'high_quality_image_url': uploaded_image.high_quality_image.url
            })
    else:
        form = ImageUploadForm()
    return render(request, 'upload.html', {'form': form})


@login_required
def delete_image(request, image_id):
    if request.method == 'POST':
        image = get_object_or_404(UploadedImage, id=image_id)
        image.delete()
        messages.success(request, 'Image deleted successfully.')
    return redirect('home')


@login_required
def delete_video(request, video_id):
    if request.method == 'POST':
        video = get_object_or_404(UploadedVideo, id=video_id)
        video.delete()
        messages.success(request, 'Video deleted successfully.')
    return redirect('video_home_view')