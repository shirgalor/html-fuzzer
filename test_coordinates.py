#!/usr/bin/env python3
"""
Test current Assistant button coordinates
"""

import pyautogui
import time

# Current coordinates from your script
assistant_x = -138  # From right edge
assistant_y = 61    # From top

print("Testing Assistant button coordinates...")
print(f"Current coordinates: ({assistant_x}, {assistant_y})")

# Convert negative X to absolute position
screen_width = pyautogui.size()[0]
absolute_x = screen_width + assistant_x  # -138 becomes screen_width - 138

print(f"Screen width: {screen_width}")
print(f"Absolute coordinates: ({absolute_x}, {assistant_y})")

# Show where we're about to click
print(f"\nWill click at: ({absolute_x}, {assistant_y})")
print("Make sure Comet is open and visible...")

# Countdown
for i in range(5, 0, -1):
    print(f"Clicking in {i}...")
    time.sleep(1)

# Click the Assistant button
print("Clicking now!")
pyautogui.click(absolute_x, assistant_y)
print("Click performed!")

# Check if it worked
worked = input("\nDid the Assistant button get activated? (y/n): ")
if worked.lower() == 'y':
    print("SUCCESS! Coordinates are correct!")
else:
    print("FAILED! Need to find correct coordinates...")
    print("\nLet's find the correct position:")
    input("Position your mouse over the Assistant button and press Enter...")
    
    x, y = pyautogui.position()
    print(f"New coordinates: ({x}, {y})")
    
    # Convert to relative
    relative_x = x - screen_width
    print(f"As relative from right: ({relative_x}, {y})")
    print(f"Update comet_ui_automation.py with: assistant_x = {relative_x}, assistant_y = {y}")
