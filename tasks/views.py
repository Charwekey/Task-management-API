from rest_framework import viewsets, permissions
from .models import Task
from .serializers import TaskSerializer

class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Return tasks belonging to the current user
        return Task.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        # Set the user to the current user
        serializer.save(user=self.request.user)
