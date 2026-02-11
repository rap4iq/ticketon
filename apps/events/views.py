from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count, Q
from django_filters.rest_framework import DjangoFilterBackend

from .models import Category, Venue, Event, TicketCategory
from .serializers import CategorySerializer, CategoryListSerializer
from apps.users.permissions import IsAdminOrReadOnly

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]
    lookup_field = 'slug'

    filter_backend = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_field = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']

    def get_queryset(self):
        queryset = Category.objects.annotate(
            events_count=Count(
                'events',
                filter=Q(events__status=Event.Status.PUBLISHED),
                distinct=True
            )
        )
        return queryset

    def get_serializer_class(self):
        if self.action == 'list':
            return CategoryListSerializer
        return CategorySerializer

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.events.exists():
            return Response({
                'error': 'Category cannot be deleted because it has events',
                'events_count': instance.events.count()
            }, status=status.HTTP_400_BAD_REQUEST)
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'])
    def popular(self, request):
        popular_categories = self.queryset().filter(
            events_count__gt=0
        ).order_by('-events_count')[:5]

        serializer = CategoryListSerializer(popular_categories, many=True)
        return Response(serializer.data)