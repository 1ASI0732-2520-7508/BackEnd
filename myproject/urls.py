# project_name/urls.py
from django.contrib import admin
from django.urls import path, include
// coment 
urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('myapp.urls')), # Include your app's URLs
]
