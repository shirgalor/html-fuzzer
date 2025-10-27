"""
Comet Conversion Implementation
================================
Conversion implementation for Perplexity Comet browser.

Handles sending queries and capturing responses from Perplexity Sidecar.
"""

import time
from typing import Any, Optional

# Import from parent's parent package (conversion)
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from conversion.base import BaseConversion


class CometConversion(BaseConversion):
    """
    Conversion implementation for Comet browser with Perplexity Sidecar.
    
    Uses the Sidecar interface to:
    - Send queries to the AI assistant
    - Capture and return responses
    """
    
    def __init__(self, driver: Any, navigator: Any = None):
        """
        Initialize Comet conversion handler.
        
        Args:
            driver: Selenium WebDriver attached to Comet
            navigator: CometNavigator instance (optional)
        """
        super().__init__(driver, navigator)
    
    def send_query(self, query: str, submit: bool = True) -> bool:
        """
        Send a query to Perplexity Sidecar input field.
        
        Sidecar uses a contenteditable div with id="ask-input".
        
        Args:
            query: The text to send
            submit: If True, press Enter to submit
            
        Returns:
            True if successful, False otherwise
        """
        try:
            from selenium.webdriver.common.by import By
            from selenium.webdriver.common.keys import Keys
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            from selenium.common.exceptions import StaleElementReferenceException
            
            print(f"[COMET CONVERSION] Sending query...")
            print(f"[COMET CONVERSION] Query: '{query}'")
            
            # Bring window to focus
            try:
                self.driver.switch_to.window(self.driver.current_window_handle)
                self.driver.execute_script("window.focus();")
                print(f"[COMET CONVERSION] Window focused")
                time.sleep(2)  # Give more time for page to be ready
            except Exception as e:
                print(f"[WARN] Could not focus window: {e}")
            
            # Wait for input field to be available
            print(f"[COMET CONVERSION] Looking for input field...")
            
            # Add extra wait time to ensure page is fully loaded
            print(f"[COMET CONVERSION] Waiting for page to be fully interactive...")
            time.sleep(3)
            
            # Debug: Check current URL and page state
            current_url = self.driver.current_url
            print(f"[DEBUG] Current URL: {current_url}")
            
            # Try to find the ask-input element with multiple fallback strategies
            ask_input = None
            
            # Strategy 1: Wait for Lexical editor to be ready (most reliable)
            try:
                print("[DEBUG] Strategy 1: Waiting for Lexical editor...")
                
                def wait_for_lexical_editor():
                    return self.driver.execute_script('''
                        var element = document.getElementById("ask-input");
                        return element && element.getAttribute("data-lexical-editor") === "true";
                    ''')
                
                WebDriverWait(self.driver, 10).until(lambda driver: wait_for_lexical_editor())
                ask_input = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.ID, "ask-input"))
                )
                print("[DEBUG] ✓ Strategy 1 success: Lexical editor ready")
                
            except Exception as e1:
                print(f"[DEBUG] Strategy 1 failed: {e1}")
                
                # Strategy 2: Look for ask-input by ID (less strict)
                try:
                    print("[DEBUG] Strategy 2: Looking for ask-input by ID...")
                    ask_input = WebDriverWait(self.driver, 5).until(
                        EC.presence_of_element_located((By.ID, "ask-input"))
                    )
                    # Verify it's visible and enabled
                    if ask_input.is_displayed() and ask_input.is_enabled():
                        print("[DEBUG] ✓ Strategy 2 success: Found ask-input")
                    else:
                        raise Exception("Element not interactive")
                        
                except Exception as e2:
                    print(f"[DEBUG] Strategy 2 failed: {e2}")
                    
                    # Strategy 3: Find any contenteditable with lexical attribute
                    try:
                        print("[DEBUG] Strategy 3: Looking for contenteditable with lexical...")
                        contenteditables = self.driver.find_elements(By.CSS_SELECTOR, "[contenteditable='true']")
                        print(f"[DEBUG] Found {len(contenteditables)} contenteditable elements")
                        
                        for idx, elem in enumerate(contenteditables):
                            try:
                                lexical = elem.get_attribute('data-lexical-editor')
                                elem_id = elem.get_attribute('id')
                                print(f"[DEBUG] Element {idx}: id='{elem_id}' lexical='{lexical}'")
                                
                                # Prefer ask-input, but accept any lexical editor
                                if elem_id == 'ask-input' or lexical == 'true':
                                    if elem.is_displayed() and elem.is_enabled():
                                        ask_input = elem
                                        print(f"[DEBUG] ✓ Strategy 3 success: Using element {idx}")
                                        break
                            except Exception as elem_err:
                                print(f"[DEBUG] Element {idx} check failed: {elem_err}")
                                
                        if not ask_input:
                            raise Exception("No suitable contenteditable found")
                            
                    except Exception as e3:
                        print(f"[DEBUG] Strategy 3 failed: {e3}")
                        raise Exception("All input detection strategies failed")
            
            if ask_input:
                
                print(f"[COMET CONVERSION] ✓ Found ask-input element")
                
                # Wait for element to become fully interactive
                print(f"[COMET CONVERSION] Waiting for element to be interactive...")
                try:
                    # Additional wait for element to become clickable
                    WebDriverWait(self.driver, 10).until(
                        lambda driver: ask_input.is_displayed() and ask_input.is_enabled()
                    )
                    
                    # Try multiple methods to make it interactive
                    # Method 1: Scroll to element
                    self.driver.execute_script("arguments[0].scrollIntoView(true);", ask_input)
                    time.sleep(0.5)
                    
                    # Method 2: Try to focus via JavaScript first
                    self.driver.execute_script("arguments[0].focus();", ask_input)
                    time.sleep(0.5)
                    
                    print(f"[COMET CONVERSION] Element should now be interactive")
                    
                except Exception as wait_err:
                    print(f"[COMET CONVERSION] Warning: Interactive wait failed: {wait_err}")
                
                # Clear any existing content first - try JavaScript approach first
                print(f"[COMET CONVERSION] Clearing input field...")
                
                try:
                    # Try JavaScript approach first (more reliable for contenteditable)
                    self.driver.execute_script("""
                        var element = arguments[0];
                        element.focus();
                        
                        // For Lexical editor, clear content properly
                        if (element.getAttribute('data-lexical-editor') === 'true') {
                            // Try to clear Lexical editor content
                            element.innerHTML = '<p><br></p>';
                        } else {
                            // Regular contenteditable clear
                            element.innerHTML = '';
                        }
                        
                        // Trigger input events
                        element.dispatchEvent(new Event('input', { bubbles: true }));
                        element.dispatchEvent(new Event('change', { bubbles: true }));
                    """, ask_input)
                    
                    time.sleep(0.5)
                    print(f"[COMET CONVERSION] ✓ Cleared via JavaScript")
                    
                except Exception as js_err:
                    print(f"[COMET CONVERSION] JavaScript clear failed: {js_err}")
                    # Fallback to click approach
                    try:
                        ask_input.click()
                        time.sleep(0.5)
                        ask_input.send_keys(Keys.CONTROL + "a")
                        time.sleep(0.2)
                        ask_input.send_keys(Keys.DELETE)
                        time.sleep(0.5)
                        print(f"[COMET CONVERSION] ✓ Cleared via keyboard")
                    except Exception as kb_err:
                        print(f"[COMET CONVERSION] Keyboard clear failed: {kb_err}")
                
                # Now try to type the query
                print(f"[COMET CONVERSION] Typing query...")
                
                # Try JavaScript typing first (more reliable for Lexical)
                try:
                    self.driver.execute_script("""
                        var element = arguments[0];
                        var text = arguments[1];
                        
                        element.focus();
                        
                        // For Lexical editor, simulate typing properly
                        if (element.getAttribute('data-lexical-editor') === 'true') {
                            // Clear and set content for Lexical
                            element.innerHTML = '<p>' + text + '</p>';
                        } else {
                            // Regular contenteditable
                            element.textContent = text;
                        }
                        
                        // Trigger input events
                        element.dispatchEvent(new Event('input', { bubbles: true }));
                        element.dispatchEvent(new Event('change', { bubbles: true }));
                    """, ask_input, query)
                    
                    print(f"[COMET CONVERSION] ✓ Query typed via JavaScript")
                    time.sleep(0.5)
                    
                except Exception as js_type_err:
                    print(f"[COMET CONVERSION] JavaScript typing failed: {js_type_err}")
                    # Fallback to regular send_keys
                    try:
                        ask_input.send_keys(query)
                        print(f"[COMET CONVERSION] ✓ Query typed via send_keys")
                    except Exception as sendkeys_err:
                        print(f"[COMET CONVERSION] Send keys failed: {sendkeys_err}")
                        raise Exception(f"All typing methods failed")
                
                print(f"[COMET CONVERSION] ✓ Query typed successfully")
                time.sleep(0.5)
                
                if submit:
                    print(f"[COMET CONVERSION] Submitting query...")
                    ask_input.send_keys(Keys.RETURN)
                    time.sleep(1)
                    print(f"[COMET CONVERSION] ✓ Query submitted")
                
                print(f"[COMET CONVERSION] ✓ Found input element")
                
                # Clear any existing content first
                print(f"[COMET CONVERSION] Clearing input field...")
                ask_input.click()
                time.sleep(0.5)
                
                # Select all and delete (works with Lexical editor)
                ask_input.send_keys(Keys.CONTROL + "a")
                time.sleep(0.2)
                ask_input.send_keys(Keys.DELETE)
                time.sleep(0.5)
                
                # Type the query using send_keys (should work with Lexical)
                print(f"[COMET CONVERSION] Typing query...")
                ask_input.send_keys(query)
                
                print(f"[COMET CONVERSION] ✓ Query typed successfully")
                time.sleep(0.5)
                
                if submit:
                    print(f"[COMET CONVERSION] Submitting query...")
                    ask_input.send_keys(Keys.RETURN)
                    time.sleep(1)
                    print(f"[COMET CONVERSION] ✓ Query submitted")
                
                return True
            else:
                print(f"[COMET CONVERSION] ✗ Could not find suitable input element")
                
                # Debug: Save page source for inspection
                try:
                    from pathlib import Path
                    debug_file = Path("output/debug_page_source.html")
                    debug_file.parent.mkdir(parents=True, exist_ok=True)
                    debug_file.write_text(self.driver.page_source, encoding='utf-8')
                    print(f"[DEBUG] Page source saved to: {debug_file}")
                except Exception as debug_err:
                    print(f"[WARN] Could not save debug page source: {debug_err}")
                
                return False
            
        except Exception as e:
            print(f"[COMET CONVERSION ERROR] Failed to send query: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def capture_response(self, wait_for_completion: bool = True, 
                        max_wait: float = 60.0) -> Optional[str]:
        """
        Capture the assistant's response from Perplexity Sidecar.
        
        Waits for the response to appear and extracts the text.
        
        Args:
            wait_for_completion: Wait for response to finish streaming
            max_wait: Maximum time to wait (seconds)
            
        Returns:
            The response text, or None if not found
        """
        try:
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            from selenium.common.exceptions import StaleElementReferenceException
            
            print(f"[COMET CONVERSION] Capturing response...")
            print(f"[COMET CONVERSION] Wait for completion: {wait_for_completion}")
            print(f"[COMET CONVERSION] Max wait: {max_wait}s")
            
            # Response selectors to try
            response_selectors = [
                ".prose"
            ]
            
            start_time = time.time()
            response_element = None
            
            # Try each selector
            for selector in response_selectors:
                try:
                    print(f"[COMET CONVERSION] Trying selector: {selector}")
                    wait = WebDriverWait(self.driver, 5)
                    elements = wait.until(
                        EC.presence_of_all_elements_located((By.CSS_SELECTOR, selector))
                    )
                    
                    if elements:
                        # Get the last/most recent element
                        response_element = elements[-1]
                        print(f"[COMET CONVERSION] ✓ Found response element: {selector}")
                        break
                        
                except Exception:
                    continue
            
            if not response_element:
                print(f"[COMET CONVERSION] ✗ Could not find response element")
                return None
            
            # Wait for response to complete if requested
            if wait_for_completion:
                print(f"[COMET CONVERSION] Waiting for response to complete...")
                previous_text = ""
                stable_count = 0
                
                while time.time() - start_time < max_wait:
                    try:
                        # Try to get text from current element
                        current_text = response_element.text.strip()
                    except StaleElementReferenceException:
                        print(f"[COMET CONVERSION] Element became stale, re-finding...")
                        # Re-find the response element
                        try:
                            response_element = WebDriverWait(self.driver, 10).until(
                                EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                            )
                            current_text = response_element.text.strip()
                            print(f"[COMET CONVERSION] ✓ Re-found response element")
                        except Exception as refind_err:
                            print(f"[COMET CONVERSION] Failed to re-find element: {refind_err}")
                            current_text = ""
                    except Exception as text_err:
                        print(f"[COMET CONVERSION] Error getting text: {text_err}")
                        current_text = ""
                    
                    if current_text == previous_text and current_text:
                        stable_count += 1
                        if stable_count >= 3:  # Stable for 3 checks
                            print(f"[COMET CONVERSION] ✓ Response appears complete")
                            break
                    else:
                        stable_count = 0
                        previous_text = current_text
                    
                    time.sleep(1)
                
                if time.time() - start_time >= max_wait:
                    print(f"[COMET CONVERSION] ⚠ Max wait reached")
            else:
                time.sleep(2)  # Brief wait
            
            # Get final response text
            response_text = response_element.text.strip()
            
            if response_text:
                print(f"[COMET CONVERSION] ✓ Captured response ({len(response_text)} chars)")
                print(f"[COMET CONVERSION] Preview: {response_text[:150]}...")
                return response_text
            else:
                print(f"[COMET CONVERSION] ⚠ Response element found but text is empty")
                return None
                
        except Exception as e:
            print(f"[COMET CONVERSION ERROR] Failed to capture response: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def capture_response_html(self, wait_for_completion: bool = True, 
                             max_wait: float = 60.0) -> Optional[str]:
        """
        Capture the HTML of the assistant's response.
        
        Args:
            wait_for_completion: Wait for response to finish streaming
            max_wait: Maximum time to wait (seconds)
            
        Returns:
            The response HTML, or None if not found
        """
        try:
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            
            print(f"[COMET CONVERSION] Capturing response HTML...")
            
            # Response selectors to try
            response_selectors = [
                ".prose"
            ]
            
            start_time = time.time()
            response_element = None
            
            # Try each selector
            for selector in response_selectors:
                try:
                    wait = WebDriverWait(self.driver, 5)
                    elements = wait.until(
                        EC.presence_of_all_elements_located((By.CSS_SELECTOR, selector))
                    )
                    
                    if elements:
                        response_element = elements[-1]
                        print(f"[COMET CONVERSION] ✓ Found response element for HTML: {selector}")
                        break
                        
                except Exception:
                    continue
            
            if not response_element:
                print(f"[COMET CONVERSION] ✗ Could not find response element")
                return None
            
            # Wait for response to complete if requested
            if wait_for_completion:
                print(f"[COMET CONVERSION] Waiting for HTML to stabilize...")
                previous_html = ""
                stable_count = 0
                
                while time.time() - start_time < max_wait:
                    current_html = response_element.get_attribute('innerHTML')
                    
                    if current_html == previous_html and current_html:
                        stable_count += 1
                        if stable_count >= 3:  # Stable for 3 checks
                            print(f"[COMET CONVERSION] ✓ HTML appears complete")
                            break
                    else:
                        stable_count = 0
                        previous_html = current_html
                    
                    time.sleep(1)
                
                if time.time() - start_time >= max_wait:
                    print(f"[COMET CONVERSION] ⚠ Max wait reached for HTML")
            else:
                time.sleep(2)
            
            # Get final HTML
            response_html = response_element.get_attribute('innerHTML')
            
            if response_html:
                print(f"[COMET CONVERSION] ✓ Captured HTML ({len(response_html)} chars)")
                return response_html
            else:
                print(f"[COMET CONVERSION] ⚠ Response HTML is empty")
                return None
                
        except Exception as e:
            print(f"[COMET CONVERSION ERROR] Failed to capture HTML: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def save_response_html(self, filepath: str, wait_for_completion: bool = True,
                          max_wait: float = 60.0) -> bool:
        """
        Capture and save the assistant's response as an HTML file.
        
        Args:
            filepath: Path where to save the HTML file
            wait_for_completion: Wait for response to finish streaming
            max_wait: Maximum time to wait (seconds)
            
        Returns:
            True if saved successfully, False otherwise
        """
        try:
            from pathlib import Path
            
            # Capture the HTML
            response_html = self.capture_response_html(
                wait_for_completion=wait_for_completion,
                max_wait=max_wait
            )
            
            if not response_html:
                print(f"[COMET CONVERSION] ✗ No HTML to save")
                return False
            
            # Create output directory if needed
            output_path = Path(filepath)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Create a complete HTML document
            html_document = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Perplexity Response</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            line-height: 1.6;
            max-width: 800px;
            margin: 40px auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .response-container {{
            background-color: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .metadata {{
            color: #666;
            font-size: 0.9em;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 1px solid #eee;
        }}
        code {{
            background-color: #f4f4f4;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'Courier New', Courier, monospace;
        }}
        pre {{
            background-color: #f4f4f4;
            padding: 15px;
            border-radius: 5px;
            overflow-x: auto;
        }}
        a {{
            color: #0066cc;
            text-decoration: none;
        }}
        a:hover {{
            text-decoration: underline;
        }}
    </style>
</head>
<body>
    <div class="response-container">
        <div class="metadata">
            <strong>Captured from:</strong> Perplexity Sidecar<br>
            <strong>Timestamp:</strong> {time.strftime('%Y-%m-%d %H:%M:%S')}
        </div>
        <div class="response-content">
{response_html}
        </div>
    </div>
</body>
</html>
"""
            
            # Write to file
            output_path.write_text(html_document, encoding='utf-8')
            
            print(f"[COMET CONVERSION] ✓ HTML saved to: {output_path.absolute()}")
            return True
            
        except Exception as e:
            print(f"[COMET CONVERSION ERROR] Failed to save HTML: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def save_response_text(self, filepath: str, wait_for_completion: bool = True,
                          max_wait: float = 60.0) -> bool:
        """
        Capture and save the assistant's response as a plain text file.
        
        Args:
            filepath: Path where to save the text file
            wait_for_completion: Wait for response to finish streaming
            max_wait: Maximum time to wait (seconds)
            
        Returns:
            True if saved successfully, False otherwise
        """
        try:
            from pathlib import Path
            
            # Capture the text response
            response_text = self.capture_response(
                wait_for_completion=wait_for_completion,
                max_wait=max_wait
            )
            
            if not response_text:
                print(f"[COMET CONVERSION] ✗ No text to save")
                return False
            
            # Create output directory if needed
            output_path = Path(filepath)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Create text document with metadata
            text_document = f"""PERPLEXITY ASSISTANT RESPONSE
{'=' * 70}
Captured from: Perplexity Sidecar
Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}
{'=' * 70}

{response_text}

{'=' * 70}
End of Response
"""
            
            # Write to file
            output_path.write_text(text_document, encoding='utf-8')
            
            print(f"[COMET CONVERSION] ✓ Text saved to: {output_path.absolute()}")
            return True
            
        except Exception as e:
            print(f"[COMET CONVERSION ERROR] Failed to save text: {e}")
            import traceback
            traceback.print_exc()
            return False
