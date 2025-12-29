from rest_framework import serializers
from django.utils import timezone
from .models import Task, Category

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'user']
        read_only_fields = ['user']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

class TaskSerializer(serializers.ModelSerializer):
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), source='category', write_only=True, required=False, allow_null=True
    )
    category = CategorySerializer(read_only=True)

    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'due_date', 'priority', 'status', 'user', 'category', 'category_id', 'is_recurring', 'recurrence_interval', 'created_at', 'updated_at']
        read_only_fields = ['user', 'created_at', 'updated_at']

    def validate_due_date(self, value):
        if value < timezone.now():
            raise serializers.ValidationError("Due date must be in the future.")
        return value

    def validate(self, data):
        # Prevent editing if task is already completed, unless status is being changed to Pending
        if self.instance and self.instance.status == 'Completed':
            new_status = data.get('status')
            if new_status and new_status != 'Pending': 
                 if len(data) > 1: # Trying to update other fields
                     raise serializers.ValidationError("Cannot edit a completed task. Mark it as pending first.")
            elif not new_status: # Just updating fields
                 raise serializers.ValidationError("Cannot edit a completed task. Mark it as pending first.")
        
        # Validate category ownership
        category = data.get('category')
        if category and category.user != self.context['request'].user:
            raise serializers.ValidationError("You cannot assign a category that does not belong to you.")
            
        return data

    def create(self, validated_data):
        # Automatically associate the task with the current user
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
             validated_data['user'] = request.user
        return super().create(validated_data)
