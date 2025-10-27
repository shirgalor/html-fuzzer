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
            print(f"[DEBUG] Page title: {self.driver.title}")
            
            # Try to find the ask-input element
            try:
                wait = WebDriverWait(self.driver, 15)  # Increased from 10 to 15 seconds
                ask_input = wait.until(
                    EC.visibility_of_element_located((By.ID, "ask-input"))
                )
                
                print(f"[COMET CONVERSION] ✓ Found ask-input element")
                
                # Simple approach: Click and use ActionChains (works with Lexical)
                print(f"[COMET CONVERSION] Clicking input field and typing with ActionChains...")
                
                # Click to focus
                ask_input.click()
                time.sleep(1)  # Give time for focus
                
                # Use ActionChains to type (more reliable than send_keys for contenteditable)
                from selenium.webdriver.common.action_chains import ActionChains
                actions = ActionChains(self.driver)
                actions.send_keys(query).perform()
                
                print(f"[COMET CONVERSION] ✓ Query typed successfully")
                time.sleep(0.5)
                
                if submit:
                    print(f"[COMET CONVERSION] Submitting query...")
                    ask_input.send_keys(Keys.RETURN)
                    time.sleep(1)
                    print(f"[COMET CONVERSION] ✓ Query submitted")
                
                return True
                    
            except Exception as e:
                print(f"[COMET CONVERSION] Could not find ask-input: {e}")
                
                # Debug: Save page source for inspection
                try:
                    from pathlib import Path
                    debug_file = Path("output/debug_page_source.html")
                    debug_file.parent.mkdir(parents=True, exist_ok=True)
                    debug_file.write_text(self.driver.page_source, encoding='utf-8')
                    print(f"[DEBUG] Page source saved to: {debug_file}")
                except Exception as debug_err:
                    print(f"[WARN] Could not save debug page source: {debug_err}")
                
                # Fallback: try contenteditable
                try:
                    print(f"[COMET CONVERSION] Trying contenteditable fallback...")
                    wait = WebDriverWait(self.driver, 5)
                    contenteditable = wait.until(
                        EC.visibility_of_element_located((By.CSS_SELECTOR, "[contenteditable='true']"))
                    )
                    
                    contenteditable.click()
                    time.sleep(0.5)
                    contenteditable.send_keys(query)
                    
                    if submit:
                        contenteditable.send_keys(Keys.RETURN)
                        time.sleep(1)
                    
                    print(f"[COMET CONVERSION] ✓ Query sent via contenteditable")
                    return True
                    
                except Exception as e2:
                    print(f"[COMET CONVERSION] ✗ All methods failed: {e2}")
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
                    current_text = response_element.text.strip()
                    
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
