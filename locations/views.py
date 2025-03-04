import googlemaps
import json
from geopy.distance import geodesic
from django.shortcuts import render
from .forms import DonationForm
from .models import DonationLocation
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

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


@csrf_exempt
def donation_view(request):
    if request.method == 'POST':
        # Check if this is an API request
        is_api_request = request.path.startswith('/api/')
        
        # For API requests, get data from JSON
        if is_api_request:
            try:
                data = json.loads(request.body)
                category_id = data.get('category')
                radius = float(data.get('radius', 5))
                address = data.get('address', '')
                
                category = DonationCategory.objects.get(id=category_id)
                
                # Use Google's Geocoding API
                gmaps = googlemaps.Client(key=settings.GOOGLE_MAPS_API_KEY)
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
                                    
                                    nearby_locations.append({
                                        'id': loc.id,
                                        'name': loc.name,
                                        'address': loc.address,
                                        'distance': distance,
                                        'latitude': loc.latitude,
                                        'longitude': loc.longitude,
                                        'phone': loc.phone,
                                        'website': loc.website,
                                        'opening_hours': opening_hours
                                    })

                        # Sort by distance
                        nearby_locations.sort(key=lambda x: x['distance'])
                        
                        return JsonResponse({
                            'status': 'success',
                            'locations': nearby_locations,
                            'search_address': address,
                            'radius': radius,
                            'category': category.name
                        })
                    else:
                        return JsonResponse({
                            'status': 'error',
                            'error': 'כתובת לא חוקית. אנא וודאי שהכתובת מכילה רחוב, מספר בית ועיר.'
                        }, status=400)
                except Exception as e:
                    return JsonResponse({
                        'status': 'error',
                        'error': f'שגיאה בחיפוש הכתובת: {str(e)}. אנא נסי שוב.'
                    }, status=500)
                    
            except Exception as e:
                return JsonResponse({
                    'status': 'error',
                    'error': f'שגיאה בעיבוד הבקשה: {str(e)}'
                }, status=400)
        
        # For regular form submissions, continue with existing code
        form = DonationForm(request.POST)
        if form.is_valid():
            category = form.cleaned_data['category']
            radius = form.cleaned_data['radius']
            address = form.cleaned_data['address']

            # Use Google's Geocoding API
            gmaps = googlemaps.Client(key=settings.GOOGLE_MAPS_API_KEY)
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
                                loc.opening_hours_formatted = opening_hours
                                nearby_locations.append(loc)

                    # Sort by distance
                    nearby_locations.sort(key=lambda x: x.distance['km'])
                    
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

@csrf_exempt
def vote_location(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            location_id = data.get('location_id')
            vote_type = data.get('vote_type')
            feedback = data.get('feedback', '')
            
            if not location_id:
                return JsonResponse({
                    'status': 'error',
                    'error': 'Missing location_id'
                }, status=400)
            
            if vote_type not in ['up', 'down']:
                return JsonResponse({
                    'status': 'error',
                    'error': 'Invalid vote_type. Must be "up" or "down"'
                }, status=400)
            
            # Get the location
            try:
                location = DonationLocation.objects.get(id=location_id)
            except DonationLocation.DoesNotExist:
                return JsonResponse({
                    'status': 'error',
                    'error': 'Location not found'
                }, status=404)
            
            # Process the vote
            if vote_type == 'up':
                location.upvotes += 1
            else:  # vote_type == 'down'
                location.downvotes += 1
            
            location.save()
            
            # Store feedback if provided
            if feedback:
                # Simply log it for now
                print(f"Feedback for location {location_id}: {feedback}")
            
            return JsonResponse({
                'status': 'success',
                'upvotes': location.upvotes,
                'downvotes': location.downvotes,
                'score': location.score,
                'total_votes': location.total_votes
            })
            
        except json.JSONDecodeError:
            return JsonResponse({
                'status': 'error',
                'error': 'Invalid JSON in request body'
            }, status=400)
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'error': f'Error processing vote: {str(e)}'
            }, status=500)
    
    # Handle non-POST requests
    return JsonResponse({
        'status': 'error',
        'error': 'Method not allowed'
    }, status=405)