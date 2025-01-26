from django.core.management.base import BaseCommand
from locations.scraper_django import search_and_save_locations

class Command(BaseCommand):
    help = 'Updates donation locations using Google Places API'

    def handle(self, *args, **options):
        self.stdout.write('Starting location update...')
        search_and_save_locations()
        self.stdout.write(self.style.SUCCESS('Successfully updated locations'))