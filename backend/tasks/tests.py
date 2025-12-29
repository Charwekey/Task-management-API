from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import Task
from django.utils import timezone
from datetime import timedelta

class TaskTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.client.force_authenticate(user=self.user)
        self.url = reverse('task-list')
        self.future_date = (timezone.now() + timedelta(days=7))

    def test_create_task(self):
        data = {
            'title': 'Test Task', 
            'due_date': self.future_date,
            'priority': 'Medium'
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Task.objects.count(), 1)
        self.assertEqual(Task.objects.get().title, 'Test Task')

    def test_create_task_past_date(self):
        past_date = (timezone.now() - timedelta(days=1))
        data = {
            'title': 'Past Task', 
            'due_date': past_date,
            'priority': 'Medium'
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Due date must be in the future', str(response.data))

    def test_get_own_tasks_only(self):
        # Create task for current user
        Task.objects.create(user=self.user, title="My Task", due_date=self.future_date)
        
        # Create another user and task
        other_user = User.objects.create_user(username='other', password='password123')
        Task.objects.create(user=other_user, title="Other Task", due_date=self.future_date)

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], "My Task")

    def test_mark_complete(self):
        task = Task.objects.create(user=self.user, title="Pending Task", due_date=self.future_date)
        url = reverse('task-mark-complete', args=[task.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        task.refresh_from_db()
        self.assertEqual(task.status, 'Completed')

    def test_update_completed_task_restriction(self):
        # This is a requirement we haven't implemented yet: "Once complete, cannot be edited unless reverted"
        # Let's add this logic to permissions or serializers check?
        pass 
