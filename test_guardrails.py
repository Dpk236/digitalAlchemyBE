# test_guardrails.py

import sys
import os
# Add current directory to path
sys.path.append(os.getcwd())

from route_query import route_query

def test_query(query, video_id=None):
    print(f"\nTesting Query: '{query}' (video_id={video_id})")
    result = route_query(query, video_id=video_id)
    print(f"Result Type: {result.get('type')}")
    if result.get('type') == 'guardrail_blocked':
        print(f"✅ Blocked correctly: {result.get('response').splitlines()[0]}")
    else:
        print(f"❌ Not blocked: {result.get('type')}")

if __name__ == "__main__":
    # Test 1: Blocked Entertainment
    test_query("Who is your favorite actor in Marvel movies?")
    
    # Test 2: Blocked Sports
    test_query("What is the latest IPL score?")
    
    # Test 3: Allowed Physics (Always Allowed Pattern)
    test_query("Explain gravity.")
    
    # Test 4: Allowed with Educational Framing
    test_query("What is the physics of cricket?")
    
    # Test 5: Subject Specific - Biology (Allowed)
    test_query("What are bryophytes?", video_id="480989616")
    
    # Test 6: Subject Specific - Physics Extension (Allowed)
    test_query("How to solve calculus problems?", video_id="projectile_motion")

    # Test 7: Blocked Gaming
    test_query("How to play Fortnite?")
