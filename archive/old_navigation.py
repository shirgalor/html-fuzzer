#!/usr/bin/env python3
"""
COMET NAVIGATION - Selenium Web Automation
==========================================

Handles web page navigation and content interaction through Selenium WebDriver.
Works with web page elements and content, not Comet's browser UI.

Functions:
- navigate_to_url(): Navigate to specified URL using Selenium
- type_in_search_bar(): Type in web page search elements using keyboard shortcuts  
- click_assistant_button(): Find and click web-based Assistant buttons
"""

import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import os
from pathlib import Path

# =============================================================================
# URL NAVIGATION
# =============================================================================
import time
from selenium import webdriver
from selenium.webdriver.chrome.webdriver import WebDriver
from typing import Tuple, Optional

# --- Helper Functions (Core Logic) ---

def _attempt_standard_navigation(driver: WebDriver, url: str) -> bool:
    """Attempts standard driver.get(url) and returns True/False on success/failure."""
    print(f"Attempting standard driver.get()...")
    try:
        driver.get(url)
        time.sleep(2)  # Wait for initial load
        print("  ✅ [SUCCESS] Standard navigation initiated.")
        return True
    except Exception as e:
        print(f"[WARN] driver.get failed: {e}")
        return False

def _fallback_js_new_tab(driver: WebDriver, url: str) -> bool:
    """Fallback 1: Attempts navigation by opening the URL in a new tab via JavaScript."""
    print(f"[INFO] Trying Fallback 1: JS window.open()...")
    try:
        driver.execute_script("window.open(arguments[0], '_blank');", url)
        time.sleep(1)
        if len(driver.window_handles) > 1:
            driver.switch_to.window(driver.window_handles[-1])
            print("[INFO] Switched to new tab.")
            time.sleep(1)
            if driver.current_url.lower().startswith('file://'):
                return True
        return False
    except Exception as e:
        print(f"  ❌ [WARN] JS window.open fallback failed: {e}")
        return False

def _fallback_cdp_navigate(driver: WebDriver, url: str) -> bool:
    """Fallback 2: Attempts navigation using the Chrome DevTools Protocol (CDP) Page.navigate."""
    print(f"[INFO] Trying Fallback 2: CDP Page.navigate...")
    try:
        driver.execute_cdp_cmd('Page.enable', {})
        driver.execute_cdp_cmd('Page.navigate', {'url': url})
        time.sleep(1.5)
        # Check success specifically for file URLs if that's the goal
        return driver.current_url.lower().startswith('file://') if url.startswith('file://') else True
    except Exception as e:
        print(f"[WARN] CDP navigate fallback failed: {e}")
        return False

def _get_and_log_page_status(driver: WebDriver) -> Tuple[str, str]:
    """Retrieves and logs the current URL and page title."""
    current_url = driver.current_url
    page_title = driver.title or "No title"
    print(f" [INFO] Current URL: {current_url}")
    print(f" [INFO] Page title: {page_title}")
    return current_url, page_title

def _verify_navigation(url: str, current_url: str) -> bool:
    """Verifies if the navigation succeeded based on the target and current URL."""
    if url.startswith('file://'):
        # Check for file URL loaded state
        if current_url.lower().startswith('file://'):
            print(" [SUCCESS] File URL loaded.")
            return True
        else:
            return False
    else:
        # Check for HTTP/HTTPS URL
        normalized_target = url.replace('https://', '').replace('http://', '')
        if normalized_target in current_url:
            print("[SUCCESS] Navigation completed successfully.")
            return True
        else:
            print("[WARNING] Navigation may have been redirected or not reached target.")
            return True # Assume partial success or redirect for non-file URLs

# --- Main Orchestration Function ---

def navigate_to_url(driver: WebDriver, url: str) -> bool:
    """
    Attempts to navigate to a URL, trying standard methods and fallbacks for file:// links.
    """
    print("\n" + "="*50)
    print(f"🌐 [STEP] Starting navigation to: {url}")
    
    try:
        # 1. Attempt standard navigation
        _attempt_standard_navigation(driver, url)

        # 2. Get status after initial attempt
        current_url, page_title = _get_and_log_page_status(driver)

        # 3. Handle File URLs with Fallbacks
        if url.startswith('file://'):
            if not _verify_navigation(url, current_url):
                print("  🟡 [WARNING] File URL failure. Trying fallbacks...")
                
                # Try Fallback 1: JS New Tab
                if _fallback_js_new_tab(driver, url):
                    current_url, _ = _get_and_log_page_status(driver)
                    return _verify_navigation(url, current_url)
                
                # Try Fallback 2: CDP Navigate
                if _fallback_cdp_navigate(driver, url):
                    current_url, _ = _get_and_log_page_status(driver)
                    return _verify_navigation(url, current_url)
                
                print("  🔴 [ERROR] Could not load file URL after fallbacks.")
                return False
            else:
                return True

        # 4. Handle HTTP/HTTPS URLs
        else:
            return _verify_navigation(url, current_url)
            
    except Exception as e:
        print(f"[ERROR] Navigation failed due to unexpected exception: {e}")
        return False
# =============================================================================
# PAGE ELEMENT INTERACTION
# =============================================================================

def type_in_search_bar(driver, text):
    """
    Type text using keyboard shortcut to focus address bar.
    Uses Ctrl+L to focus address bar then types text.
    
    Args:
        driver: Selenium WebDriver instance
        text (str): Text to type
        
    Returns:
        bool: True if typing successful, False otherwise
    """
    try:
        print(f"[STEP] Typing in address bar using keyboard shortcut...")
        print(f"[INFO] Text to type: '{text}'")
        
        # Use Ctrl+L to focus address bar (universal browser shortcut)
        print("[INFO] Using Ctrl+L to focus address bar...")
        ActionChains(driver).key_down(Keys.CONTROL).send_keys('l').key_up(Keys.CONTROL).perform()
        time.sleep(0.5)
        
        # Type the text
        ActionChains(driver).send_keys(text).perform()
        print(f"[SUCCESS] Successfully typed '{text}' in address bar")
        return True
        
    except Exception as e:
        print(f"[ERROR] Failed to type in address bar: {e}")
        return False


# =============================================================================
# LOCAL HTML OPENING
# =============================================================================

def open_local_html_files(driver, folder_path: str | os.PathLike, pattern: str = "*.html", new_tabs: bool = True, wait_per_page: float = 0.5):
    """
    Open all local HTML files in a folder as file:// URLs.

    Args:
        driver: Selenium WebDriver already attached to Comet/Chrome.
        folder_path: Folder containing HTML files.
        pattern: Glob pattern (default '*.html').
        new_tabs: Open each file in a new tab (True) or reuse current tab (False).
        wait_per_page: Seconds to wait after loading each page.

    Returns:
        list[str]: List of file:// URLs opened.
    """
    try:
        base = Path(folder_path)
        if not base.exists():
            print(f"[ERROR] HTML folder not found: {base}")
            return []

        files = sorted(base.glob(pattern))
        if not files:
            print(f"[INFO] No files matching {pattern} in {base}")
            return []

        opened = []
        for p in files:
            # Build a proper file URL (Windows-safe)
            file_url = p.resolve().as_uri()
            if new_tabs:
                # Open in new tab via JavaScript to keep Selenium session stable
                driver.execute_script("window.open(arguments[0], '_blank');", file_url)
            else:
                driver.get(file_url)
            print(f"[SUCCESS] Opened local HTML: {file_url}")
            opened.append(file_url)
            time.sleep(wait_per_page)

        # If we used new tabs, switch to the first newly opened tab
        try:
            if new_tabs and len(driver.window_handles) > 1:
                driver.switch_to.window(driver.window_handles[-len(opened)])
        except Exception:
            pass

        return opened
    except Exception as e:
        print(f"[ERROR] Failed to open local HTML files: {e}")
        return []
        
    except Exception as e:
        print(f"[ERROR] Failed to click Assistant button: {e}")
        return False
