from rest_framework import serializers

from ImageProcessingCore.models import Core, ImageOutputs

class CoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Core
        fields = "__all__"

class ImageOutputsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImageOutputs
        fields = "__all__"