from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from datetime import timedelta

class Category(models.Model):
    name = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='categories')
    
    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name

class Task(models.Model):
    PRIORITY_CHOICES = [
        ('Low', 'Low'),
        ('Medium', 'Medium'),
        ('High', 'High'),
    ]
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Completed', 'Completed'),
    ]
    RECURRENCE_CHOICES = [
        ('Daily', 'Daily'),
        ('Weekly', 'Weekly'),
        ('Monthly', 'Monthly'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    due_date = models.DateTimeField()
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='Medium')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Pending')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tasks')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='tasks')
    
    is_recurring = models.BooleanField(default=False)
    recurrence_interval = models.CharField(max_length=10, choices=RECURRENCE_CHOICES, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

@receiver(post_save, sender=Task)
def create_recurring_task(sender, instance, created, **kwargs):
    # Check if task is completed AND recurring AND this is an update (not creation of the new task itself)
    # We use a flag 'skip_signal' or check if we just marked it complete
    if instance.status == 'Completed' and instance.is_recurring:
        # Check if we already created the next task to avoid infinite loops or duplicates
        # A simple way is to check if a task with same title exists for next due date
        # But titles can be same.
        # Better: Changing status to Completed triggers this.
        # We need to calculate next date.
        
        next_due_date = None
        if instance.recurrence_interval == 'Daily':
            next_due_date = instance.due_date + timedelta(days=1)
        elif instance.recurrence_interval == 'Weekly':
            next_due_date = instance.due_date + timedelta(weeks=1)
        elif instance.recurrence_interval == 'Monthly':
            next_due_date = instance.due_date + timedelta(days=30) # Approx
            
        if next_due_date:
            # Check if duplicate exists (rudimentary check)
            exists = Task.objects.filter(
                title=instance.title, 
                user=instance.user, 
                due_date=next_due_date
            ).exists()
            
            if not exists:
                Task.objects.create(
                    title=instance.title,
                    description=instance.description,
                    due_date=next_due_date,
                    priority=instance.priority,
                    status='Pending',
                    user=instance.user,
                    category=instance.category,
                    is_recurring=True, # Next task is also recurring
                    recurrence_interval=instance.recurrence_interval
                )
