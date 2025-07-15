#!/usr/bin/env python3
"""
Test script for public YouTube metrics (without OpenAI)
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.youtube_public import resolve_channel_id, fetch_public_metrics

def test_public_metrics():
    try:
        # Test with MrBeast channel
        url = "https://www.youtube.com/@MrBeast"
        print(f"🔍 Testing channel resolution for: {url}")
        
        channel_id = resolve_channel_id(url)
        print(f"✅ Channel ID resolved: {channel_id}")
        
        print(f"📊 Fetching public metrics...")
        metrics = fetch_public_metrics(channel_id, days=30)
        
        print(f"✅ Public metrics fetched:")
        for key, value in metrics.items():
            print(f"   {key}: {value:,}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_public_metrics() 