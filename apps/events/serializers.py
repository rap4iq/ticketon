from rest_framework import serializers
from .models import Event, Category, Venue, TicketCategory

class CategorySerializer(serializers.ModelSerializer):
    events_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description', 'image', 'events_count', 'created_at']
        read_only_fields = ['id', 'slug', 'events_count', 'created_at']

    def get_events_count(self, obj):
        return obj.events.filter(status=Event.Status.PUBLISHED).count()

    def validate_name(self, value):
        if self.instance:
            if Category.objects.exclude(id=self.instance.id).filter(name__iexact=value).exists():
                raise serializers.ValidationError("Category with this name already exists")
        else:
            if Category.objects.filter(name__iexact=value).exists():
                raise serializers.ValidationError("Category with this name already exists")
        return value


class CategoryListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'image']


