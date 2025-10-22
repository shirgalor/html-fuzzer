"""
Comet Navigator Implementation
===============================
Navigation implementation for Perplexity Comet browser.

Handles Comet-specific navigation quirks and optimizations.
"""

from pathlib import Path
from typing import Any, List, Optional
import time

# Import from parent package's navigator
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from navigator.base import Navigator, NavigationResult


class CometNavigator(Navigator):
    """
    Navigator implementation for Comet browser.
    
    Comet is Chromium-based, so most standard Selenium navigation works,
    but we add specific fallbacks for file:// URLs and app-mode windows.
    """
    
    def __init__(self, driver: Any):
        """
        Initialize Comet navigator.
        
        Args:
            driver: Selenium WebDriver attached to Comet
        """
        super().__init__(driver)
    
    def navigate_to_url(self, url: str, wait_time: float = 2.0) -> NavigationResult:
        """
        Navigate to a URL with Comet-specific fallbacks.
        
        For file:// URLs, tries multiple strategies:
        1. Standard driver.get()
        2. window.open() in new tab
        3. CDP Page.navigate
        
        Args:
            url: Target URL
            wait_time: Wait time after navigation
        
        Returns:
            NavigationResult with success status
        """
        print(f"[STEP] Navigating to URL...")
        print(f"[INFO] Target: {url}")
        
        try:
            # Get initial URL to verify navigation actually happens
            initial_url = self.get_current_url()
            print(f"[DEBUG] Initial URL before navigation: {initial_url}")
            
            # Attempt 1: Standard navigation
            try:
                print(f"[DEBUG] Calling driver.get('{url}')...")
                self.driver.get(url)
                print(f"[DEBUG] driver.get() completed")
            except Exception as e:
                print(f"[WARN] driver.get() failed: {e}")
            
            time.sleep(wait_time)
            current_url = self.get_current_url()
            print(f"[INFO] Current URL after driver.get(): {current_url}")
            
            # Verify URL actually changed
            if current_url == initial_url and current_url != url:
                print(f"[ERROR] URL did not change! Still at: {current_url}")
                print(f"[ERROR] Expected: {url}")
                # Force navigation using JavaScript
                print(f"[INFO] FORCING navigation via JavaScript...")
                try:
                    self.driver.execute_script(f"window.location.href = '{url}';")
                    time.sleep(wait_time + 2)
                    current_url = self.get_current_url()
                    print(f"[INFO] After forced JS navigation: {current_url}")
                except Exception as js_error:
                    print(f"[ERROR] JavaScript navigation also failed: {js_error}")
            
            # If URL still doesn't match, try one more time with replace
            if url not in current_url:
                print(f"[WARNING] URL mismatch. Trying location.replace()...")
                try:
                    self.driver.execute_script(f"window.location.replace('{url}');")
                    time.sleep(wait_time + 2)
                    current_url = self.get_current_url()
                    print(f"[INFO] After location.replace(): {current_url}")
                except Exception as replace_error:
                    print(f"[ERROR] location.replace() failed: {replace_error}")
            
            # Check if navigation succeeded
            if url.startswith('file://'):
                # For file URLs, just check if we're on a file:// URL
                if current_url.lower().startswith('file://'):
                    print("[SUCCESS] File URL loaded")
                    return NavigationResult(True, current_url, "File URL loaded successfully")
                else:
                    # Try fallback strategies for file URLs
                    print("[WARNING] File URL did not load; trying fallbacks...")
                    return self._navigate_file_url_fallback(url)
            else:
                # For HTTP(S) URLs, check if domain matches
                normalized_url = url.replace('https://', '').replace('http://', '')
                if normalized_url in current_url:
                    print("[SUCCESS] Navigation completed successfully")
                    return NavigationResult(True, current_url, "Navigation successful")
                else:
                    print(f"[WARNING] Navigation may not have reached target")
                    # Return success anyway (might be redirect)
                    return NavigationResult(True, current_url, "Navigation completed (possible redirect)")
        
        except Exception as e:
            print(f"[ERROR] Navigation failed: {e}")
            return NavigationResult(False, url, f"Navigation failed: {e}", e)
    
    def _navigate_file_url_fallback(self, url: str) -> NavigationResult:
        """
        Fallback strategies for file:// URL navigation.
        
        Args:
            url: file:// URL to navigate to
        
        Returns:
            NavigationResult
        """
        # Fallback 1: Open in new tab via JavaScript
        try:
            print("[INFO] Fallback 1: Opening in new tab via JavaScript...")
            self.driver.execute_script("window.open(arguments[0], '_blank');", url)
            time.sleep(1)
            
            # Switch to the new tab
            handles = self.get_window_handles()
            if len(handles) > 1:
                self.driver.switch_to.window(handles[-1])
                print("[INFO] Switched to new tab for file URL")
                time.sleep(1)
                
                if self.get_current_url().lower().startswith('file://'):
                    print("[SUCCESS] File URL loaded in new tab")
                    return NavigationResult(True, url, "File loaded via window.open")
        except Exception as e:
            print(f"[WARN] window.open fallback failed: {e}")
        
        # Fallback 2: Use Chrome DevTools Protocol
        try:
            print("[INFO] Fallback 2: Using CDP Page.navigate...")
            self.driver.execute_cdp_cmd('Page.enable', {})
            self.driver.execute_cdp_cmd('Page.navigate', {'url': url})
            time.sleep(1.5)
            
            if self.get_current_url().lower().startswith('file://'):
                print("[SUCCESS] File URL loaded via CDP")
                return NavigationResult(True, url, "File loaded via CDP")
        except Exception as e:
            print(f"[WARN] CDP navigate fallback failed: {e}")
        
        # All fallbacks failed
        print("[ERROR] Could not load file URL after all fallbacks")
        return NavigationResult(False, url, "All navigation fallbacks failed")
    
    def open_local_html_files(
        self,
        folder_path: Path,
        pattern: str = "*.html",
        new_tabs: bool = True,
        wait_per_page: float = 0.5
    ) -> List[str]:
        """
        Open multiple local HTML files in Comet.
        
        Args:
            folder_path: Directory containing HTML files
            pattern: Glob pattern for files
            new_tabs: Open in new tabs (True) or reuse tab (False)
            wait_per_page: Wait time between files
        
        Returns:
            List of file:// URLs opened
        """
        try:
            folder = Path(folder_path)
            if not folder.exists():
                print(f"[ERROR] HTML folder not found: {folder}")
                return []
            
            files = sorted(folder.glob(pattern))
            if not files:
                print(f"[INFO] No files matching {pattern} in {folder}")
                return []
            
            opened = []
            for file_path in files:
                # Build proper file:// URL
                file_url = file_path.resolve().as_uri()
                
                if new_tabs:
                    # Open in new tab via JavaScript (more reliable for app-mode)
                    try:
                        self.driver.execute_script("window.open(arguments[0], '_blank');", file_url)
                        print(f"[SUCCESS] Opened in new tab: {file_url}")
                        opened.append(file_url)
                    except Exception as e:
                        print(f"[ERROR] Failed to open {file_url}: {e}")
                else:
                    # Navigate current tab
                    result = self.navigate_to_url(file_url, wait_time=0.5)
                    if result.success:
                        opened.append(file_url)
                
                time.sleep(wait_per_page)
            
            # If we opened new tabs, switch to the first one
            if new_tabs and opened and len(self.get_window_handles()) > 1:
                try:
                    # Calculate index of first opened tab
                    first_new_tab_index = len(self.get_window_handles()) - len(opened)
                    self.switch_to_window_by_index(first_new_tab_index)
                    print(f"[INFO] Switched to first opened tab")
                except Exception:
                    pass
            
            return opened
        
        except Exception as e:
            print(f"[ERROR] Failed to open local HTML files: {e}")
            return []
    
    def send_query_to_sidecar(self, query: str, submit: bool = True) -> bool:
        """
        Send a query to Perplexity Sidecar input field.
        
        Sidecar uses a contenteditable div with id="ask-input", not a textarea.
        
        Args:
            query: The text to type
            submit: If True, press Enter to submit
            
        Returns:
            True if successful, False otherwise
        """
        try:
            from selenium.webdriver.common.by import By
            from selenium.webdriver.common.keys import Keys
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            
            print(f"[COMET] Looking for Sidecar input field...")
            
            # Bring window to focus and refresh page
            print(f"[COMET] Bringing window to focus...")
            try:
                self.driver.switch_to.window(self.driver.current_window_handle)
                self.driver.execute_script("window.focus();")
                
                # Refresh the page to ensure it's fully loaded
                print(f"[COMET] Refreshing page to ensure full load...")
                self.driver.refresh()
                time.sleep(3)
                print(f"[COMET] Page refreshed, current URL: {self.get_current_url()}")
            except Exception as e:
                print(f"[WARN] Could not refresh page: {e}")
            
            # Wait for page to become interactive
            print(f"[COMET] Waiting for page to become interactive...")
            time.sleep(2)
            
            # Method 1: Find by ID (ask-input) with explicit wait
            try:
                print(f"[COMET] Attempting to find element by ID: ask-input")
                
                # Wait up to 10 seconds for element to be visible
                wait = WebDriverWait(self.driver, 10)
                ask_input = wait.until(
                    EC.visibility_of_element_located((By.ID, "ask-input"))
                )
                
                print(f"[COMET] ✓ Found ask-input element by ID and it's visible!")
                
                # Click to focus
                ask_input.click()
                print(f"[COMET] Clicked on input field")
                time.sleep(0.5)
                
                # Type the query
                print(f"[COMET] Typing query: '{query}'")
                ask_input.send_keys(query)
                print(f"[COMET] ✓ Query typed successfully")
                time.sleep(0.5)
                
                if submit:
                    print(f"[COMET] Submitting query...")
                    ask_input.send_keys(Keys.RETURN)
                    time.sleep(1)
                    print(f"[COMET] ✓ Query submitted")
                
                return True
                    
            except Exception as e:
                print(f"[COMET] Could not find visible ask-input by ID: {e}")
            
            # Method 2: Find any contenteditable element with wait
            try:
                print(f"[COMET] Trying contenteditable='true' selector...")
                wait = WebDriverWait(self.driver, 5)
                contenteditable = wait.until(
                    EC.visibility_of_element_located((By.CSS_SELECTOR, "[contenteditable='true']"))
                )
                print(f"[COMET] ✓ Found visible contenteditable element!")
                
                contenteditable.click()
                time.sleep(0.5)
                
                print(f"[COMET] Typing query: '{query}'")
                contenteditable.send_keys(query)
                print(f"[COMET] ✓ Query typed successfully")
                time.sleep(0.5)
                
                if submit:
                    contenteditable.send_keys(Keys.RETURN)
                    time.sleep(1)
                    print(f"[COMET] ✓ Query submitted")
                
                return True
                    
            except Exception as e:
                print(f"[COMET] Could not find visible contenteditable: {e}")
            
            # Method 3: Find div with role="textbox"
            try:
                print(f"[COMET] Trying div[role='textbox'] selector...")
                textbox = self.driver.find_element(By.CSS_SELECTOR, "div[role='textbox']")
                print(f"[COMET] ✓ Found textbox role element!")
                
                if textbox.is_displayed():
                    textbox.click()
                    time.sleep(0.5)
                    textbox.send_keys(query)
                    print(f"[COMET] ✓ Query typed successfully")
                    
                    if submit:
                        textbox.send_keys(Keys.RETURN)
                        time.sleep(1)
                        print(f"[COMET] ✓ Query submitted")
                    
                    return True
                    
            except Exception as e:
                print(f"[COMET] Could not find textbox role: {e}")
            
            print("[COMET] ✗ Could not find any suitable input field")
            print("[COMET] The Sidecar page may not have loaded correctly")
            return False
            
        except Exception as e:
            print(f"[COMET ERROR] Failed to send query: {e}")
            import traceback
            traceback.print_exc()
            return False
