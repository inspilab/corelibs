from rest_framework import serializers


class ExperienceSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=True)
    slug = serializers.CharField(max_length=256, required=True)
    title = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    location_title = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    location_slug = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    background_photo = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    class Meta:
        fields = (
            'id', 'slug', 'title', 'location_title', 'location_slug', 'background_photo'
        )
