from django.conf.urls import url, include
from django.views.generic import TemplateView
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf import settings
from django.conf.urls.static import static

from rest_framework import routers
from rest_framework_jwt.views import obtain_jwt_token

from books import views
from books.views import LoginView, RegisterUsersView


router = routers.DefaultRouter()
router.register(r'books', views.BookViewSet)

urlpatterns = [
    url(r'^$', TemplateView.as_view(template_name='home.html')),
    url(r'^', include(router.urls)),
    url(r'^admin/', admin.site.urls),
    url(r'^auth/login/', LoginView.as_view(), name="auth-login"),
    url(r'^auth/register/', RegisterUsersView.as_view(), name="auth-register"),
    url(r'^api/auth/', obtain_jwt_token, name='create-token'),
]

urlpatterns += staticfiles_urlpatterns()
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
