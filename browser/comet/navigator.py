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
    
    def read_assistant_response(self, wait_for_completion: bool = True, max_wait: float = 60.0) -> Optional[str]:
        """
        Read the assistant's response from Perplexity Sidecar.
        
        The assistant's response appears in a message container after submitting a query.
        This method waits for the response to appear and reads the text.
        
        Args:
            wait_for_completion: If True, wait for the response to finish streaming
            max_wait: Maximum time to wait for response (seconds)
            
        Returns:
            The assistant's response text, or None if not found
        """
        try:
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            
            print(f"[COMET] Waiting for assistant response...")
            
            # Wait for response container to appear
            # Perplexity typically uses divs with specific classes for responses
            response_selectors = [
                "div[class*='answer']",
                "div[class*='response']",
                "div[class*='message']",
                "div[data-role='assistant']",
                ".prose",  # Common class for formatted text
                "[class*='markdown']"
            ]
            
            start_time = time.time()
            response_element = None
            
            # Try each selector
            for selector in response_selectors:
                try:
                    print(f"[COMET] Trying selector: {selector}")
                    wait = WebDriverWait(self.driver, 5)
                    elements = wait.until(
                        EC.presence_of_all_elements_located((By.CSS_SELECTOR, selector))
                    )
                    
                    if elements:
                        # Get the last/most recent element
                        response_element = elements[-1]
                        print(f"[COMET] ✓ Found response element with selector: {selector}")
                        break
                        
                except Exception as e:
                    print(f"[COMET] No elements with selector {selector}: {e}")
                    continue
            
            if not response_element:
                print(f"[COMET] ✗ Could not find response element")
                return None
            
            # If waiting for completion, use the intelligent streaming detector
            if wait_for_completion:
                print(f"[COMET] Waiting for response to finish streaming...")
                
                # Use the smart streaming detection
                completed = self.wait_for_response_streaming(timeout=max_wait)
                
                if not completed:
                    print(f"[COMET] ⚠ Response may not be complete, but returning current content")
            else:
                # Just wait a bit for initial content to appear
                time.sleep(2)
            
            # Get final response text
            response_text = response_element.text.strip()
            
            if response_text:
                print(f"[COMET] ✓ Got response ({len(response_text)} characters)")
                print(f"[COMET] Response preview: {response_text[:200]}...")
                return response_text
            else:
                print(f"[COMET] ⚠ Response element found but text is empty")
                return None
                
        except Exception as e:
            print(f"[COMET ERROR] Failed to read response: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def wait_for_response_streaming(self, timeout: float = 60.0) -> bool:
        """
        Intelligently wait for the assistant's response to finish streaming.
        
        Uses multiple detection methods:
        1. Monitors text length changes in the response element
        2. Checks for streaming indicators (spinners, loading states)
        3. Looks for "stop generating" button presence
        
        Args:
            timeout: Maximum time to wait (seconds)
            
        Returns:
            True if streaming completed, False if timeout
        """
        try:
            from selenium.webdriver.common.by import By
            
            print(f"[COMET] Intelligently waiting for response to complete...")
            
            # Find the response element first
            response_element = self._find_latest_response_element()
            
            if not response_element:
                print(f"[COMET] ⚠ No response element found yet")
                return False
            
            # Strategy: Monitor text length changes
            start_time = time.time()
            previous_length = 0
            stable_count = 0
            check_interval = 0.5  # Check every 500ms
            stability_threshold = 4  # Need 4 consecutive stable checks (2 seconds)
            
            print(f"[COMET] Monitoring response text changes...")
            
            while time.time() - start_time < timeout:
                try:
                    # Get current response length
                    current_text = response_element.text.strip()
                    current_length = len(current_text)
                    
                    # Check if length has changed
                    if current_length == previous_length and current_length > 0:
                        stable_count += 1
                        if stable_count >= stability_threshold:
                            print(f"[COMET] ✓ Response stable at {current_length} chars for {stable_count * check_interval:.1f}s")
                            
                            # Double-check: Look for "stop generating" button or streaming indicators
                            if self._is_actively_streaming():
                                print(f"[COMET] Still streaming (indicators detected), continuing to wait...")
                                stable_count = 0  # Reset counter
                                time.sleep(check_interval)
                                continue
                            
                            print(f"[COMET] ✓ Response complete! Final length: {current_length} chars")
                            return True
                    else:
                        # Text is still changing
                        if current_length > previous_length:
                            print(f"[COMET] Response growing: {previous_length} → {current_length} chars")
                        stable_count = 0
                        previous_length = current_length
                    
                    time.sleep(check_interval)
                    
                except Exception as e:
                    print(f"[COMET] Error reading response: {e}")
                    time.sleep(check_interval)
            
            print(f"[COMET] ⚠ Timeout reached ({timeout}s), returning anyway")
            print(f"[COMET] Final response length: {previous_length} chars")
            return False
            
        except Exception as e:
            print(f"[COMET ERROR] Error waiting for streaming: {e}")
            return False
    
    def _find_latest_response_element(self):
        """
        Find the most recent response element from the assistant.
        
        Returns:
            WebElement or None
        """
        try:
            from selenium.webdriver.common.by import By
            
            # Try multiple selectors that Perplexity might use
            selectors = [
                "div[class*='answer']",
                "div[class*='response']",
                ".prose",
                "[class*='markdown']",
                "div[class*='message']"
            ]
            
            for selector in selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    visible_elements = [el for el in elements if el.is_displayed()]
                    
                    if visible_elements:
                        # Return the last (most recent) element
                        return visible_elements[-1]
                except Exception:
                    continue
            
            return None
            
        except Exception:
            return None
    
    def _is_actively_streaming(self) -> bool:
        """
        Check if the assistant is actively streaming a response.
        
        Looks for:
        - "Stop generating" button
        - Loading/streaming indicators
        - Animated elements
        
        Returns:
            True if actively streaming, False otherwise
        """
        try:
            from selenium.webdriver.common.by import By
            
            # Check for "stop generating" button (strong indicator)
            stop_button_selectors = [
                "button[aria-label*='stop']",
                "button[class*='stop']",
                "button:contains('Stop')",
                "[class*='stop-generate']"
            ]
            
            for selector in stop_button_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if any(el.is_displayed() for el in elements):
                        return True
                except Exception:
                    continue
            
            # Check for loading/streaming indicators
            streaming_indicators = [
                "[class*='loading']",
                "[class*='streaming']",
                "[class*='spinner']",
                "[class*='animate-pulse']",
                "svg[class*='animate-spin']"
            ]
            
            for selector in streaming_indicators:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if any(el.is_displayed() for el in elements):
                        return True
                except Exception:
                    continue
            
            return False
            
        except Exception:
            return False
    
    def have_conversation(self, messages: List[str], read_responses: bool = True, 
                         wait_between_messages: float = 2.0) -> List[dict]:
        """
        Have a multi-turn conversation with the Perplexity assistant.
        
        Args:
            messages: List of messages to send to the assistant
            read_responses: If True, read and return assistant responses
            wait_between_messages: Time to wait between sending messages (seconds)
            
        Returns:
            List of dicts with format: {'role': 'user'|'assistant', 'content': str}
        """
        conversation = []
        
        try:
            for i, message in enumerate(messages):
                print(f"\n[COMET] === Turn {i+1}/{len(messages)} ===")
                print(f"[COMET] User: {message}")
                
                # Add user message to conversation
                conversation.append({
                    'role': 'user',
                    'content': message
                })
                
                # Send the message
                success = self.send_query_to_sidecar(message, submit=True)
                
                if not success:
                    print(f"[COMET] ✗ Failed to send message {i+1}")
                    conversation.append({
                        'role': 'assistant',
                        'content': '[ERROR: Failed to send message]'
                    })
                    continue
                
                # Read the response if requested
                if read_responses:
                    # Wait for streaming to complete
                    self.wait_for_response_streaming(timeout=60.0)
                    
                    # Read the response
                    response = self.read_assistant_response(
                        wait_for_completion=True,
                        max_wait=60.0
                    )
                    
                    if response:
                        print(f"[COMET] Assistant: {response[:200]}...")
                        conversation.append({
                            'role': 'assistant',
                            'content': response
                        })
                    else:
                        print(f"[COMET] ✗ Failed to read response")
                        conversation.append({
                            'role': 'assistant',
                            'content': '[ERROR: Failed to read response]'
                        })
                
                # Wait before next message (to allow time to prepare input)
                if i < len(messages) - 1:
                    print(f"[COMET] Waiting {wait_between_messages}s before next message...")
                    time.sleep(wait_between_messages)
            
            print(f"\n[COMET] === Conversation Complete ===")
            print(f"[COMET] Total turns: {len(messages)}")
            
            return conversation
            
        except Exception as e:
            print(f"[COMET ERROR] Conversation failed: {e}")
            import traceback
            traceback.print_exc()
            return conversation
