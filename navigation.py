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
- show_page_elements(): Debug utility to show available page elements
"""

import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

# =============================================================================
# URL NAVIGATION
# =============================================================================

def navigate_to_url(driver, url):
    """
    Navigate to a specific URL using Selenium WebDriver.
    
    Args:
        driver: Selenium WebDriver instance
        url (str): Target URL to navigate to
        
    Returns:
        bool: True if navigation successful, False otherwise
    """
    try:
        print(f"[STEP] Navigating to URL...")
        print(f"[INFO] Target: {url}")
        
        # Perform navigation
        driver.get(url)
        time.sleep(2)  # Wait for initial load
        
        # Get results
        current_url = driver.current_url
        page_title = driver.title or "No title"
        
        print(f"[INFO] Current URL: {current_url}")
        print(f"[INFO] Page title: {page_title}")
        
        # Verify navigation success
        if url.replace('https://', '').replace('http://', '') in current_url:
            print("[SUCCESS] Navigation completed successfully")
            return True
        else:
            print(f"[WARNING] Navigation may not have reached target")
            return True  # Return True anyway, might be redirect
            
    except Exception as e:
        print(f"[ERROR] Navigation failed: {e}")
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

def click_assistant_button(driver):
    """
    Find and click Assistant button in web page content.
    Uses multiple strategies to locate Assistant elements.
    
    Args:
        driver: Selenium WebDriver instance
        
    Returns:
        bool: True if button found and clicked, False otherwise
    """
    try:
        print("[STEP] Looking for Assistant button in page content...")
        
        # Strategy 1: XPath text-based search
        xpath_selectors = [
            "//button[contains(text(), 'Assistant')]",
            "//div[contains(text(), 'Assistant')]",
            "//*[contains(text(), 'Assistant') and (@role='button' or name()='button')]"
        ]
        
        for xpath in xpath_selectors:
            try:
                elements = driver.find_elements(By.XPATH, xpath)
                for element in elements:
                    if element.is_displayed() and element.is_enabled():
                        element.click()
                        print(f"[SUCCESS] Clicked Assistant button using XPath")
                        return True
            except Exception:
                continue
        
        # Strategy 2: Search all clickable elements for Assistant text
        print("[INFO] Searching all clickable elements...")
        clickable_elements = driver.find_elements(By.CSS_SELECTOR, 
            "button, [role='button'], div[onclick], span[onclick]")
        
        for element in clickable_elements:
            try:
                text = element.text or ''
                aria_label = element.get_attribute('aria-label') or ''
                title = element.get_attribute('title') or ''
                
                # Check if any attribute contains "assistant"
                if any('assistant' in attr.lower() for attr in [text, aria_label, title]):
                    if element.is_displayed() and element.is_enabled():
                        element.click()
                        print(f"[SUCCESS] Found and clicked Assistant: '{text or aria_label or title}'")
                        return True
            except Exception:
                continue
        
        print("[INFO] No web-based Assistant button found")
        return False
        
    except Exception as e:
        print(f"[ERROR] Failed to click Assistant button: {e}")
        return False

# =============================================================================
# DEBUG UTILITIES
# =============================================================================

def show_page_elements(driver):
    """
    Debug utility to show available elements on the current page.
    
    Args:
        driver: Selenium WebDriver instance
    """
    try:
        print("\n" + "="*50)
        print("PAGE ELEMENTS DEBUG INFO")
        print("="*50)
        
        # Current page info
        print(f"URL: {driver.current_url}")
        print(f"Title: {driver.title}")
        print()
        
        # Input elements
        inputs = driver.find_elements(By.CSS_SELECTOR, "input")
        print(f"INPUT ELEMENTS ({len(inputs)} found):")
        for i, inp in enumerate(inputs[:5]):  # Show first 5
            try:
                placeholder = inp.get_attribute('placeholder') or ''
                name = inp.get_attribute('name') or ''
                inp_type = inp.get_attribute('type') or 'text'
                visible = "visible" if inp.is_displayed() else "hidden"
                print(f"  {i+1}. Type: {inp_type}, Name: '{name}', Placeholder: '{placeholder}', Status: {visible}")
            except Exception:
                print(f"  {i+1}. Error reading input")
        
        # Button elements  
        buttons = driver.find_elements(By.CSS_SELECTOR, "button")
        print(f"\nBUTTON ELEMENTS ({len(buttons)} found):")
        for i, btn in enumerate(buttons[:5]):  # Show first 5
            try:
                text = btn.text or btn.get_attribute('aria-label') or 'No text'
                visible = "visible" if btn.is_displayed() else "hidden"
                print(f"  {i+1}. Text: '{text}', Status: {visible}")
            except Exception:
                print(f"  {i+1}. Error reading button")
        
        print("="*50)
        
    except Exception as e:
        print(f"[ERROR] Failed to show page elements: {e}")

def get_page_info(driver):
    """
    Get basic information about the current page.
    
    Args:
        driver: Selenium WebDriver instance
        
    Returns:
        dict: Page information including counts of elements
    """
    try:
        return {
            'url': driver.current_url,
            'title': driver.title,
            'inputs': len(driver.find_elements(By.CSS_SELECTOR, "input")),
            'buttons': len(driver.find_elements(By.CSS_SELECTOR, "button")),
            'links': len(driver.find_elements(By.CSS_SELECTOR, "a")),
            'clickable': len(driver.find_elements(By.CSS_SELECTOR, 
                "[role='button'], [onclick], button"))
        }
    except Exception as e:
        return {'error': str(e)}

def find_assistant_candidates(driver):
    """
    Debug utility to find potential Assistant elements on page.
    
    Args:
        driver: Selenium WebDriver instance
        
    Returns:
        list: List of elements that might be Assistant buttons
    """
    try:
        print("[INFO] Searching for Assistant-related elements...")
        candidates = []
        
        all_elements = driver.find_elements(By.CSS_SELECTOR, "*")
        for element in all_elements[:100]:  # Check first 100 elements
            try:
                text = element.text or ''
                aria_label = element.get_attribute('aria-label') or ''
                title = element.get_attribute('title') or ''
                tag = element.tag_name
                
                if any('assistant' in attr.lower() for attr in [text, aria_label, title]):
                    candidates.append({
                        'tag': tag,
                        'text': text,
                        'aria_label': aria_label,
                        'title': title,
                        'visible': element.is_displayed()
                    })
            except Exception:
                continue
        
        print(f"[INFO] Found {len(candidates)} Assistant-related elements")
        return candidates
        
    except Exception as e:
        print(f"[ERROR] Failed to find Assistant candidates: {e}")
        return []