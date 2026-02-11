from enum import unique
from unittest.util import _MAX_LENGTH
from django.db import models
from django.utils.text import slugify
from apps.users.models import CustomUser

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='categories/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'categories'
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
        ordering = ['name']


    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


    def __str__(self):
        return self.name


class Venue(models.Model):
    name = models.CharField(max_length=200)
    address = models.CharField(max_length=300)
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=100, default='Kazakhstan')
    capacity = models.IntegerField(help_text='Total capacity of the venue')
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'venues'
        verbose_name = 'Venue'
        verbose_name_plural = 'Venues'
        ordering = ['city','name']

    def __str__(self):
        return f"{self.name} - {self.city}"


class Event(models.Model):
    class Status(models.TextChoices):
        DRAFT = 'DRAFT', 'Draft'
        PUBLISHED = 'PUBLISHED', 'Published'
        CANCELLED = 'CANCELLED', 'Cancelled'
        COMPLETED = 'COMPLETED', 'Completed'

    organizer = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='organized_events',
        limit_choices_to={'role': CustomUser.Role.ORGANIZER}
    )

    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name='events',
    )

    venue = models.ForeignKey(
        Venue,
        on_delete=models.PROTECT,
        related_name='events',
    )

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    description = models.TextField()
    image = models.ImageField(upload_to='events/', blank=True, null=True)
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.DRAFT
    )
    is_featured = models.BooleanField(default=False, help_text='Show on homepage')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'events'
        verbose_name = 'Event'
        verbose_name_plural = 'Events'
        ordering = ['-start_datetime']
        indexes = [
            models.Index(fields=['start_datetime', 'status']),
            models.Index(fields=['category', 'status']),
            models.Index(fields=['status', 'is_featured'])
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title



class TicketCategory(models.Model):
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name='ticket_categories'
    )

    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    total_quantity = models.IntegerField()
    available_quantity = models.IntegerField()
    max_per_order = models.IntegerField(default=10)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'ticket_categories'
        verbose_name = 'Ticket Category'
        verbose_name_plural = 'Ticket Categories'
        unique_together = ['event', 'name']
        ordering = ['-price']

    def save(self, *args, **kwargs):
        if not self.pk:
            self.available_quantity = self.total_quantity
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.event.title} - {self.name} (${self.price})"