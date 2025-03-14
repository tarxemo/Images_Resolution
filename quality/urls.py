from django.urls import path
from .views import *
from .video_views import *

urlpatterns = [
    path('', index, name='index'),
    
    path('upload/', upload_image, name='upload_image'),
    path('upload_video/', upload_video, name='upload_video'),
    path('video_home_view/', video_home_view, name='video_home_view'),
    
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('register/', register_view, name='register'),
    path('home/', home_view, name='home'),
    path('delete/<int:image_id>/', delete_image, name='delete_image'),
    path('delete_video/<int:video_id>/', delete_video, name='delete_video'),

]