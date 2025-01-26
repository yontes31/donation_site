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
            # Process the form data
            category = form.cleaned_data['category']
            radius = form.cleaned_data['radius']
            address = form.cleaned_data['address']

            # Geocode the address
            geolocator = Nominatim(
                user_agent="django_app",
                ssl_context=ssl.create_default_context(cafile=certifi.where())
            )
            location = geolocator.geocode(address)

            if location:
                user_coords = (location.latitude, location.longitude)

                # Find locations within the radius
                locations = DonationLocation.objects.all()
                print("All locations:", locations.values('name', 'latitude', 'longitude'))
                nearby_locations = []
                for loc in locations:
                    print(f"\nLocation {loc.name}:")
                    print(f"Hours: {loc.opening_hours}")
                    if loc.latitude and loc.longitude:  # Add this check
                        loc_coords = (loc.latitude, loc.longitude)
                        distance = geodesic(user_coords, loc_coords).km
                        if distance <= radius:
                         nearby_locations.append((loc, distance))

                # Sort by distance and send to template
                nearby_locations.sort(key=lambda x: x[1])
                print(f"Found {len(nearby_locations)} nearby locations")
                return render(request, 'locations/results.html', {'locations': nearby_locations})
            else:
                form.add_error('address', 'כתובת לא חוקית. נסי שוב.')
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