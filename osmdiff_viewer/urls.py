"""osmdiff_viewer URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
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
from django.urls import path

from osm_sniffer import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('<int:diff_id>/', views.index, name='index'),
    path('<int:diff_id>/map/', views.map_view, name='map_view'),
    path('<int:diff_id>/map_almostover/', views.almostover_map_view, name='map_view')
]
