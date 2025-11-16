# 📸🎬 Django Image & Video Enhancement System

A full-stack **Django application** that allows users to register, upload images and videos, and automatically enhance their quality using **OpenCV**, **PIL**, **MoviePy**, and **NumPy**.
The system supports:

* User authentication (register, login, logout)
* Image enhancement (upscaling, denoising, sharpening, color boost)
* Video enhancement (frame-by-frame processing + audio preservation)
* Media management (upload, list, delete)
* Per-user image & video library

This README explains the setup, features, project structure, and usage.

---

## 🚀 Features

### 🔐 Authentication

* User registration
* Login & logout
* Login-required protection for media pages

### 📸 Image Enhancement Pipeline

Every image uploaded goes through:

1. **Upscaling** (×3 using Lanczos interpolation)
2. **Denoising** (Bilateral filter)
3. **Sharpening** (Unsharp mask)
4. **Contrast & brightness adjustment**
5. **Color saturation enhancement**
6. Saves both **original** & **high-quality** versions

### 🎬 Video Enhancement Pipeline

Each frame is processed using the following:

1. **Upscaling** (×3)
2. **Denoising** for small frames
3. **Sharpening**
4. **Brightness & contrast improvement**
5. **Color enhancement**
6. **Audio preserved** using MoviePy

### 📁 User Media Dashboard

* List all your images
* List all your videos
* View enhanced results
* Delete media

---

## 📦 Tech Stack

| Area             | Technology                                 |
| ---------------- | ------------------------------------------ |
| Backend          | Django                                     |
| Media Processing | OpenCV, Pillow, NumPy, MoviePy             |
| Frontend         | HTML, CSS, JavaScript (AJAX JSON response) |
| Database         | SQLite / PostgreSQL                        |
| Authentication   | Django Auth System                         |

---

## 📂 Project Structure (Relevant Parts)

```
your_project/
│
├── media/                  # Stores uploaded and enhanced media
│
├── app_name/
│   ├── models.py           # UploadedImage & UploadedVideo models
│   ├── views.py            # (Your provided code)
│   ├── forms.py
│   ├── urls.py
│   ├── templates/
│       ├── index.html
│       ├── login.html
│       ├── register.html
│       ├── home.html
│       ├── video_home.html
│       ├── upload.html
│       ├── upload_video.html
│
└── requirements.txt
```

---

## ⚙️ Installation & Setup

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/yourrepo.git
cd yourrepo
```

### 2. Create and Activate Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

Required packages include:

```
Django
opencv-python
pillow
numpy
moviepy
scikit-image
```

### 4. Apply Migrations

```bash
python manage.py migrate
```

### 5. Create Superuser (optional)

```bash
python manage.py createsuperuser
```

### 6. Run Development Server

```bash
python manage.py runserver
```

Visit:

```
http://127.0.0.1:8000/
```

---

## 🖼️ Image Enhancement Flow

When a user uploads an image:

1. Stored temporarily
2. Enhanced using:

```python
upscale_image(image, scale_factor=3)
apply_denoising(image)
apply_sharpening(image)
adjust_contrast_brightness(image)
enhance_color(image)
```

3. Saved as:

   ```
   original_image.jpg
   high_quality_original_image.jpg
   ```

4. Returns JSON:

```json
{
  "original_image_url": "...",
  "high_quality_image_url": "..."
}
```

---

## 🎬 Video Enhancement Flow

Video is processed frame by frame:

1. Extract each frame with OpenCV
2. Enhance with same pipeline as images
3. Save enhanced video (temporary)
4. Add original audio using MoviePy
5. Save as:

```
original.mp4
high_quality_original.mp4
```

---

## 🔧 API Endpoints

### Image Endpoints

| URL                   | Method | Description            |
| --------------------- | ------ | ---------------------- |
| `/upload/`            | POST   | Upload & enhance image |
| `/home/`              | GET    | List user images       |
| `/delete-image/<id>/` | POST   | Delete image           |

### Video Endpoints

| URL                   | Method | Description            |
| --------------------- | ------ | ---------------------- |
| `/upload-video/`      | POST   | Upload & enhance video |
| `/video-home/`        | GET    | List user videos       |
| `/delete-video/<id>/` | POST   | Delete video           |

### Authentication

| URL          | Description    |
| ------------ | -------------- |
| `/register/` | Create account |
| `/login/`    | Login          |
| `/logout/`   | Logout         |

---

## 💾 Models Summary

### `UploadedImage`

* `user`
* `original_image`
* `high_quality_image`
* `uploaded_at`

### `UploadedVideo`

* `user`
* `original_video`
* `high_quality_video`
* `uploaded_at`

---

## 🛡️ Authentication & Security

* Uses Django built-in auth system
* CSRF protection enabled except AJAX upload
* Access to images/videos is user-restricted

---

## 🔮 Future Improvements (Optional)

* Add progress bar during enhancement
* Support batch processing
* Integrate WebSockets for real-time progress updates
* Add AI-based super resolution (ESRGAN)

---

## 📜 License

MIT License — free to use, modify, and distribute.

---
