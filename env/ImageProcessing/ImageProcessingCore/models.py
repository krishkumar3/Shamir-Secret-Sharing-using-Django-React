from django.db import models

# Create your models here.
class Core(models.Model):
    n = models.IntegerField()
    k = models.IntegerField()
    inputImage = models.ImageField(upload_to ='uploads/')
    outputImage = models.ImageField(upload_to ='outputs/',default= 'frontend/src/default.jpg')
    sharesRGB = models.TextField(default="")
    cipher = models.TextField(default="")
    keys = models.TextField(default="")
    finalOutput = models.TextField(default="")

class ImageOutputs(models.Model):
    un_id =  models.IntegerField(default= 0)
    shares = models.ImageField(upload_to ='frontend/src/outputs/')
    cipher = models.TextField(default="")

class Decryption(models.Model):
    outputImage = models.ImageField(upload_to ='outputs/',default= 'frontend/src/default.jpg')
    cipher = models.FileField(default="file.txt")
    keys = models.FileField(default="file.txt")


class CustomUser(models.Model):
    email = models.EmailField( unique=True)
    username = models.CharField(max_length=100, unique=True)
    password = models.CharField(max_length=50)


class UserImageList(models.Model):
    coreId = models.IntegerField(default=0)
    useremail = models.EmailField()
    fromemail = models.EmailField(default="")
    count = models.IntegerField(default=0)