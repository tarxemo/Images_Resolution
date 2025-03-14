from django import forms
from .models import UploadedImage, UploadedVideo

class ImageUploadForm(forms.ModelForm):
    class Meta:
        model = UploadedImage
        fields = ['original_image']


class VideoUploadForm(forms.ModelForm):
    class Meta:
        model = UploadedVideo
        fields = ['original_video']