'use client';

import { useState, useEffect, useCallback } from 'react';
import { voteLocation } from '@/lib/locations';
import { Button } from '@/components/ui/button';
import { useToast } from '@/components/ui/use-toast';

interface LocationVotingProps {
  locationId: string;
  initialUpvotes?: number;
  initialDownvotes?: number;
  onVoteSubmitted?: (result: { 
    upvotes: number; 
    downvotes: number; 
    score: number; 
    total_votes: number 
  }) => void;
}

export default function LocationVoting({ 
  locationId, 
  initialUpvotes = 0, 
  initialDownvotes = 0,
  onVoteSubmitted
}: LocationVotingProps) {
  const [hasVoted, setHasVoted] = useState(false);
  const [upvotes, setUpvotes] = useState(initialUpvotes);
  const [downvotes, setDownvotes] = useState(initialDownvotes);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const { toast } = useToast();

  // Memoize the onVoteSubmitted callback to prevent unnecessary re-renders
  const memoizedOnVoteSubmitted = useCallback((result: { 
    upvotes: number; 
    downvotes: number; 
    score: number; 
    total_votes: number 
  }) => {
    console.log('Calling memoized onVoteSubmitted with:', result);
    if (onVoteSubmitted) {
      onVoteSubmitted(result);
    }
  }, [onVoteSubmitted]);

  useEffect(() => {
    // Check if user has already voted for this location
    const voteType = localStorage.getItem(`vote-${locationId}`);
    if (voteType) {
      setHasVoted(true);
      console.log(`User has already voted ${voteType} for location ${locationId}`);
    }
  }, [locationId]);

  // Update state immediately when props change
  useEffect(() => {
    console.log(`LocationVoting: Props changed for location ${locationId}. New upvotes: ${initialUpvotes}, downvotes: ${initialDownvotes}`);
    setUpvotes(initialUpvotes);
    setDownvotes(initialDownvotes);
  }, [initialUpvotes, initialDownvotes, locationId]);

  // Force update parent component when vote counts change
  useEffect(() => {
    // Only call if not the initial render and if we have vote counts
    if (upvotes !== initialUpvotes || downvotes !== initialDownvotes) {
      console.log('Vote counts changed, notifying parent component:', { 
        upvotes, downvotes, 
        score: upvotes - downvotes, 
        total_votes: upvotes + downvotes 
      });
      
      // Call the callback with the latest vote counts
      memoizedOnVoteSubmitted({
        upvotes,
        downvotes,
        score: upvotes - downvotes,
        total_votes: upvotes + downvotes
      });
    }
  }, [upvotes, downvotes, initialUpvotes, initialDownvotes, memoizedOnVoteSubmitted]);

  const handleVote = async (isUpvote: boolean) => {
    if (hasVoted || isLoading) {
      console.log('Vote blocked: User has already voted or is currently voting');
      toast({
        title: 'כבר הצבעת למקום זה',
        description: 'ניתן להצביע פעם אחת בלבד לכל מקום',
        variant: 'destructive',
      });
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const voteType = isUpvote ? 'up' : 'down';
      console.log(`Attempting to vote ${voteType} for location ID: ${locationId} (type: ${typeof locationId})`);
      
      // Log the data being sent to the API
      console.log('Sending vote to: /api/vote/ with data:', { location_id: locationId, vote_type: voteType });
      
      const result = await voteLocation(locationId, voteType);
      console.log('Vote result received:', result);
      
      // Update local state immediately with the new vote counts
      setUpvotes(result.upvotes);
      setDownvotes(result.downvotes);
      setHasVoted(true);
      
      // Store vote in localStorage to prevent multiple votes
      localStorage.setItem(`vote-${locationId}`, voteType);
      console.log(`Saved vote to localStorage: vote-${locationId} = ${voteType}`);
      
      // Show success toast
      toast({
        title: 'תודה על ההצבעה שלך!',
        variant: 'default',
      });
      
      // Directly notify parent component of the vote
      if (onVoteSubmitted) {
        console.log('Directly calling onVoteSubmitted after successful vote with result:', result);
        onVoteSubmitted({
          upvotes: result.upvotes,
          downvotes: result.downvotes,
          score: result.score,
          total_votes: result.total_votes
        });
      }
    } catch (err: any) {
      console.error('Error submitting vote:', err);
      console.log('Error details:', JSON.stringify(err, null, 2));
      
      // Check if this is an "already voted" error
      if (err.response && err.response.data) {
        const { error: errorMsg, existing_vote_type, upvotes: newUpvotes, downvotes: newDownvotes, score, total_votes } = err.response.data;
        console.log('Error response data:', err.response.data);
        
        const isAlreadyVotedError = errorMsg && errorMsg.includes('already voted');
        console.log('Is already voted error?', isAlreadyVotedError);
        
        if (isAlreadyVotedError) {
          // Mark as voted
          setHasVoted(true);
          localStorage.setItem(`vote-${locationId}`, existing_vote_type || 'unknown');
          console.log(`User already voted. Saved to localStorage: vote-${locationId} = ${existing_vote_type || 'unknown'}`);
          
          // Update vote counts if available
          if (typeof newUpvotes === 'number') {
            console.log('Updating upvotes to:', newUpvotes);
            setUpvotes(newUpvotes);
          }
          if (typeof newDownvotes === 'number') {
            console.log('Updating downvotes to:', newDownvotes);
            setDownvotes(newDownvotes);
          }
          
          // Show already voted toast
          toast({
            title: 'כבר הצבעת למקום זה',
            description: 'ניתן להצביע פעם אחת בלבד לכל מקום',
            variant: 'destructive',
          });
          
          // Directly notify parent component of the vote counts
          if (onVoteSubmitted && typeof newUpvotes === 'number' && typeof newDownvotes === 'number') {
            console.log('Directly calling onVoteSubmitted after already voted error');
            onVoteSubmitted({
              upvotes: newUpvotes,
              downvotes: newDownvotes,
              score: score !== undefined ? score : (newUpvotes - newDownvotes),
              total_votes: total_votes !== undefined ? total_votes : (newUpvotes + newDownvotes)
            });
          }
        } else {
          // Show general error toast with the specific error message
          console.log('General error with message:', errorMsg);
          toast({
            title: 'שגיאה בשליחת ההצבעה',
            description: errorMsg || 'אנא נסי שוב מאוחר יותר',
            variant: 'destructive',
          });
          setError(errorMsg || 'Failed to submit vote. Please try again.');
        }
      } else if (err.message) {
        // Handle case where err.response.data is not available
        console.log('Error with message but no response data:', err.message);
        toast({
          title: 'שגיאה בשליחת ההצבעה',
          description: err.message || 'אנא נסי שוב מאוחר יותר',
          variant: 'destructive',
        });
        setError(err.message || 'Failed to submit vote. Please try again.');
      } else {
        // Fallback for unexpected error format
        console.log('Unexpected error format:', err);
        toast({
          title: 'שגיאה בשליחת ההצבעה',
          description: 'אנא נסי שוב מאוחר יותר',
          variant: 'destructive',
        });
        setError('Failed to submit vote. Please try again.');
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col items-center space-y-2 p-2 bg-gray-50 rounded-md">
      <div className="text-sm font-medium text-center mb-2">
        האם המקום תואם את תוצאות החיפוש שלך?
      </div>
      
      <div className="flex space-x-4 rtl:space-x-reverse">
        <Button
          variant={hasVoted && localStorage.getItem(`vote-${locationId}`) === 'up' ? 'default' : 'outline'}
          size="sm"
          onClick={() => handleVote(true)}
          disabled={hasVoted || isLoading}
          className="flex items-center space-x-1 rtl:space-x-reverse"
        >
          <span>👍</span>
          <span>{upvotes}</span>
        </Button>
        
        <Button
          variant={hasVoted && localStorage.getItem(`vote-${locationId}`) === 'down' ? 'default' : 'outline'}
          size="sm"
          onClick={() => handleVote(false)}
          disabled={hasVoted || isLoading}
          className="flex items-center space-x-1 rtl:space-x-reverse"
        >
          <span>👎</span>
          <span>{downvotes}</span>
        </Button>
      </div>
      
      {error && (
        <div className="text-red-500 text-xs mt-1">{error}</div>
      )}
      
      {hasVoted && (
        <div className="text-green-600 text-xs mt-1">
          תודה על ההצבעה שלך!
        </div>
      )}
    </div>
  );
} 