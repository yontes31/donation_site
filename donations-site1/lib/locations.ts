import { fetchWithErrorHandling } from './utils';

export interface Location {
  id: string;
  name: string;
  address: string;
  phone?: string;
  website?: string;
  opening_hours?: {
    weekday_text: string[];
  };
  distance: number;
  rating?: {
    upvotes: number;
    downvotes: number;
    score: number;
    total_votes: number;
  };
}

/**
 * Search for donation locations
 */
export async function searchLocations(params: {
  category: string;
  radius: number;
  address: string;
  lat?: number;
  lng?: number;
}): Promise<Location[]> {
  try {
    const response = await fetch('/api/search/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(params),
      credentials: 'include',
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || 'Error searching for locations');
    }

    const data = await response.json();
    return data.locations;
  } catch (error: any) {
    console.error('Search error:', error);
    throw error;
  }
}

/**
 * Vote for a location (upvote or downvote)
 * @param locationId The ID of the location to vote for
 * @param voteType 'up' for upvote, 'down' for downvote
 * @returns The updated vote counts
 */
export async function voteLocation(
  locationId: string, 
  voteType: 'up' | 'down',
  feedback?: string
): Promise<{ upvotes: number; downvotes: number; score: number; total_votes: number }> {
  try {
    console.log(`voteLocation called with locationId: ${locationId} (type: ${typeof locationId}), voteType: ${voteType}`);
    
    // Ensure locationId is properly formatted
    const formattedLocationId = !isNaN(Number(locationId)) ? Number(locationId) : locationId;
    
    console.log(`Formatted locationId: ${formattedLocationId} (type: ${typeof formattedLocationId})`);
    
    // Prepare the request body
    const requestBody = {
      location_id: formattedLocationId,
      vote_type: voteType,
      feedback: feedback || undefined
    };
    
    console.log('Sending vote request to:', `${process.env.NEXT_PUBLIC_API_BASE_URL || ''}/api/vote/`);
    console.log('Request body:', requestBody);
    
    const response = await fetch('/api/vote/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(requestBody),
      cache: 'no-store',
    });

    console.log(`Response status: ${response.status}`);
    
    // Clone the response before reading it as JSON to avoid "body already read" errors
    const responseClone = response.clone();
    const data = await response.json();
    console.log('Response data:', data);

    // If the response is not ok, but it's an "already voted" error,
    // we still want to return the vote counts
    if (!response.ok) {
      console.log(`Response not OK. Status: ${response.status}, Error: ${data.error || 'Unknown error'}`);
      
      if (data.error && data.error.includes('already voted') && 
          typeof data.upvotes === 'number' && typeof data.downvotes === 'number') {
        console.log('Already voted error with vote counts');
        // Return the vote counts even though it's an error
        throw {
          message: data.error,
          response: { 
            data: {
              error: data.error,
              existing_vote_type: data.existing_vote_type,
              upvotes: data.upvotes,
              downvotes: data.downvotes,
              score: data.score !== undefined ? data.score : (data.upvotes - data.downvotes),
              total_votes: data.total_votes !== undefined ? data.total_votes : (data.upvotes + data.downvotes)
            }, 
            status: response.status 
          },
        };
      }
      
      console.log('Other error type:', data.error);
      
      // For other errors, try to extract as much information as possible
      // If the response body couldn't be parsed as JSON, try to get the text
      let errorText = data.error || 'Error submitting vote';
      if (!data.error) {
        try {
          const textResponse = await responseClone.text();
          errorText = textResponse || errorText;
          console.log('Response text:', textResponse);
        } catch (textError) {
          console.error('Error reading response text:', textError);
        }
      }
      
      throw {
        message: errorText,
        response: { 
          data: {
            ...data,
            // Ensure we have score and total_votes even in error cases
            score: data.score !== undefined ? data.score : 
                  (data.upvotes !== undefined && data.downvotes !== undefined ? 
                   data.upvotes - data.downvotes : 0),
            total_votes: data.total_votes !== undefined ? data.total_votes : 
                        (data.upvotes !== undefined && data.downvotes !== undefined ? 
                         data.upvotes + data.downvotes : 0)
          }, 
          status: response.status 
        },
      };
    }

    console.log('Vote successful. Returning data:', {
      upvotes: data.upvotes,
      downvotes: data.downvotes,
      score: data.score !== undefined ? data.score : (data.upvotes - data.downvotes),
      total_votes: data.total_votes !== undefined ? data.total_votes : (data.upvotes + data.downvotes)
    });

    // Ensure we have all the required fields, calculate them if missing
    return {
      upvotes: data.upvotes,
      downvotes: data.downvotes,
      score: data.score !== undefined ? data.score : (data.upvotes - data.downvotes),
      total_votes: data.total_votes !== undefined ? data.total_votes : (data.upvotes + data.downvotes)
    };
  } catch (error: any) {
    console.error('Vote error:', error);
    // Rethrow the error to be handled by the component
    throw error;
  }
} 