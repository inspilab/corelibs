from rest_framework import generics


class CreateAPIView(generics.CreateAPIView):
    def perform_create(self, serializer):
        instance = serializer.save()
        if hasattr(self, 'get_publish_action') and callable(self.get_publish_action):
            publish_action = self.get_publish_action()
            if callable(publish_action):
                publish_action(instance)

        return instance


class UpdateAPIView(generics.UpdateAPIView):
    def perform_update(self, serializer):
        instance = serializer.save()
        if hasattr(self, 'get_publish_action') and callable(self.get_publish_action):
            publish_action = self.get_publish_action()
            if callable(publish_action):
                publish_action(instance)

        return instance


class RetrieveAPIView(generics.RetrieveAPIView):
    # Override function here
    pass


class ListAPIView(generics.ListAPIView):
    # Override function here
    pass
