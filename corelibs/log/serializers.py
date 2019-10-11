from rest_framework import serializers


class LogSerializer(serializers.Serializer):
    action_time = serializers.DateTimeField()
    action_date = serializers.DateField()
    actor_type = serializers.CharField()
    actor_id = serializers.IntegerField(allow_blank=True)
    actor_email = serializers.CharField(allow_blank=True)
    actor_name = serializers.CharField(allow_blank=True)
    actor_photo = serializers.CharField(allow_blank=True)
    content_type = serializers.CharField()
    content_object_id = serializers.CharField()
    action_flag = serializers.CharField()
    extra_data = serializers.JSONField()
    message = serializers.CharField(allow_blank=True)
