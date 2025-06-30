"""yolowebapp2 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from user_registration import views
from django.conf.urls import handler400, handler403, handler404, handler500
from django.views.decorators.csrf import requires_csrf_token
from  django.views import defaults
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),    
    path('',  include('detection.urls',namespace="index")),
    path('mcti/',  include('detection.urls',namespace="multi_detection_image")),
    path('leafdetection/',  include('detection.urls',namespace="leaf_detection_image")),
    path('user_pr/',  include('user_registration.urls',namespace="user_pr")),
    path('user_edit/',  include('user_registration.urls',namespace="user_edit")),
    path('login/', include('user_registration.urls',namespace="login")),
    path('calendar/', include('user_registration.urls',namespace="calendar")),
    path('login_view/', include('user_registration.urls',namespace="login_view")),
    path('logout/', include('user_registration.urls',namespace="logout")),
    path('signup/', include('user_registration.urls',namespace="signup")),
    path('forgot_password/', include('user_registration.urls',namespace="forgot_password")),
    path('pricing/', views.pricing, name='pricing'),
    path('map/', include('dron_map.urls',namespace="map")),
    path('projects/', include('dron_map.urls',namespace="projects")),
    path('add_projects/', include('dron_map.urls',namespace="add_projects")),
    #path('404/', include('polls.urls',namespace="page_not_founds")),
    #path('403/', include('polls.urls',namespace="permission_denieds")),
    #path('400/', include('polls.urls',namespace="bad_requests")),
    #path('500/', include('polls.urls',namespace="server_errors")),
]
