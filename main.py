"""
Main Entry Point
================
Launches Comet browser and opens Perplexity Sidecar with optional query.

Workflow:
1. Browser facade launches Comet
2. Browser facade navigates to Sidecar URL
3. Pipeline sends query to Sidecar (if provided)
"""

import time
from pathlib import Path
from browser import BrowserFactory, BrowserType
from pipeline import PipelineConfig

# ==================== Configuration ====================
BROWSER_TYPE = BrowserType.COMET
SIDECAR_URL = "https://www.perplexity.ai/sidecar?copilot=true"

# Query configuration
QUERY = "What is Python?"  # Set to None to skip query
SUBMIT_QUERY = False  # True to submit, False to just type


def main():
    """
    Main function: Launch Comet, open Sidecar, and send query.
    """
    print("=" * 60)
    print("COMET BROWSER - PERPLEXITY SIDECAR WITH QUERY")
    print("=" * 60)
    print(f"Browser: {BROWSER_TYPE.value}")
    print(f"Target: {SIDECAR_URL}")
    if QUERY:
        print(f"Query: '{QUERY}'")
        print(f"Submit: {SUBMIT_QUERY}")
    else:
        print(f"Query: None (just open Sidecar)")
    print("=" * 60)
    
    try:
        # Create browser facade (bundles launcher, navigator, pipeline)
        browser = BrowserFactory.create(BROWSER_TYPE)
        
        # Configure pipeline
        config = PipelineConfig(
            target_url=SIDECAR_URL,  # Browser will navigate here
            load_wait_time=5,
            keep_open=True,
            activate_features=False
        )
        
        # Run pipeline (Browser facade orchestrates everything)
        print(f"\n[INFO] Running Comet pipeline...")
        result = browser.run_pipeline(
            config,
            query=QUERY,      # Pass query to pipeline
            submit=SUBMIT_QUERY  # Pass submit flag
        )
        
        if not result.success:
            print(f"[ERROR] Pipeline failed: {result.message}")
            return False
        
        print(f"\n[SUCCESS] Pipeline completed!")
        print(f"[INFO] Steps: {', '.join(result.steps_completed)}")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Main execution failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
