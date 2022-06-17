from django.contrib import admin
from .models import Core,ImageOutputs,Decryption,CustomUser, UserImageList


# Register your models here.

admin.site.register(Core)
admin.site.register(ImageOutputs)
admin.site.register(Decryption)
admin.site.register(CustomUser)
admin.site.register(UserImageList)

