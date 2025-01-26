from django.core.management.base import BaseCommand
from django.conf import settings
import googlemaps
from locations.models import DonationLocation
import time
import traceback

class Command(BaseCommand):
    help = 'Updates google_place_id for all DonationLocation instances'

    def handle(self, *args, **options):
        try:
            gmaps = googlemaps.Client(key=settings.GOOGLE_MAPS_API_KEY)
            test_result = gmaps.geocode('Jerusalem, Israel')
            print("Test API call result:", test_result)
        except Exception as e:
            print(f"Initial setup error: {str(e)}")
            print(traceback.format_exc())
            return

        locations = DonationLocation.objects.all()

        for location in locations:
            try:
                search_query = f"{location.name} {location.address}"
                print(f"\nSearching for: {search_query}")
                places_result = gmaps.places(search_query)

                if places_result['results']:
                    place_id = places_result['results'][0]['place_id']
                    place_details = gmaps.place(place_id)
                    result = place_details['result']

                    location.google_place_id = place_id

                    # Update coordinates
                    if 'geometry' in result:
                        location.latitude = result['geometry']['location']['lat']
                        location.longitude = result['geometry']['location']['lng']

                    # Update opening hours
                    if 'opening_hours' in result:
                        opening_hours = {
                            'weekdayDescriptions': result['opening_hours'].get('weekday_text', [])
                        }
                        location.opening_hours = str(opening_hours)

                    location.save()
                    self.stdout.write(self.style.SUCCESS(
                        f'Successfully updated {location.name} with coordinates ({location.latitude}, {location.longitude})'
                    ))
                else:
                    self.stdout.write(self.style.WARNING(
                        f'No results found for {location.name}'
                    ))

                time.sleep(2)

            except Exception as e:
                print(f"Error updating {location.name}: {str(e)}")
                print(traceback.format_exc())