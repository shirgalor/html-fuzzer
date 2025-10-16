#!/usr/bin/env python3
"""
Simple Comet Address Bar and Assistant Automation
Types any given address in the search/address bar and presses the Assistant button.
"""

import time
import argparse
import sys
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, NoSuchElementException

class SimpleAutomation:
    def __init__(self, driver):
        self.driver = driver
        
    def navigate_to_perplexity(self):
        """Navigate to Perplexity main page first"""
        try:
            print("[*] Navigating to Perplexity...")
            self.driver.get("https://www.perplexity.ai/")
            time.sleep(3)  # Wait for page load
            print(f"[✓] Loaded: {self.driver.title}")
            return True
        except Exception as e:
            print(f"[!] Navigation failed: {e}")
            return False
    
    def type_in_address_bar(self, address):
        """Type address in the URL/address bar using keyboard shortcut"""
        try:
            print(f"[*] Typing address: {address}")
            
            # Method 1: Use Ctrl+L to focus address bar
            print("[*] Using Ctrl+L to focus address bar...")
            ActionChains(self.driver).key_down(Keys.CONTROL).send_keys('l').key_up(Keys.CONTROL).perform()
            time.sleep(0.5)
            
            # Type the address
            ActionChains(self.driver).send_keys(address).perform()
            time.sleep(0.5)
            
            # Press Enter to navigate
            ActionChains(self.driver).send_keys(Keys.ENTER).perform()
            time.sleep(2)
            
            print(f"[✓] Navigated to: {self.driver.current_url}")
            return True
            
        except Exception as e:
            print(f"[!] Address bar typing failed: {e}")
            return False
    
    def type_in_search_box(self, query):
        """Type in the main search box on Perplexity"""
        try:
            print(f"[*] Looking for search box to type: {query}")
            
            # Wait for page to load and find search box
            wait = WebDriverWait(self.driver, 10)
            
            # Try multiple selectors for the search box
            search_selectors = [
                "textarea[placeholder*='Ask anything']",
                "input[placeholder*='Ask anything']", 
                "textarea[placeholder*='Type @ for mentions']",
                "input[type='search']",
                "textarea[data-testid*='search']",
                "input[data-testid*='search']",
                ".search-input textarea",
                ".search-input input"
            ]
            
            search_element = None
            for selector in search_selectors:
                try:
                    search_element = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
                    if search_element.is_displayed():
                        print(f"[✓] Found search box: {selector}")
                        break
                except:
                    continue
            
            if not search_element:
                print("[!] Could not find search box")
                return False
            
            # Click and type in search box
            search_element.click()
            time.sleep(0.5)
            
            search_element.clear()
            search_element.send_keys(query)
            time.sleep(0.5)
            
            print(f"[✓] Typed query: {query}")
            return True
            
        except Exception as e:
            print(f"[!] Search box typing failed: {e}")
            return False
    
    def click_assistant_button(self):
        """Click the Assistant button"""
        try:
            print("[*] Looking for Assistant button...")
            
            wait = WebDriverWait(self.driver, 10)
            
            # Try multiple ways to find Assistant button
            assistant_selectors = [
                "//button[contains(text(), 'Assistant')]",
                "//button[contains(., 'Assistant')]",
                "//*[contains(text(), 'Assistant') and (self::button or @role='button')]",
                "button[aria-label*='Assistant']",
                "[data-testid*='assistant']"
            ]
            
            assistant_element = None
            for selector in assistant_selectors:
                try:
                    if selector.startswith("//"):
                        assistant_element = wait.until(EC.element_to_be_clickable((By.XPATH, selector)))
                    else:
                        assistant_element = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
                    
                    if assistant_element.is_displayed():
                        print(f"[✓] Found Assistant button")
                        break
                except:
                    continue
            
            if not assistant_element:
                # Fallback: look for any button with "Assistant" text
                buttons = self.driver.find_elements(By.TAG_NAME, "button")
                for btn in buttons:
                    if btn.is_displayed() and "assistant" in btn.text.lower():
                        assistant_element = btn
                        print("[✓] Found Assistant button by text search")
                        break
            
            if not assistant_element:
                print("[!] Could not find Assistant button")
                return False
            
            # Scroll into view and click
            self.driver.execute_script("arguments[0].scrollIntoView(true);", assistant_element)
            time.sleep(0.3)
            
            assistant_element.click()
            time.sleep(1)
            
            print("[✓] Assistant button clicked")
            return True
            
        except Exception as e:
            print(f"[!] Assistant button click failed: {e}")
            
            # Try JavaScript click as fallback
            try:
                print("[*] Trying JavaScript click...")
                self.driver.execute_script("arguments[0].click();", assistant_element)
                print("[✓] Assistant button clicked with JavaScript")
                return True
            except:
                return False

def connect_to_comet(port=9222):
    """Connect to running Comet instance"""
    try:
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.chrome.service import Service
        
        # Get chromedriver
        driver_path = None
        try:
            import chromedriver_autoinstaller as cda
            driver_path = cda.install()
        except:
            try:
                from webdriver_manager.chrome import ChromeDriverManager
                driver_path = ChromeDriverManager().install()
            except:
                pass
        
        if not driver_path:
            print("[!] Please install: pip install chromedriver-autoinstaller")
            return None
        
        opts = Options()
        opts.debugger_address = f"127.0.0.1:{port}"
        opts.add_argument("--remote-allow-origins=*")
        
        service = Service(driver_path)
        driver = webdriver.Chrome(service=service, options=opts)
        
        print(f"[✓] Connected to Comet")
        return driver
        
    except Exception as e:
        print(f"[!] Connection failed: {e}")
        return None

def main():
    parser = argparse.ArgumentParser(description="Simple Comet Address Bar and Assistant Automation")
    parser.add_argument("--address", "-a", type=str, help="Address/URL to navigate to")
    parser.add_argument("--query", "-q", type=str, help="Query to type in search box")
    parser.add_argument("--assistant", action="store_true", help="Click Assistant button after typing")
    parser.add_argument("--port", type=int, default=9222, help="Remote debugging port")
    
    args = parser.parse_args()
    
    if not args.address and not args.query:
        print("Usage examples:")
        print("  # Navigate to URL and click Assistant:")
        print("  python simple_automation.py --address 'https://www.google.com' --assistant")
        print()
        print("  # Type query in search box and click Assistant:")
        print("  python simple_automation.py --query 'What is AI?' --assistant") 
        print()
        print("  # Just navigate to URL:")
        print("  python simple_automation.py --address 'https://www.perplexity.ai'")
        print()
        print("  # Type query without clicking Assistant:")
        print("  python simple_automation.py --query 'hello world'")
        return 1
    
    # Connect to Comet
    driver = connect_to_comet(args.port)
    if not driver:
        return 1
    
    try:
        automation = SimpleAutomation(driver)
        
        # Navigate to Perplexity first (good starting point)
        automation.navigate_to_perplexity()
        
        success = True
        
        # Handle address navigation
        if args.address:
            if not automation.type_in_address_bar(args.address):
                success = False
        
        # Handle search query
        if args.query:
            if not automation.type_in_search_box(args.query):
                success = False
        
        # Click Assistant if requested
        if args.assistant:
            if not automation.click_assistant_button():
                success = False
        
        if success:
            print("\n[✓] All operations completed successfully!")
        else:
            print("\n[!] Some operations failed - check output above")
            
        # Keep browser open
        print("[*] Browser remains open for inspection")
        
    except KeyboardInterrupt:
        print("\n[*] Interrupted by user")
    except Exception as e:
        print(f"\n[!] Error: {e}")
    
    return 0

if __name__ == "__main__":
    exit(main())
