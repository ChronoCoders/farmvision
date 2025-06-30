from django.urls import path, re_path

from . import views
app_name = 'detection'



urlpatterns = [
   
    path('index', views.index, name='index'),
    path('mcti', views.multi_detection_image, name='multi_detection_image'),
    path('leafdetection', views.leaf_detection_image, name='leaf_detection_image'),
    #path('download/<path>', views.download, name='download'),
    path('', views.index, name='index'),      
    re_path('download_image/(?P<slug>[\w-]+)', views.download_image, name='download_image'),
]

