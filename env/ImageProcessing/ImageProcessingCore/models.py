from django.db import models
# Create your models here.
class Core(models.Model):
    n = models.IntegerField()
    k = models.IntegerField()
    inputImage = models.ImageField(upload_to ='uploads/')
    outputImage = models.ImageField(upload_to ='outputs/',default= 'frontend/src/default.jpg')
    cipher = models.TextField(default="")
    finalOutput = models.TextField(default="")

class ImageOutputs(models.Model):
    un_id =  models.IntegerField(default= 0)
    shares = models.ImageField(upload_to ='outputs/')
    cipher = models.TextField(default="")