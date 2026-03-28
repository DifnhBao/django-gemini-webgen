from django.urls import path

from . import views

app_name = 'ai_builder'

urlpatterns = [
    path('', views.DashboardView, name='dashboard'),
    path('website/<int:website_id>/', views.RenderWebsiteView, name='render_website'),
    path('website/<int:pk>/delete/', views.delete_website, name='delete_website'),
]
