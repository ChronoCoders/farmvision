from django.urls import path, re_path

from . import views
app_name = 'dron_map'



urlpatterns = [
       
    path('projects', views.projects, name='projects'),     
    re_path(r'projects/(?P<slug>[\w-]+)/(?:id-(?P<id>[0-9]+)/)?$', views.add_projects, name='add_projects'),
    re_path(r'map/(?:id-(?P<id>[0-9]+)/)?$', views.maping, name='map'),
    
]

