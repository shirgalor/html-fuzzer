#!/usr/bin/env python3
"""
Simple coordinate finder for Assistant button
"""

import time
import pyautogui

def find_assistant_coordinates():
    print("="*50)
    print("ASSISTANT BUTTON COORDINATE FINDER")
    print("="*50)
    print("Instructions:")
    print("1. Make sure Comet is open and visible")
    print("2. Position your mouse EXACTLY over the Assistant button")
    print("3. Press Enter to capture coordinates")
    print("="*50)
    
    input("Press Enter when mouse is over Assistant button...")
    
    # Get current mouse position
    x, y = pyautogui.position()
    print(f"\nCaptured coordinates: ({x}, {y})")
    
    # Test the coordinates
    test = input(f"Test click at ({x}, {y})? (y/n): ")
    if test.lower() == 'y':
        print("Testing click in 3 seconds...")
        time.sleep(3)
        pyautogui.click(x, y)
        print("Test click performed!")
        
        # Ask if it worked
        worked = input("Did the Assistant button get clicked? (y/n): ")
        if worked.lower() == 'y':
            print(f"SUCCESS! Use these coordinates: ({x}, {y})")
            return x, y
        else:
            print("Click didn't work. Try positioning mouse more precisely.")
            return None, None
    
    return x, y

if __name__ == "__main__":
    x, y = find_assistant_coordinates()
    if x and y:
        print(f"\nFinal coordinates: ({x}, {y})")
        
        # Show how to convert to negative (from right edge) if needed
        screen_width = pyautogui.size()[0]
        relative_x = x - screen_width
        print(f"As relative from right edge: ({relative_x}, {y})")
        
        print("\nUpdate comet_ui_automation.py with these coordinates!")
