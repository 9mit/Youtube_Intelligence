"""
TubeTale Analytics - Data Processing Utility
Uses pandas and numpy for enhanced data analysis and statistical calculations
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional


def create_growth_dataframe(growth_timeline: List[Dict]) -> pd.DataFrame:
    """
    Convert growth timeline to pandas DataFrame for analysis
    
    Args:
        growth_timeline: List of dicts with year, subscribers, videos
        
    Returns:
        DataFrame with validated and normalized data
    """
    if not growth_timeline:
        return pd.DataFrame(columns=['year', 'subscribers', 'videos'])
    
    df = pd.DataFrame(growth_timeline)
    
    # Ensure correct data types
    df['year'] = pd.to_numeric(df['year'], errors='coerce')
    df['subscribers'] = pd.to_numeric(df['subscribers'], errors='coerce')
    df['videos'] = pd.to_numeric(df['videos'], errors='coerce')
    
    # Remove any rows with missing data
    df = df.dropna()
    
    # Sort by year
    df = df.sort_values('year')
    
    return df


def calculate_growth_rate(df: pd.DataFrame) -> Dict[str, float]:
    """
    Calculate growth statistics from timeline data
    
    Args:
        df: DataFrame with year, subscribers, videos columns
        
    Returns:
        Dict with growth metrics
    """
    if len(df) < 2:
        return {
            'avg_subscriber_growth': 0.0,
            'avg_video_growth': 0.0,
            'growth_trend': 'insufficient_data'
        }
    
    # Calculate year-over-year growth rates
    df = df.copy()
    df['sub_growth'] = df['subscribers'].pct_change() * 100
    df['video_growth'] = df['videos'].pct_change() * 100
    
    # Calculate averages (excluding first NaN row)
    avg_sub_growth = df['sub_growth'].dropna().mean()
    avg_video_growth = df['video_growth'].dropna().mean()
    
    # Determine trend
    if avg_sub_growth > 10:
        trend = 'rapid_growth'
    elif avg_sub_growth > 0:
        trend = 'steady_growth'
    elif avg_sub_growth > -5:
        trend = 'stable'
    else:
        trend = 'declining'
    
    return {
        'avg_subscriber_growth': round(avg_sub_growth, 2),
        'avg_video_growth': round(avg_video_growth, 2),
        'growth_trend': trend,
        'latest_subscribers': int(df['subscribers'].iloc[-1]),
        'latest_videos': int(df['videos'].iloc[-1])
    }


def calculate_trend_prediction(df: pd.DataFrame, periods: int = 1) -> Dict[str, Any]:
    """
    Calculate linear trend and predict future values
    
    Args:
        df: DataFrame with year, subscribers columns
        periods: Number of periods to predict ahead
        
    Returns:
        Dict with trend line and predictions
    """
    if len(df) < 3:
        return {'prediction_available': False}
    
    # Use numpy for linear regression
    x = np.array(range(len(df)))
    y = df['subscribers'].values
    
    # Calculate linear regression coefficients
    coefficients = np.polyfit(x, y, 1)
    slope, intercept = coefficients
    
    # Generate trend line
    trend_line = slope * x + intercept
    
    # Predict future values
    future_x = np.array(range(len(df), len(df) + periods))
    predictions = slope * future_x + intercept
    
    # Calculate R-squared for trend strength
    y_mean = np.mean(y)
    ss_tot = np.sum((y - y_mean) ** 2)
    ss_res = np.sum((y - trend_line) ** 2)
    r_squared = 1 - (ss_res / ss_tot)
    
    return {
        'prediction_available': True,
        'slope': float(slope),
        'r_squared': float(r_squared),
        'trend_strength': 'strong' if r_squared > 0.7 else 'moderate' if r_squared > 0.4 else 'weak',
        'predicted_next_year': int(predictions[0]) if len(predictions) > 0 else None
    }


def calculate_battle_statistics(scores_df: pd.DataFrame) -> Dict[str, Any]:
    """
    Calculate statistical analysis for battle comparisons
    
    Args:
        scores_df: DataFrame with channel scores
        
    Returns:
        Dict with statistical significance and rankings
    """
    if len(scores_df) < 2:
        return {'statistical_analysis': 'insufficient_data'}
    
    # Calculate overall score statistics
    overall_scores = scores_df['overall']
    
    stats = {
        'mean_score': float(overall_scores.mean()),
        'std_dev': float(overall_scores.std()),
        'score_range': float(overall_scores.max() - overall_scores.min()),
        'close_competition': overall_scores.std() < 10,  # Low std dev = close battle
    }
    
    # Determine if winner is statistically significant
    if len(scores_df) >= 2:
        top_score = overall_scores.max()
        second_score = overall_scores.nlargest(2).iloc[1]
        score_diff = top_score - second_score
        
        # Winner is "decisive" if difference > 1 std dev
        stats['decisive_winner'] = score_diff > overall_scores.std()
        stats['score_difference'] = float(score_diff)
    
    return stats


def normalize_topic_distribution(topics: List[Dict]) -> pd.DataFrame:
    """
    Normalize topic distribution to ensure percentages sum to 100
    
    Args:
        topics: List of dicts with name and value
        
    Returns:
        DataFrame with normalized values
    """
    if not topics:
        return pd.DataFrame(columns=['name', 'value', 'percentage'])
    
    df = pd.DataFrame(topics)
    
    # Normalize values to percentages
    total = df['value'].sum()
    if total > 0:
        df['percentage'] = (df['value'] / total * 100).round(2)
    else:
        df['percentage'] = 0
    
    # Sort by value descending
    df = df.sort_values('value', ascending=False)
    
    return df


def calculate_confidence_interval(score: float, sample_size: int = 100, confidence: float = 0.95) -> Dict[str, float]:
    """
    Calculate confidence interval for a score (e.g., truth score)
    
    Args:
        score: The calculated score (0-100)
        sample_size: Sample size for calculation
        confidence: Confidence level (default 95%)
        
    Returns:
        Dict with lower and upper bounds
    """
    # Convert score to proportion
    p = score / 100.0
    
    # Calculate standard error
    se = np.sqrt((p * (1 - p)) / sample_size)
    
    # Z-score for 95% confidence
    z = 1.96 if confidence == 0.95 else 2.576 if confidence == 0.99 else 1.645
    
    # Calculate margin of error
    margin = z * se * 100  # Convert back to 0-100 scale
    
    lower_bound = max(0, score - margin)
    upper_bound = min(100, score + margin)
    
    return {
        'score': round(score, 1),
        'lower_bound': round(lower_bound, 1),
        'upper_bound': round(upper_bound, 1),
        'margin_of_error': round(margin, 1)
    }


def validate_channel_data(channel_data: Dict) -> Dict:
    """
    Validate and clean channel analysis data
    
    Args:
        channel_data: Raw channel data from AI
        
    Returns:
        Cleaned and validated channel data
    """
    # Ensure required fields exist
    required_fields = ['channelName', 'stats', 'growthTimeline']
    for field in required_fields:
        if field not in channel_data:
            raise ValueError(f"Missing required field: {field}")
    
    # Validate growth timeline
    if 'growthTimeline' in channel_data:
        df = create_growth_dataframe(channel_data['growthTimeline'])
        
        # Add growth statistics
        growth_stats = calculate_growth_rate(df)
        channel_data['growthStatistics'] = growth_stats
        
        # Add trend prediction if enough data
        trend_pred = calculate_trend_prediction(df)
        if trend_pred.get('prediction_available'):
            channel_data['trendPrediction'] = trend_pred
    
    # Normalize topic distribution
    if 'topicAnalysis' in channel_data and 'topicDistribution' in channel_data['topicAnalysis']:
        topics_df = normalize_topic_distribution(channel_data['topicAnalysis']['topicDistribution'])
        channel_data['topicAnalysis']['topicDistribution'] = topics_df.to_dict('records')
    
    return channel_data
