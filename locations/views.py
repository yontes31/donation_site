
import googlemaps
import json
from geopy.distance import geodesic
from django.shortcuts import render
from .forms import DonationForm
from .models import DonationLocation

from django.shortcuts import render
from locations.models import DonationCategory
from .forms import DonationForm
from .models import Location
import certifi
import ssl
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
from .models import Posts, DonationLocation
from .forms import CreatePosts
from django.shortcuts import redirect


def donation_view(request):
    if request.method == 'POST':
        form = DonationForm(request.POST)
        if form.is_valid():
            category = form.cleaned_data['category']
            radius = form.cleaned_data['radius']
            address = form.cleaned_data['address']

            # Use Google's Geocoding API
            gmaps = googlemaps.Client(key='AIzaSyDE1a0ng5gOuW6JPJTML66b9rbe1fSwDxk')
            try:
                geocode_result = gmaps.geocode(address)
                if geocode_result:
                    location = geocode_result[0]['geometry']['location']
                    user_coords = (location['lat'], location['lng'])

                    # Find locations within radius that accept the category
                    locations = DonationLocation.objects.filter(categories=category)
                    nearby_locations = []
                    
                    for loc in locations:
                        if loc.latitude and loc.longitude:
                            loc_coords = (loc.latitude, loc.longitude)
                            distance = geodesic(user_coords, loc_coords).km
                            if distance <= radius:
                                # Parse opening hours if they exist
                                try:
                                    opening_hours = json.loads(loc.opening_hours) if loc.opening_hours else None
                                except:
                                    opening_hours = None
                                
                                loc.distance = {'km': distance}
                                loc.opening_hours = opening_hours
                                nearby_locations.append(loc)

                    # Sort by distance
                    nearby_locations.sort(key=lambda x: x['distance'])
                    
                    return render(request, 'locations/results.html', {
                        'locations': nearby_locations,
                        'search_address': address,
                        'radius': radius,
                        'category': category
                    })
                else:
                    form.add_error('address', 'כתובת לא חוקית. אנא וודאי שהכתובת מכילה רחוב, מספר בית ועיר.')
            except Exception as e:
                form.add_error('address', f'שגיאה בחיפוש הכתובת: {str(e)}. אנא נסי שוב.')
    else:
        form = DonationForm()

    return render(request, 'locations/donation_form.html', {'form': form})

def home(request):
    categories = DonationCategory.objects.all()
    return render(request, 'locations/home.html', {'categories': categories})

def create_post_view(request):
    if request.method == 'POST':
        form = CreatePosts(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('home')  # Add this import: from django.shortcuts import redirect
    else:
        form = CreatePosts()
    return render(request, 'locations/create_post.html', {'form': form})