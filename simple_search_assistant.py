#!/usr/bin/env python3
"""
Simple script to type in search bar and press Assistant button
Usage: python simple_search_assistant.py
"""

import time
import sys
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def connect_to_comet():
    """Connect to running Comet instance"""
    try:
        # Get chromedriver
        try:
            import chromedriver_autoinstaller as cda
            driver_path = cda.install()
        except:
            from webdriver_manager.chrome import ChromeDriverManager
            driver_path = ChromeDriverManager().install()
        
        # Connect to Comet's remote debugging port
        opts = Options()
        opts.debugger_address = "127.0.0.1:9222"
        opts.add_argument("--remote-allow-origins=*")
        
        service = Service(driver_path)
        driver = webdriver.Chrome(service=service, options=opts)
        
        print("[✓] Connected to Comet successfully!")
        return driver
        
    except Exception as e:
        print(f"[✗] Failed to connect to Comet: {e}")
        print("Make sure Comet is running with remote debugging enabled")
        return None

def type_in_search_bar(driver, text="hello world"):
    """Type text in the search bar"""
    try:
        print(f"[*] Typing '{text}' in search bar...")
        
        # Multiple strategies to find and use the search bar
        
        # Strategy 1: Look for common search input selectors
        search_selectors = [
            "input[type='search']",
            "input[placeholder*='search']", 
            "input[placeholder*='Search']",
            "input[aria-label*='search']",
            "input[name*='search']",
            "input[id*='search']",
            ".search-input",
            "[data-testid*='search']"
        ]
        
        search_found = False
        for selector in search_selectors:
            try:
                search_input = WebDriverWait(driver, 2).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                )
                search_input.clear()
                search_input.send_keys(text)
                print(f"[✓] Successfully typed in search bar using: {selector}")
                search_found = True
                break
            except:
                continue
        
        # Strategy 2: Use keyboard shortcut to focus address bar
        if not search_found:
            print("[*] Trying Ctrl+L shortcut to focus address bar...")
            ActionChains(driver).key_down(Keys.CONTROL).send_keys('l').key_up(Keys.CONTROL).perform()
            time.sleep(0.5)
            ActionChains(driver).send_keys(text).perform()
            search_found = True
            print(f"[✓] Typed using keyboard shortcut")
        
        # Strategy 3: Try to find any input field and type there
        if not search_found:
            print("[*] Looking for any input field...")
            try:
                inputs = driver.find_elements(By.CSS_SELECTOR, "input")
                for inp in inputs:
                    if inp.is_displayed() and inp.is_enabled():
                        inp.click()
                        inp.clear()
                        inp.send_keys(text)
                        print(f"[✓] Typed in input field")
                        search_found = True
                        break
            except:
                pass
        
        if not search_found:
            print("[✗] Could not find search bar")
            return False
            
        return True
        
    except Exception as e:
        print(f"[✗] Error typing in search bar: {e}")
        return False

def press_assistant_button(driver):
    """Find and click the Assistant button"""
    try:
        print("[*] Looking for Assistant button...")
        
        # Multiple strategies to find the Assistant button
        assistant_selectors = [
            "button[aria-label*='Assistant']",
            "button[title*='Assistant']", 
            "button:contains('Assistant')",
            "[data-testid*='assistant']",
            ".assistant-button",
            "button[class*='assistant']",
            # Generic button selectors to try
            "button",
            "[role='button']"
        ]
        
        assistant_found = False
        
        # Try specific Assistant selectors first
        for selector in assistant_selectors[:6]:  # First 6 are specific
            try:
                if ":contains" in selector:
                    # Use XPath for text-based search
                    buttons = driver.find_elements(By.XPATH, "//button[contains(text(), 'Assistant')]")
                    if buttons:
                        button = buttons[0]
                    else:
                        continue
                else:
                    button = WebDriverWait(driver, 2).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                    )
                
                if button.is_displayed() and button.is_enabled():
                    button.click()
                    print(f"[✓] Successfully clicked Assistant button using: {selector}")
                    assistant_found = True
                    break
                    
            except:
                continue
        
        # If not found, try to find any button that might be Assistant
        if not assistant_found:
            print("[*] Trying to find Assistant button by text content...")
            try:
                buttons = driver.find_elements(By.CSS_SELECTOR, "button")
                for button in buttons:
                    try:
                        button_text = button.get_attribute('aria-label') or button.text or button.get_attribute('title') or ''
                        if 'assistant' in button_text.lower() or 'ai' in button_text.lower():
                            if button.is_displayed() and button.is_enabled():
                                button.click()
                                print(f"[✓] Clicked button with text: '{button_text}'")
                                assistant_found = True
                                break
                    except:
                        continue
            except:
                pass
        
        # If still not found, show available buttons for debugging
        if not assistant_found:
            print("[*] Assistant button not found. Available buttons:")
            try:
                buttons = driver.find_elements(By.CSS_SELECTOR, "button")[:10]  # Show first 10
                for i, button in enumerate(buttons):
                    try:
                        text = button.text or button.get_attribute('aria-label') or button.get_attribute('title') or f"Button {i+1}"
                        print(f"    - {text}")
                    except:
                        print(f"    - Button {i+1} (no text)")
            except:
                pass
            return False
        
        return True
        
    except Exception as e:
        print(f"[✗] Error clicking Assistant button: {e}")
        return False

def main():
    print("="*50)
    print("COMET SEARCH & ASSISTANT AUTOMATION")
    print("="*50)
    
    # Step 1: Connect to Comet
    driver = connect_to_comet()
    if not driver:
        print("\n[✗] Cannot proceed without Comet connection")
        print("Make sure:")
        print("1. Comet is running")
        print("2. Comet was launched with --remote-debugging-port=9222")
        sys.exit(1)
    
    try:
        # Show current page info
        print(f"\n[*] Current page: {driver.title}")
        print(f"[*] Current URL: {driver.current_url}")
        
        # Step 2: Type in search bar
        success = type_in_search_bar(driver, "hello world")
        if not success:
            print("[!] Failed to type in search bar")
        
        time.sleep(1)  # Brief pause
        
        # Step 3: Press Assistant button
        success = press_assistant_button(driver)
        if not success:
            print("[!] Failed to click Assistant button")
        
        print("\n[*] Task completed!")
        print("[*] Keeping browser open for inspection...")
        print("[*] Press Ctrl+C to close")
        
        # Keep open for manual inspection
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n[*] Closing...")
            
    finally:
        try:
            driver.quit()
        except:
            pass

if __name__ == "__main__":
    main()
