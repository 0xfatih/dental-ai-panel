from django.contrib import admin
from django.urls import path
from core import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('home/', views.index, name='index'),
    path('', views.index, name='index'),
    path('tables/', views.tables, name='tables'),
    path('charts/', views.charts, name='charts'),
    path('login/', views.login_view, name='login'),
    path('upload/', views.upload_and_predict, name='upload'),
    #path('results/', views.results, name='results'),
    path('results/<int:xray_id>/', views.results, name='results'),
    path("about/", views.about, name="about"),
    path("contact/", views.contact, name="contact"),
    path("logout/", views.logout_view, name="logout"),
    path("register/", views.register_view, name="register"),
    path("privacy/", views.privacy, name="privacy"),
    path("terms/", views.terms, name="terms"),
    path("yolov11/", views.yolov11, name="yolov11"),
    path("results/<int:xray_id>/pdf/", views.results_pdf, name="results_pdf"),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
#Yüklenen dosyaların (resim, röntgen, pdf vs.) tarayıcıda açılmasını sağlar.

