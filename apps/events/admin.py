from django.contrib import admin
from .models import Category, Venue, Event, TicketCategory

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'created_at']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']


@admin.register(Venue)
class VenueAdmin(admin.ModelAdmin):
    list_display = ['name', 'city', 'country', 'capacity']
    list_filter = ['city', 'country']
    search_fields = ['name', 'city', 'address']


class TicketCategoryInline(admin.TabularInline):
    model = TicketCategory
    extra = 1
    fields = ['name', 'description', 'price', 'total_quantity', 'available_quantity', 'max_per_order']
    readonly_fields = ['available_quantity']


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['title', 'organizer', 'category', 'venue', 'start_datetime', 'status', 'is_featured']
    list_filter = ['status', 'is_featured', 'category', 'start_datetime']
    search_fields = ['title', 'description']
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'start_datetime'
    inlines = [TicketCategoryInline]
    
    fieldsets = (
        ('Basic Info', {
            'fields': ('title', 'slug', 'description', 'image')
        }),
        ('Organization', {
            'fields': ('organizer', 'category', 'venue')
        }),
        ('Schedule', {
            'fields': ('start_datetime', 'end_datetime')
        }),
        ('Status', {
            'fields': ('status', 'is_featured')
        }),
    )