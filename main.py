"""
Main Entry Point
================
Opens multiple local HTML files in a single browser session using
the modular pipeline architecture.

Uses the new pipeline system which provides browser-specific workflows.
"""

import time
from pathlib import Path
from browser_launcher import BrowserFactory, BrowserType
from navigator import NavigatorFactory, NavigatorType
from pipeline import PipelineFactory, PipelineType, PipelineConfig

# Configuration
HTMLS_FOLDER = Path(__file__).parent / "htmls"
LOAD_WAIT_TIME = 2  # wait between opening tabs
STABILITY_WAIT_TIME = 2
PIPELINE_TYPE = PipelineType.COMET
BROWSER_TYPE = BrowserType.COMET
NAVIGATOR_TYPE = NavigatorType.COMET


def main():
    """
    Main function: Opens multiple local HTML files using the pipeline architecture.
    
    The workflow:
    1. Create browser launcher and navigator factory
    2. Use PipelineFactory to create Comet pipeline (opens Sidecar first)
    3. Pipeline navigates to first HTML file
    4. Manually open remaining HTML files in new tabs
    5. Pipeline activates Assistant
    """
    print("=" * 60)
    print("OPEN LOCAL HTMLS - PIPELINE ARCHITECTURE")
    print("=" * 60)
    print(f"HTMLs folder: {HTMLS_FOLDER}")
    print(f"Pipeline: {PIPELINE_TYPE.value}")
    print("=" * 60)

    if not HTMLS_FOLDER.exists():
        print(f"[ERROR] HTMLs folder not found: {HTMLS_FOLDER}")
        return False

    html_files = sorted([p for p in HTMLS_FOLDER.iterdir() if p.suffix.lower() in {".html", ".htm"}])
    if not html_files:
        print(f"[WARNING] No HTML files found in {HTMLS_FOLDER}")
        return False

    print(f"[INFO] Found {len(html_files)} HTML files")
    
    try:
        # Create browser launcher
        browser_launcher = BrowserFactory.create(BROWSER_TYPE)
        
        # Create navigator factory (callable that takes driver)
        navigator_factory = lambda driver: NavigatorFactory.create(NAVIGATOR_TYPE, driver)
        
        # Configure pipeline to open first HTML file
        first_html = html_files[0]
        config = PipelineConfig(
            target_url=first_html.as_uri(),
            load_wait_time=LOAD_WAIT_TIME,
            stability_wait_time=STABILITY_WAIT_TIME,
            keep_open=True,  # We'll handle cleanup manually
            activate_features=True  # Activate Assistant
        )
        
        # Create and run pipeline
        print(f"\n[INFO] Creating {PIPELINE_TYPE.value} pipeline...")
        pipeline = PipelineFactory.create(
            PIPELINE_TYPE,
            browser_launcher=browser_launcher,
            navigator_factory=navigator_factory,
            config=config
        )
        
        # Run pipeline (opens Sidecar, navigates to first HTML, activates Assistant)
        result = pipeline.run()
        
        if not result.success:
            print(f"[ERROR] Pipeline failed: {result.message}")
            return False
        
        # Get driver and navigator from pipeline result
        driver = result.driver
        navigator = NavigatorFactory.create(NAVIGATOR_TYPE, driver)
        
        # Open remaining HTML files in new tabs
        if len(html_files) > 1:
            print(f"\n[INFO] Opening remaining {len(html_files) - 1} HTML files in new tabs...")
            remaining_files = html_files[1:]
            
            for i, html_file in enumerate(remaining_files, 2):
                file_uri = html_file.as_uri()
                print(f"  [{i}/{len(html_files)}] {html_file.name}")
                
                nav_result = navigator.navigate_to_url(file_uri, wait_time=0.3)
                if not nav_result.success:
                    print(f"    [WARNING] Failed to open: {nav_result.message}")
            
            time.sleep(LOAD_WAIT_TIME)
        
        # Print summary
        print("\n" + "=" * 60)
        print("DONE - ALL HTML FILES OPENED")
        print("=" * 60)
        print(f"✓ Launched {BROWSER_TYPE.value}")
        print(f"✓ Opened Perplexity Sidecar")
        print(f"✓ Opened {len(html_files)} HTML files")
        print(f"✓ Activated Assistant")
        print(f"✓ Total tabs: {len(navigator.get_window_handles())}")
        print("=" * 60)
        print("[INFO] Browser will remain open for interaction")
        input("[INFO] Press Enter to close and exit... ")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Failed during execution: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        # Pipeline handles cleanup
        pass


if __name__ == "__main__":
    ok = main()
    if ok:
        print("[INFO] Completed opening of HTML files in one session")
    else:
        print("[ERROR] Opening failed or no files found")
