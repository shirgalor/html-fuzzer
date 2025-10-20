#!/usr/bin/env python3

import time
import pyautogui

# =============================================================================
# CONFIGURATION - Calibrated Coordinates
# =============================================================================
ASSISTANT_X = -138  # From right edge of screen (negative value)
ASSISTANT_Y = 61    # From top of screen
CLICK_DURATION = 0.5  # Mouse movement duration for smoother clicks
TYPE_INTERVAL = 0.05  # Delay between keystrokes for stability

# =============================================================================
# ASSISTANT BUTTON AUTOMATION
# =============================================================================

def click_assistant_button_ui():
    """
    Click Comet's Assistant button using calibrated coordinates.
    
    Returns:
        bool: True if click was successful, False otherwise
    """
    try:
        print("[STEP] Activating Assistant button...")
        
        # Stability wait
        time.sleep(1)
        
        # Convert relative coordinates to absolute screen position
        screen_width = pyautogui.size()[0]
        absolute_x = screen_width + ASSISTANT_X if ASSISTANT_X < 0 else ASSISTANT_X
        
        print(f"[INFO] Screen resolution: {screen_width}x{pyautogui.size()[1]}")
        print(f"[INFO] Converting relative ({ASSISTANT_X}, {ASSISTANT_Y}) to absolute ({absolute_x}, {ASSISTANT_Y})")
        
        # Move to position smoothly, then click
        print(f"[INFO] Moving to Assistant button position...")
        pyautogui.moveTo(absolute_x, ASSISTANT_Y, duration=CLICK_DURATION)
        time.sleep(0.2)
        
        print(f"[INFO] Clicking Assistant button...")
        pyautogui.click(absolute_x, ASSISTANT_Y)
        
        print("[SUCCESS] Assistant button clicked successfully!")
        print("[INFO] Waiting for Assistant to load...")
        time.sleep(3)
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Failed to click Assistant button: {e}")
        return False

# =============================================================================
# ADDRESS BAR AUTOMATION  
# =============================================================================

def type_in_address_bar_ui(text):
    """
    Type text in Comet's address bar using keyboard shortcuts.
    
    Args:
        text (str): Text to type in the address bar
        
    Returns:
        bool: True if typing was successful, False otherwise
    """
    try:
        print(f"[STEP] Typing in address bar: '{text}'")
        
        # Ensure window is focused
        time.sleep(0.5)
        
        # Focus address bar with Ctrl+L
        print("[INFO] Focusing address bar (Ctrl+L)...")
        pyautogui.hotkey('ctrl', 'l')
        time.sleep(1)
        
        # Clear existing content
        print("[INFO] Clearing existing content...")
        pyautogui.hotkey('ctrl', 'a')
        time.sleep(0.2)
        
        # Type new text with controlled speed
        print(f"[INFO] Typing: '{text}'")
        pyautogui.typewrite(text, interval=TYPE_INTERVAL)
        time.sleep(0.5)
        
        # Submit with Enter
        print("[INFO] Submitting (Enter)...")
        pyautogui.press('enter')
        
        print("[SUCCESS] Text typed and submitted successfully!")
        return True
        
    except Exception as e:
        print(f"[ERROR] Failed to type in address bar: {e}")
        return False

# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def find_assistant_button_coordinates():
    """
    Interactive utility to find Assistant button coordinates.
    
    Returns:
        tuple: (x, y) coordinates if successful, (None, None) otherwise
    """
    print("\n" + "="*60)
    print("ASSISTANT BUTTON COORDINATE FINDER")
    print("="*60)
    print("Instructions:")
    print("1. Make sure Comet is visible and maximized")
    print("2. Position your mouse exactly over the Assistant button")
    print("3. Press Enter to capture the coordinates")
    print("="*60)
    
    input("Press Enter when mouse is positioned over Assistant button...")
    
    x, y = pyautogui.position()
    print(f"\nCaptured coordinates: ({x}, {y})")
    
    # Convert to relative coordinates
    screen_width = pyautogui.size()[0]
    relative_x = x - screen_width
    
    print(f"Relative coordinates (from right edge): ({relative_x}, {y})")
    
    # Test the coordinates
    confirm = input(f"Test click at ({x}, {y})? (y/n): ")
    if confirm.lower() == 'y':
        print("Testing click in 3 seconds...")
        time.sleep(3)
        pyautogui.click(x, y)
        print("Test click performed!")
        return x, y
    
    return None, None

def get_screen_info():
    """Get current screen resolution and basic info."""
    width, height = pyautogui.size()
    print(f"Screen resolution: {width}x{height}")
    print(f"Current mouse position: {pyautogui.position()}")
    return width, height

# =============================================================================
# MAIN - For testing and utilities
# =============================================================================

if __name__ == "__main__":
    print("COMET UI AUTOMATION - Testing Mode")
    print("="*40)
    
    while True:
        print("\nOptions:")
        print("1. Find Assistant button coordinates")
        print("2. Test Assistant button click") 
        print("3. Test address bar typing")
        print("4. Show screen info")
        print("5. Exit")
        
        choice = input("\nSelect option (1-5): ").strip()
        
        if choice == '1':
            find_assistant_button_coordinates()
        elif choice == '2':
            click_assistant_button_ui()
        elif choice == '3':
            text = input("Enter text to type: ")
            type_in_address_bar_ui(text)
        elif choice == '4':
            get_screen_info()
        elif choice == '5':
            break
        else:
            print("Invalid option")
    
    print("Exiting...")
