from django.contrib import admin
from .models import DonationCategory, DonationLocation, Posts

admin.site.register(Posts)

@admin.register(DonationCategory)
class DonationCategoryAdmin(admin.ModelAdmin):
    list_display = ('name_hebrew', 'name_english')
    search_fields = ('name_hebrew', 'name_english')

@admin.register(DonationLocation)
class DonationLocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'address', 'phone', 'opening_hours')
    search_fields = ('name', 'address')
    filter_horizontal = ('categories',)

    def get_opening_hours(self, obj):
        return obj.format_opening_hours()
    get_opening_hours.short_description = 'שעות פתיחה'