"use client"

import { useState, useEffect, Suspense } from "react"
import { Button } from "@/components/ui/button"
import { MapPin, Globe, Clock, ChevronDown, ChevronUp, Phone, ArrowLeft } from "lucide-react"
import Link from "next/link"
import { useSearchParams } from 'next/navigation'
import { useRouter } from 'next/navigation'
import { searchLocations } from "@/lib/locations"
import type { Location } from "@/lib/locations"
import { useToast } from "../../components/ui/use-toast"
import LocationVoting from '@/components/LocationVoting'

function ResultsContent() {
  const [expandedHours, setExpandedHours] = useState<string | null>(null)
  const [locations, setLocations] = useState<Location[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [forceUpdate, setForceUpdate] = useState<number>(0)
  const { toast } = useToast()
  
  const searchParams = useSearchParams()
  
  // Function to handle vote updates
  const handleVoteUpdate = (locationId: string, voteResult: { 
    upvotes: number; 
    downvotes: number; 
    score: number; 
    total_votes: number 
  }) => {
    console.log('handleVoteUpdate called with:', { locationId, voteResult });
    
    // Create a new array with updated locations to ensure React detects the change
    const updatedLocations = locations.map(location => {
      // Convert both IDs to strings for comparison to handle number vs string mismatches
      if (String(location.id) === String(locationId)) {
        console.log(`Updating location ${location.id} (${location.name})`);
        
        // Create a new location object with the updated rating
        return {
          ...location,
          rating: {
            upvotes: voteResult.upvotes,
            downvotes: voteResult.downvotes,
            score: voteResult.score,
            total_votes: voteResult.total_votes
          }
        };
      }
      return location;
    });
    
    // Update state immediately with the new locations array
    setLocations(updatedLocations);
    
    // Force a UI refresh
    setForceUpdate(prev => prev + 1);
  };
  
  useEffect(() => {
    const dataParam = searchParams.get('data');
    
    if (dataParam) {
      try {
        const parsedData = JSON.parse(decodeURIComponent(dataParam));
        console.log('Parsed data:', parsedData);
        
        // Ensure each location has a rating object
        const locationsWithRating = parsedData.locations.map((location: any) => ({
          ...location,
          rating: location.rating || {
            upvotes: 0,
            downvotes: 0,
            score: 0,
            total_votes: 0
          }
        }));
        
        setLocations(locationsWithRating);
        setLoading(false);
      } catch (err) {
        console.error('Error parsing data:', err);
        setError('Failed to parse location data');
        setLoading(false);
      }
    }
  }, [searchParams]);
  
  const fetchLocations = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const category = searchParams.get('category') || searchParams.get('item') || '';
      const radius = searchParams.get('radius') || searchParams.get('distance') || '5';
      const address = searchParams.get('address') || '';
      const lat = searchParams.get('lat');
      const lng = searchParams.get('lng');
      
      const results = await searchLocations({
        category,
        radius: parseInt(radius),
        address,
        lat: lat ? parseFloat(lat) : undefined,
        lng: lng ? parseFloat(lng) : undefined
      });
      
      // Ensure each location has a rating object
      const locationsWithRating = results.map(location => ({
        ...location,
        rating: location.rating || {
          upvotes: 0,
          downvotes: 0,
          score: 0,
          total_votes: 0
        }
      }));
      
      setLocations(locationsWithRating);
      setLoading(false);
    } catch (err: any) {
      console.error('Search error:', err);
      setError(err.message || 'Failed to fetch locations');
      setLoading(false);
    }
  };
  
  const toggleHours = (id: string) => {
    setExpandedHours(expandedHours === id ? null : id);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center min-h-screen p-4 bg-blue-50">
        <div className="bg-white p-8 rounded-lg shadow-md max-w-md w-full text-center">
          <div className="text-red-600 text-xl mb-4">{error}</div>
          <p className="text-gray-600 mb-6">אנא בדקו את הכתובת שהזנתם ונסו שוב</p>
          <Button 
            onClick={() => window.history.back()} 
            className="bg-blue-600 hover:bg-blue-700 w-full"
          >
            חזרה לחיפוש
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col items-center justify-center min-h-screen p-4 bg-blue-50">
      <main className="w-full max-w-4xl space-y-6">
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-2xl font-bold">תוצאות חיפוש</h1>
          <Link href="/">
            <Button variant="outline" className="flex items-center gap-2">
              <ArrowLeft size={16} />
              חיפוש חדש
            </Button>
          </Link>
        </div>
        <div className="bg-blue-50 border border-blue-200 rounded-md p-4 mb-6">
          <p className="text-center">
            נמצאו {locations.length} מקומות לתרומה
          </p>
        </div>
        {locations.length === 0 ? (
          <div className="text-center py-8">
            <p className="text-xl text-blue-600 mb-4">לא נמצאו מקומות באזור זה</p>
            <Button onClick={() => window.history.back()} className="bg-blue-600 hover:bg-blue-700">
              חזרה לחיפוש
            </Button>
          </div>
        ) : (
          <>
            <p className="text-xl text-blue-600">נמצאו {locations.length} מקומות לתרומה בסביבתכם:</p>
            <div className="space-y-4">
              {locations.map((location) => (
                <div key={location.id} className="bg-white p-6 rounded-lg shadow-md">
                  <div className="flex flex-col space-y-4">
                    <div className="text-right">
                      <div className="flex justify-between items-start">
                        <div className="bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm font-medium">
                          ציון: {location.rating?.score ?? 0}
                          <span className="text-xs text-blue-600 mr-1">
                            ({location.rating?.total_votes ?? 0} ביקורות)
                          </span>
                        </div>
                        <h2 className="text-xl font-semibold text-blue-800 mb-2 break-words">{location.name}</h2>
                      </div>
                      <div className="space-y-2">
                        <div className="flex items-start justify-end text-blue-700 gap-2">
                          <div className="flex-grow text-right break-words">{location.address}</div>
                          <MapPin className="h-4 w-4 flex-shrink-0 mt-1" />
                        </div>
                        {location.distance && (
                          <div className="flex items-center justify-end text-blue-600 gap-2">
                            <span>{typeof location.distance === 'number' ? location.distance.toFixed(1) : location.distance} ק"מ</span>
                            <span className="h-4 w-4 flex-shrink-0">↔️</span>
                          </div>
                        )}
                        {location.website && (
                          <div className="flex items-start justify-end text-blue-700 gap-2">
                            <Link 
                              href={location.website} 
                              target="_blank" 
                              rel="noopener noreferrer" 
                              className="hover:text-blue-800 break-all text-right"
                            >
                              {location.website.replace(/^www\./, '')}
                            </Link>
                            <Globe className="h-4 w-4 flex-shrink-0 mt-1" />
                          </div>
                        )}
                      </div>
                    </div>

                    {location.opening_hours && (
                      <div className="border-t pt-4">
                        <button
                          onClick={() => toggleHours(location.id)}
                          className="flex items-center justify-between w-full text-blue-700 hover:text-blue-800"
                        >
                          <span className="flex items-center gap-2">
                            <Clock className="h-4 w-4" />
                            שעות פתיחה
                          </span>
                          {expandedHours === location.id ? (
                            <ChevronUp className="h-4 w-4" />
                          ) : (
                            <ChevronDown className="h-4 w-4" />
                          )}
                        </button>
                        {expandedHours === location.id && location.opening_hours.weekday_text && (
                          <div className="mt-4 text-blue-700 space-y-1 break-words">
                            {location.opening_hours.weekday_text.map((dayText: string, index: number) => (
                              <div key={index} className="text-right">{dayText}</div>
                            ))}
                          </div>
                        )}
                      </div>
                    )}

                    <div className="border-t pt-4">
                      <div className="flex flex-col items-end gap-2">
                        <div className="text-sm text-blue-600 mb-2">
                          דירוג המקום: {location.rating?.score ?? 0} ({location.rating?.upvotes ?? 0} חיובי, {location.rating?.downvotes ?? 0} שלילי)
                        </div>
                        <div className="mt-4 pt-4 border-t border-gray-100">
                          <LocationVoting 
                            key={`vote-${location.id}-${location.rating?.upvotes || 0}-${location.rating?.downvotes || 0}-${forceUpdate}`}
                            locationId={location.id}
                            initialUpvotes={location.rating?.upvotes || 0}
                            initialDownvotes={location.rating?.downvotes || 0}
                            onVoteSubmitted={(result) => handleVoteUpdate(location.id, result)}
                          />
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </>
        )}
      </main>
    </div>
  );
}

export default function Results() {
  return (
    <Suspense fallback={
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
      </div>
    }>
      <ResultsContent />
    </Suspense>
  );
}