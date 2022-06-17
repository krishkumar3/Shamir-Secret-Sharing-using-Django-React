from rest_framework import serializers

from ImageProcessingCore.models import Core, ImageOutputs, Decryption , CustomUser, UserImageList

class CoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Core
        fields = "__all__"

class ImageOutputsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImageOutputs
        fields = "__all__"

class DecryptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Decryption
        fields = "__all__"

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = "__all__"

class UserImageListSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserImageList
        fields = "__all__"