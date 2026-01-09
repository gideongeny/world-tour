// Affiliate Tracking Utilities
// Client-side tracking for affiliate link clicks

export interface AffiliateClickData {
    affiliateType: 'booking' | 'skyscanner' | 'insurance' | 'activity';
    destination: string;
    userId?: number;
}

export const trackAffiliateClick = async (data: AffiliateClickData): Promise<void> => {
    try {
        await fetch('/api/affiliate/track', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data),
        });
    } catch (error) {
        console.error('Failed to track affiliate click:', error);
    }
};

export const generateAffiliateLink = (
    type: 'hotel' | 'flight' | 'insurance',
    params: Record<string, string>
): string => {
    const baseUrl = '/api/affiliate/redirect';
    const queryParams = new URLSearchParams({ type, ...params });
    return `${baseUrl}?${queryParams.toString()}`;
};
