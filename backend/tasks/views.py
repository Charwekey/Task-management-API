from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from .models import Task, Category
from .serializers import TaskSerializer, CategorySerializer

class CategoryViewSet(viewsets.ModelViewSet):
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Category.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    filterset_fields = ['status', 'priority', 'category']
    ordering_fields = ['due_date', 'priority']
    search_fields = ['title', 'description']


    def get_queryset(self):
        # Return tasks belonging to the current user
        return Task.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        # Set the user to the current user
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'], url_path='complete')
    def mark_complete(self, request, pk=None):
        task = self.get_object()
        if task.status == 'Completed':
             return Response({'detail': 'Task is already completed.'}, status=status.HTTP_400_BAD_REQUEST)
        
        task.status = 'Completed'
        task.save()
        return Response({'status': 'Task marked as complete', 'completed_at': timezone.now()})

    @action(detail=True, methods=['post'], url_path='incomplete')
    def mark_incomplete(self, request, pk=None):
        task = self.get_object()
        if task.status == 'Pending':
             return Response({'detail': 'Task is already pending.'}, status=status.HTTP_400_BAD_REQUEST)
        
        task.status = 'Pending'
        task.save()
        return Response({'status': 'Task marked as pending'})
