import os
import re
import requests
from typing import Dict, List, Optional, Any
import google.generativeai as genai
from dotenv import load_dotenv
from services.data_processor import (
    validate_channel_data,
    calculate_confidence_interval
)

# Load environment variables
load_dotenv()

# Configuration
API_KEY = os.getenv('GEMINI_API_KEY') or os.getenv('VITE_GEMINI_API_KEY')
MODEL_NAME = "gemini-2.5-flash"

# Initialize Gemini AI
if API_KEY:
    genai.configure(api_key=API_KEY)
else:
    raise ValueError("GEMINI_API_KEY not found in environment variables")

# Simple in-memory cache
cache: Dict[str, Any] = {}


def extract_json(text: str) -> Dict:
    """Extract JSON from AI response"""
    import json
    
    if not text:
        raise ValueError("AI returned an empty response")
    
    clean_text = text.strip()
    
    # Try direct JSON parse
    try:
        return json.loads(clean_text)
    except json.JSONDecodeError:
        pass
    
    # Try to extract from code blocks
    patterns = [
        r'```json\s*(\{[\s\S]*?\})\s*```',
        r'```\s*(\{[\s\S]*?\})\s*```',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, clean_text)
        if match:
            try:
                return json.loads(match.group(1))
            except json.JSONDecodeError:
                continue
    
    # Try to find first and last braces
    first_brace = clean_text.find('{')
    last_brace = clean_text.rfind('}')
    
    if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
        try:
            return json.loads(clean_text[first_brace:last_brace + 1])
        except json.JSONDecodeError:
            pass
    
    raise ValueError("Failed to parse AI response as JSON")


def extract_video_id(url: str) -> Optional[str]:
    """Extract video ID from YouTube URL"""
    patterns = [
        r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/|youtube\.com\/v\/)([a-zA-Z0-9_-]{11})',
        r'youtube\.com\/shorts\/([a-zA-Z0-9_-]{11})'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    
    return None


def fetch_video_metadata(video_url: str) -> Optional[Dict[str, str]]:
    """Fetch real video metadata from YouTube oEmbed API"""
    try:
        oembed_url = f"https://www.youtube.com/oembed?url={requests.utils.quote(video_url)}&format=json"
        response = requests.get(oembed_url, timeout=10)
        
        if not response.ok:
            return None
        
        data = response.json()
        return {
            'title': data.get('title', 'Unknown Title'),
            'author': data.get('author_name', 'Unknown Creator')
        }
    except Exception as e:
        print(f"Failed to fetch video metadata: {e}")
        return None


# ============ CHANNEL ANALYSIS ============

def analyze_channel(channel_name: str) -> Dict:
    """Analyze a YouTube channel using Gemini AI with Google Search grounding"""
    cache_key = f"channel:{channel_name.lower()}"
    
    if cache_key in cache:
        print(f'Returning cached result for {channel_name}')
        return cache[cache_key]
    
    channel_schema = """{
  "channelName": "string",
  "stats": { "subscribers": "string", "totalVideos": "string", "country": "string", "shortsCount": "string" },
  "growthTimeline": [{"year": "2020", "subscribers": 1000000, "videos": 100}],
  "topicAnalysis": {
    "timeline": [{"year": "2020", "topic": "Gaming"}],
    "topicDistribution": [{"name": "Gaming", "value": 40}],
    "mostFrequentTheme": "string"
  },
  "sentimentAnalysis": { "positivePct": 70, "neutralPct": 20, "negativePct": 10, "biasScore": 25, "bias": "string", "reputation": "string" },
  "biography": { "summary": "string", "origin": "string", "evolution": "string", "milestones": "string", "audienceSentiment": "string", "biasReputation": "string" },
  "recommendation": { "status": "Follow or Pass", "reason": "string", "criteriaAnalysis": { "quality": "string", "consistency": "string", "bias": "string", "perception": "string" } }
}"""
    
    prompt = f"""
You are an expert YouTube analyst. Analyze the channel: "{channel_name}".
Use Google Search to find current data about subscribers, videos, history, and reputation.
Return ONLY a valid JSON object matching this schema:
{channel_schema}
"""
    
    try:
        model = genai.GenerativeModel(
            model_name=MODEL_NAME,
            tools='google_search_retrieval'
        )
        
        response = model.generate_content(prompt)
        channel_data = extract_json(response.text)
        
        # Validate and enhance with pandas/numpy
        channel_data = validate_channel_data(channel_data)
        
        # Extract sources from grounding metadata
        sources = []
        if hasattr(response, 'candidates') and response.candidates:
            candidate = response.candidates[0]
            if hasattr(candidate, 'grounding_metadata') and candidate.grounding_metadata:
                if hasattr(candidate.grounding_metadata, 'grounding_chunks'):
                    for chunk in candidate.grounding_metadata.grounding_chunks:
                        if hasattr(chunk, 'web') and chunk.web:
                            sources.append({
                                'title': getattr(chunk.web, 'title', 'Source'),
                                'uri': getattr(chunk.web, 'uri', '#')
                            })
        
        # Remove duplicate sources
        unique_sources = []
        seen_uris = set()
        for source in sources:
            if source['uri'] not in seen_uris:
                unique_sources.append(source)
                seen_uris.add(source['uri'])
        
        channel_data['sources'] = unique_sources
        cache[cache_key] = channel_data
        
        return channel_data
    
    except Exception as e:
        print(f"Channel Analysis Error: {e}")
        raise


# ============ BATTLE ============

def run_battle(channel_names: List[str]) -> Dict:
    """Run a battle comparison between multiple channels"""
    import pandas as pd
    from services.data_processor import calculate_battle_statistics
    
    # Analyze all channels
    channels = [analyze_channel(name) for name in channel_names]
    
    synthesis_prompt = f"""
You are a YouTube battle analyst. Compare these channels: {', '.join([c['channelName'] for c in channels])}.
Channel data: {channels}
Return ONLY valid JSON:
{{
  "scores": [{{"channelName": "string", "quality": 85, "consistency": 78, "trust": 90, "variety": 70, "overall": 80}}],
  "verdict": {{"winner": "string", "reasoning": "string", "narrative": "string"}}
}}"""
    
    try:
        model = genai.GenerativeModel(model_name=MODEL_NAME)
        response = model.generate_content(synthesis_prompt)
        synthesis = extract_json(response.text)
        
        # Create DataFrame for statistical analysis
        scores_df = pd.DataFrame(synthesis['scores'])
        
        # Calculate statistical insights
        battle_stats = calculate_battle_statistics(scores_df)
        
        return {
            'channels': channels,
            'scores': synthesis['scores'],
            'verdict': synthesis['verdict'],
            'statistics': battle_stats  # Add statistical analysis
        }
    
    except Exception as e:
        print(f"Battle Error: {e}")
        raise


# ============ TRUTH ANALYSIS ============

def analyze_video_truth(video_input: str) -> Dict:
    """Analyze truth/fact-checking of a YouTube video"""
    is_url = 'youtube.com/' in video_input.lower() or 'youtu.be/' in video_input.lower()
    
    if not is_url:
        raise ValueError('Please provide a valid YouTube URL (youtube.com or youtu.be link)')
    
    video_id = extract_video_id(video_input)
    if not video_id:
        raise ValueError('Could not extract video ID from URL. Please provide a valid YouTube link.')
    
    # Fetch real video metadata from YouTube's oEmbed API
    print('[TRUTH] Fetching real video metadata from YouTube...')
    metadata = fetch_video_metadata(video_input)
    
    if not metadata:
        raise ValueError('Could not fetch video information. The video may be private, deleted, or the URL is invalid.')
    
    print(f"[TRUTH] Video found: {metadata['title']} by {metadata['author']}")
    
    # Use the REAL title and author in the prompt
    prompt = f"""
You are analyzing a SPECIFIC YouTube video. Here is the VERIFIED information:

VIDEO URL: {video_input}
VIDEO ID: {video_id}
VERIFIED TITLE: "{metadata['title']}"
VERIFIED CREATOR: "{metadata['author']}"

This video information is 100% accurate (fetched directly from YouTube). DO NOT change or invent different title/creator.

Your task:
1. Use the verified title and creator above (do not change them)
2. Use Google Search to find information ABOUT this specific video: "{metadata['title']}" by {metadata['author']}
3. Search for reviews, discussions, or fact-checks about this video
4. Identify factual claims that might be in a video with this title
5. Verify those claims against reliable sources
6. Calculate a Truth Score (0-100)

RULES:
- videoTitle MUST be exactly: "{metadata['title']}"
- creatorName MUST be exactly: "{metadata['author']}"
- If you cannot find specific content about this video, analyze based on the title and creator's reputation
- Be honest about what you can and cannot verify

Return ONLY valid JSON:
{{
  "videoTitle": "{metadata['title']}",
  "creatorName": "{metadata['author']}",
  "language": "Primary language of the video (infer from title)",
  "detectedLanguageCode": "en/hi/es/etc",
  "truthScore": 0-100,
  "summaryVerdict": "Assessment based on title, creator reputation, and any found information",
  "isFakingFacts": true/false,
  "toneAnalysis": "Educational/Sensationalist/Neutral/Entertainment/News",
  "claims": [
    {{
      "statement": "A claim that might be made based on the video title",
      "status": "Verified/Misleading/False/Unverified",
      "evidence": "What you found about this claim",
      "sourceUrl": "URL of source if available"
    }}
  ]
}}"""
    
    try:
        model = genai.GenerativeModel(
            model_name=MODEL_NAME,
            tools='google_search_retrieval'
        )
        
        response = model.generate_content(prompt)
        analysis = extract_json(response.text)
        
        # Ensure the title and creator are correct (override if AI changed them)
        analysis['videoTitle'] = metadata['title']
        analysis['creatorName'] = metadata['author']
        
        # Add confidence interval for truth score
        if 'truthScore' in analysis:
            confidence = calculate_confidence_interval(analysis['truthScore'])
            analysis['scoreConfidence'] = confidence
        
        # Extract sources from grounding metadata
        sources = []
        if hasattr(response, 'candidates') and response.candidates:
            candidate = response.candidates[0]
            if hasattr(candidate, 'grounding_metadata') and candidate.grounding_metadata:
                if hasattr(candidate.grounding_metadata, 'grounding_chunks'):
                    for chunk in candidate.grounding_metadata.grounding_chunks:
                        if hasattr(chunk, 'web') and chunk.web:
                            sources.append({
                                'title': getattr(chunk.web, 'title', 'Source'),
                                'uri': getattr(chunk.web, 'uri', '#')
                            })
        
        # Remove duplicate sources
        unique_sources = []
        seen_uris = set()
        for source in sources:
            if source['uri'] not in seen_uris:
                unique_sources.append(source)
                seen_uris.add(source['uri'])
        
        analysis['references'] = unique_sources
        
        return analysis
    
    except Exception as e:
        print(f"Truth Analysis Error: {e}")
        raise
