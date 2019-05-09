from rest_framework import serializers


class UserSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=True)
    email = serializers.CharField(max_length=256, required=True)
    first_name = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    last_name = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    photo = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    title = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    location = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    is_staff = serializers.NullBooleanField(required=False)

    class Meta:
        fields = (
            'id', 'email', 'first_name', 'last_name', 'photo', 'title',
            'location', 'is_staff'
        )
