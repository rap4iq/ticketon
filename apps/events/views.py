from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count, Q
from django_filters.rest_framework import DjangoFilterBackend

from .models import Category, Venue, Event, TicketCategory
from .serializers import CategorySerializer, CategoryListSerializer
from apps.users.permissions import IsAdminOrReadOnly

