from rest_framework import generics, mixins


class CreateAPIView(mixins.CreateModelMixin):
    def perform_create(self, serializer):
        instance = serializer.save()
        if hasattr(self, 'get_publish_action') and callable(self.get_publish_action):
            publish_action = self.get_publish_action()
            if callable(publish_action):
                publish_action(instance)

        return instance


class UpdateAPIView(mixins.UpdateModelMixin):
    def perform_update(self, serializer):
        instance = serializer.save()
        if hasattr(self, 'get_publish_action') and callable(self.get_publish_action):
            publish_action = self.get_publish_action()
            if callable(publish_action):
                publish_action(instance)

        return instance


class RetrieveAPIView(mixins.RetrieveModelMixin):
    # Override function here
    pass


class ListAPIView(mixins.ListModelMixin):
    # Override function here
    pass
