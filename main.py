#!/usr/bin/env python3
"""
COMET AUTOMATION - Main Workflow
================================

Simple automation workflow:
1. Launch Comet browser with remote debugging
2. Navigate to specified URL
3. Click Assistant button
4. Keep browser open for interaction

Usage: python main.py
"""

import time
import attack_coment
import navigation  
import comet_ui_automation

# =============================================================================
# CONFIGURATION
# =============================================================================
TARGET_URL = "https://www.perplexity.ai/"  # Change this to your desired URL
LOAD_WAIT_TIME = 5  # Seconds to wait for page loading
STABILITY_WAIT_TIME = 2  # Seconds to wait for UI stabilization

def main():
    """Main automation workflow"""
    print("="*60)
    print("COMET AUTOMATION WORKFLOW")
    print("="*60)
    print(f"Target URL: {TARGET_URL}")
    print(f"Load wait time: {LOAD_WAIT_TIME}s")
    print("="*60)
    
    # Step 1: Connect to Comet
    print("\n[1/3] Connecting to Comet...")
    driver = attack_coment.main()
    
    if not driver:
        print("[ERROR] Failed to connect to Comet")
        return False
    
    try:
        # Step 2: Navigate to target URL
        print(f"\n[2/3] Navigating to URL...")
        print(f"[INFO] Target: {TARGET_URL}")
        
        navigation.navigate_to_url(driver, TARGET_URL)
        time.sleep(LOAD_WAIT_TIME)
        
        # Verify navigation
        current_url = driver.current_url
        print(f"[INFO] Current URL: {current_url}")
        
        if TARGET_URL.replace('https://', '').replace('http://', '') not in current_url:
            print(f"[WARNING] Navigation may have failed!")
            print(f"[WARNING] Expected: {TARGET_URL}")
            print(f"[WARNING] Got: {current_url}")
        else:
            print(f"[SUCCESS] Successfully navigated to target")
        
        # Step 3: Activate Assistant
        print(f"\n[3/3] Activating Assistant...")
        print(f"[INFO] Waiting {STABILITY_WAIT_TIME}s for UI to stabilize...")
        time.sleep(STABILITY_WAIT_TIME)
        
        success = comet_ui_automation.click_assistant_button_ui()
        
        if success:
            print("\n" + "="*60)
            print("WORKFLOW COMPLETED SUCCESSFULLY!")
            print("="*60)
            print("✓ Comet launched and connected")
            print(f"✓ Navigated to {TARGET_URL}")  
            print("✓ Assistant activated")
            print("="*60)
            print("\n[INFO] Browser will remain open for interaction")
            print("[INFO] Press Enter to close and exit...")
            input()
            return True
        else:
            print("\n[ERROR] Failed to activate Assistant")
            return False
        
    except Exception as e:
        print(f"\n[ERROR] Workflow failed: {e}")
        return False
    
    finally:
        print("\n[INFO] Closing browser connection...")
        try:
            driver.quit()
        except Exception as e:
            print(f"[WARNING] Error closing browser: {e}")

if __name__ == "__main__":
    success = main()
    if success:
        print("[INFO] Automation completed successfully")
    else:
        print("[ERROR] Automation failed")
        input("Press Enter to exit...")