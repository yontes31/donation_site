import requests
from django.conf import settings
from locations.models import DonationLocation, DonationCategory

API_KEY = 'AIzaSyDE1a0ng5gOuW6JPJTML66b9rbe1fSwDxk'

def search_and_save_locations():
    url = 'https://places.googleapis.com/v1/places:searchText'
    
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'X-Goog-Api-Key': API_KEY,
        'X-Goog-FieldMask': 'places.id,places.displayName,places.formattedAddress,places.phoneNumber,places.websiteUri,places.currentOpeningHours'
    }

def search_and_save_locations():
    API_KEY = 'AIzaSyDE1a0ng5gOuW6JPJTML66b9rbe1fSwDxk'
    url = 'https://places.googleapis.com/v1/places:searchText'

    # Get all categories from database
    categories = DonationCategory.objects.all()
    print(f"Found {categories.count()} categories")

    for category in categories:
        print(f"\nProcessing category: {category.name_hebrew}")
        # Split keywords and clean them
        keywords = [k.strip() for k in category.keywords.split(',')]
        print(f"Keywords: {keywords}")

        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'X-Goog-Api-Key': 'AIzaSyDE1a0ng5gOuW6JPJTML66b9rbe1fSwDxk'
        }

        params = {
            'fields': '*'
        }

        for keyword in keywords:
            print(f"\nSearching for: {keyword}")
            data = {
                "textQuery": f"{keyword}, ישראל"
            }

            try:
                response = requests.post(
                    url,
                    params=params,
                    headers=headers,
                    json=data,
                    timeout=10
                )

                print(f"API Response Status: {response.status_code}")

                if response.status_code == 200:
                    results = response.json()
                    if 'places' in results:
                        print(f"Found {len(results['places'])} places")
                        for place in results['places']:
                            # Try to get or create location
                            location, created = DonationLocation.objects.get_or_create(
                                google_place_id=place.get('id'),
                                defaults={
                                    'name': place.get('displayName', {}).get('text', ''),
                                    'address': place.get('formattedAddress', ''),
                                    'phone': place.get('phoneNumber', ''),
                                    'website': place.get('websiteUri', ''),
                                    'opening_hours': str(place.get('regularOpeningHours', {}))
                                }
                            )

                            # Add the category
                            location.categories.add(category)

                            if created:
                                print(f"Added new location: {location.name}")
                            else:
                                print(f"Updated existing location: {location.name}")
                    else:
                        print("No places found in response")

            except Exception as e:
                print(f"Error processing {keyword}: {str(e)}")