"""ImageProcessing URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
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
from django.urls import path,include
from ImageProcessingCore.views import homepage, ImageViewSet, getOutputShares,ImageOutputsViewSet,imagePage, encryptWithKeys, cipherText,\
    decryptCipher,DecryptionViewSet,autogenKeys,keysOutput , CustomUserViewSet,signIn, sendEmail ,UserImageListViewSet, \
    sharedImages,decryptSharedImage
from rest_framework import routers
# from rest_framework_jwt.views import obtain_jwt_token



router = routers.DefaultRouter()
router.register(r'images', ImageViewSet)
router.register(r'imageoutputs', ImageOutputsViewSet)
router.register(r'cipher', DecryptionViewSet)
router.register(r'users', CustomUserViewSet)
router.register(r'emailshare', UserImageListViewSet)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', homepage, name="front"),
    path('api/', include(router.urls)),
    path('post/<str:id>/', getOutputShares, name="Shares"),
    path('outputs/<str:file>/', imagePage, name="images"),
    path('encrypt/<str:id>/', encryptWithKeys, name="encryption"),
    path('cipher/<str:id>/', cipherText, name="cipherText"),
    path('decrypt/<str:id>/', decryptCipher, name="decryption"),
    path('keygen/<str:num>/', autogenKeys, name="keygen"),
    path('keyout/<str:id>/', keysOutput, name="keysOutput"),
    path('signin/<str:email>/<str:password>/', signIn, name="signIn"),
    path('sendEmail/<str:email>/', sendEmail, name="sendEmail"),
    path('sharedimages/<str:email>/', sharedImages, name="sharedImages"),
    path('decryptshared/<str:id>/<str:counter>/', decryptSharedImage, name="decryptSharedImage"),

]
