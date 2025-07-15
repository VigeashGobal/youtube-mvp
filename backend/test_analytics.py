#!/usr/bin/env python3
"""
Test script to run analytics fetch once
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.db import SessionLocal
from app.models import ChannelCredentials, ChannelDailyStats
from app.auth import load_credentials
from app.jobs import fetch_all_time_stats

def test_analytics():
    db = SessionLocal()
    try:
        # Get the first connected channel
        channel = db.query(ChannelCredentials).first()
        if not channel:
            print("❌ No connected channels found")
            return
        
        print(f"📊 Testing analytics for channel: {channel.channel_id}")
        
        # Load credentials
        creds = load_credentials(channel.channel_id, db)
        if not creds:
            print("❌ No credentials found")
            return
        
        print("✅ Credentials loaded successfully")
        
        # Test the analytics fetch
        fetch_all_time_stats(db, channel.channel_id, creds)
        print("✅ All-time analytics fetch completed")
        
        # Check results
        stats_count = db.query(ChannelDailyStats).count()
        print(f"📈 Total stats records: {stats_count}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_analytics() 