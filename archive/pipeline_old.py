"""
Automation Pipeline
===================
Modular pipeline for browser automation workflows.

Uses dependency injection to support different browsers and navigators.
"""

import time
from typing import Any, Optional
from browser_launcher import BrowserLauncher, BrowserFactory, BrowserType
from navigator import Navigator, NavigatorFactory, NavigatorType
import archive.comet_ui_automation as comet_ui_automation


def pipeline(
    target_url: str,
    browser_type: BrowserType = BrowserType.COMET,
    navigator_type: NavigatorType = NavigatorType.COMET,
    browser_launcher: Optional[BrowserLauncher] = None,
    driver: Optional[Any] = None,
    load_wait_time: int = 5,
    stability_wait_time: int = 2,
    keep_open: bool = False
) -> bool:
    """
    Run the automation pipeline for a single target URL.
    
    This pipeline is modular and supports different browsers through
    dependency injection. You can either:
    1. Let it create a browser launcher (specify browser_type)
    2. Provide your own launcher (browser_launcher parameter)
    3. Provide an existing driver (driver parameter)

    Args:
        target_url: URL to open (can be file:/// path)
        browser_type: Browser to use if creating new launcher
        navigator_type: Navigator to use (should match browser type)
        browser_launcher: Optional pre-created browser launcher
        driver: Optional existing WebDriver instance
        load_wait_time: Seconds to wait after navigation
        stability_wait_time: Seconds to wait before clicking assistant
        keep_open: If True, don't block for input()

    Returns:
        True if workflow completed successfully, False otherwise
        
    Examples:
        # Simple usage - pipeline creates everything
        >>> pipeline("https://example.com")
        
        # Bring your own launcher
        >>> launcher = BrowserFactory.create(BrowserType.COMET)
        >>> driver = launcher.launch_and_attach()
        >>> pipeline("https://example.com", driver=driver, keep_open=True)
        
        # Dependency injection
        >>> launcher = BrowserFactory.create(BrowserType.COMET)
        >>> pipeline("https://example.com", browser_launcher=launcher)
    """
    print("=" * 60)
    print("BROWSER AUTOMATION PIPELINE")
    print("=" * 60)
    print(f"Target URL: {target_url}")
    print(f"Browser: {browser_type.value if not driver else 'existing driver'}")
    print(f"Load wait time: {load_wait_time}s")
    print("=" * 60)

    # Determine who owns the browser (for cleanup)
    owns_browser = False
    
    try:
        # Step 1: Get or create browser driver
        if driver is None:
            print("\n[1/4] Launching browser...")
            
            if browser_launcher is None:
                # Create launcher
                browser_launcher = BrowserFactory.create(browser_type)
                owns_browser = True
            
            driver = browser_launcher.launch_and_attach()
            
            if not driver:
                print("[ERROR] Failed to launch browser")
                return False
        else:
            print("\n[1/4] Using existing browser connection...")
        
        # Step 2: Create navigator
        print(f"\n[2/5] Creating navigator ({navigator_type.value})...")
        navigator = NavigatorFactory.create(navigator_type, driver)
        
        # Step 3: Open Perplexity Sidecar (Comet-specific first page)
        if browser_type == BrowserType.COMET:
            print(f"\n[3/5] Opening Perplexity Sidecar...")
            SIDECAR_URL = "https://www.perplexity.ai/sidecar?copilot=true"
            sidecar_result = navigator.navigate_to_url(SIDECAR_URL, wait_time=3)
            if sidecar_result.success:
                print(f"[SUCCESS] Opened Sidecar: {SIDECAR_URL}")
            else:
                print(f"[WARNING] Failed to open Sidecar: {sidecar_result.message}")
            time.sleep(2)  # Give Sidecar time to load
        
        # Step 4: Navigate to target URL
        print(f"\n[4/5] Navigating to URL...")
        result = navigator.navigate_to_url(target_url, wait_time=load_wait_time)
        
        if not result.success:
            print(f"[ERROR] Navigation failed: {result.message}")
            return False
        
        # Verify navigation
        current_url = navigator.get_current_url()
        print(f"[INFO] Current URL: {current_url}")
        print(f"[SUCCESS] {result.message}")
        
        # Step 5: Activate Assistant (Comet-specific for now)
        if browser_type == BrowserType.COMET:
            print(f"\n[5/5] Activating Assistant...")
            print(f"[INFO] Waiting {stability_wait_time}s for UI to stabilize...")
            time.sleep(stability_wait_time)
            
            success = comet_ui_automation.click_assistant_button_ui()
            
            if success:
                print("\n" + "=" * 60)
                print("WORKFLOW COMPLETED SUCCESSFULLY!")
                print("=" * 60)
                print("✓ Browser launched and connected")
                print("✓ Opened Perplexity Sidecar")
                print(f"✓ Navigated to {target_url}")
                print("✓ Assistant activated")
                print("=" * 60)
            else:
                print("\n[WARNING] Failed to activate Assistant")
                # Don't fail the pipeline for this
        
        if not keep_open and owns_browser:
            print("\n[INFO] Browser will remain open for interaction")
            print("[INFO] Press Enter to close and exit...")
            input()
        
        return True

    except Exception as e:
        print(f"\n[ERROR] Pipeline failed: {e}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        # Only clean up if we own the browser
        if owns_browser and driver:
            print("\n[INFO] Closing browser connection...")
            try:
                if browser_launcher:
                    browser_launcher.quit()
                else:
                    driver.quit()
            except Exception as e:
                print(f"[WARNING] Error closing browser: {e}")