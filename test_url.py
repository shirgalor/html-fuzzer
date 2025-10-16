#!/usr/bin/env python3
"""
Simple test to show the TARGET_URL is working
"""

def test_url():
    # Configuration - Change this URL to whatever you want
    TARGET_URL = "https://www.perplexity.ai/"
    
    print("="*50)
    print("URL TEST")
    print("="*50)
    print(f"TARGET_URL = {TARGET_URL}")
    print(f"URL length: {len(TARGET_URL)}")
    print(f"URL is valid: {TARGET_URL.startswith('http')}")
    print("="*50)

if __name__ == "__main__":
    test_url()
