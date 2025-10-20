"""
Main Entry Point
================
Launches Comet browser and opens Perplexity Sidecar.

Simple workflow:
- Launch Comet
- Open Sidecar URL (https://www.perplexity.ai/sidecar?copilot=true)
"""

import time
from pathlib import Path
from browser import BrowserFactory, BrowserType
from pipeline import PipelineConfig

# Configuration
BROWSER_TYPE = BrowserType.COMET


def main():
    """
    Main function: Launch Comet and open Sidecar.
    """
    print("=" * 60)
    print("COMET BROWSER - OPEN SIDECAR")
    print("=" * 60)
    print(f"Browser: {BROWSER_TYPE.value}")
    print("=" * 60)
    
    try:
        # Create browser (bundles launcher, navigator, pipeline)
        browser = BrowserFactory.create(BROWSER_TYPE)
        
        # Configure pipeline - target_url will be overridden to Sidecar by CometPipeline
        config = PipelineConfig(
            target_url="https://example.com",  # Will be overridden
            load_wait_time=5,
            keep_open=True,
            activate_features=False  # No Assistant activation
        )
        
        # Run pipeline (launches Comet, opens Sidecar)
        print(f"\n[INFO] Running Comet pipeline...")
        result = browser.run_pipeline(config)
        
        if not result.success:
            print(f"[ERROR] Pipeline failed: {result.message}")
            return False
        
        print(f"\n[SUCCESS] Pipeline completed!")
        print(f"Steps: {result.steps_completed}")
        
        # Print summary
        print("\n" + "=" * 60)
        print("DONE - SIDECAR OPENED")
        print("=" * 60)
        
        info = browser.get_browser_info()
        current_url = browser.get_navigator().get_current_url()
        
        print(f"✓ Browser: {info.name}")
        print(f"✓ Current URL: {current_url}")
        print(f"✓ Total tabs: {len(browser.get_window_handles())}")
        print("=" * 60)
        
        print("\n[INFO] Browser will remain open for interaction")
        input("[INFO] Press Enter to close and exit... ")
        
        # Clean up
        browser.quit()
        return True
        
    except Exception as e:
        print(f"[ERROR] Failed during execution: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    ok = main()
    if ok:
        print("[INFO] Successfully opened Sidecar")
    else:
        print("[ERROR] Failed to open Sidecar")
