"""rest_api_project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
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
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls import url, include
from rest_framework import routers
from rest_framework_jwt.views import obtain_jwt_token, refresh_jwt_token
from rest_api_app import views


router = routers.DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'groups', views.GroupViewSet)


router.register(r'menu_name', views.MenuNameViewSet)
router.register(r'training_program', views.TrainingProgramViewSet)
router.register(r'training_menu', views.TrainingMenuViewSet)
router.register(r'result_time', views.ResultTimeViewSet)
router.register(r'lap_time', views.LapTimeViewSet)
router.register(r'profile', views.ProfileViewSet)
# router.register(r'profile', profile_list, basename="profile")
# router.register(r'test', views.test)

urlpatterns = [
    path('adminsite/', admin.site.urls),
    url(r'^', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('auth/', obtain_jwt_token),
    path('logout/', refresh_jwt_token),
    path('datainput/', views.DataInput, name='datainput'),
    path('schoolsname/', views.SchoolsName, name='schoolsname'),
    path('graphandtabledata/', views.GraphAndTableData, name='graphandtabledata'),
    path('login_user/', views.LoginUser),
    path('test_func/', views.test_func),
    # path('logout/', views.Logout.as_view()),
    # path(r'profile', profile_list)
]

# if settings.DEBUG:
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# if settings.DEBUG:
if 'silk' in settings.INSTALLED_APPS:
    urlpatterns += [path('silk/', include('silk.urls', namespace='silk'))]
