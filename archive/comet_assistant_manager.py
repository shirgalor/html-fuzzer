import argparse
import subprocess
import time
import pyautogui
from pathlib import Path

class CometAssistantManager:
    def __init__(self, binary_path, assistant_x=-138, assistant_y=61):
        self.binary_path = binary_path
        self.assistant_x = assistant_x
        self.assistant_y = assistant_y
        self.process = None
    
    def launch_comet(self):
        """Launch Comet browser"""
        try:
            print(f"[info] Launching Comet browser: {self.binary_path}")
            self.process = subprocess.Popen([self.binary_path])
            print("[info] Comet browser launched successfully!")
            return True
        except FileNotFoundError:
            print(f"[error] Could not find Comet browser at: {self.binary_path}")
            return False
        except Exception as e:
            print(f"[error] Failed to launch Comet browser: {e}")
            return False
    
    def wait_for_load(self, seconds=3):
        """Wait for browser to load"""
        print(f"[info] Waiting {seconds} seconds for browser to load...")
        time.sleep(seconds)
    
    def click_assistant(self):
        """Click the Assistant button at saved coordinates"""
        try:
            print(f"[info] Clicking Assistant button at position ({self.assistant_x}, {self.assistant_y})")
            pyautogui.click(self.assistant_x, self.assistant_y)
            print("[info] Successfully clicked Assistant button!")
            time.sleep(2)  # Wait for assistant to load
            return True
        except Exception as e:
            print(f"[error] Failed to click Assistant button: {e}")
            return False
    
    def find_chat_input_position(self):
        """Interactive mode to find the chat input box position"""
        print("\n" + "="*60)
        print("CHAT INPUT BOX POSITION FINDER")
        print("="*60)
        print("1. Make sure the Assistant chat is open")
        print("2. Move your mouse over the 'Ask anything...' input box")
        print("3. Press Enter when positioned correctly")
        print("="*60)
        
        input("Press Enter when your mouse is over the chat input box...")
        
        x, y = pyautogui.position()
        print(f"\nDetected chat input position: ({x}, {y})")
        
        confirm = input(f"Save chat input position ({x}, {y}) for future use? (y/n): ")
        if confirm.lower() == 'y':
            self.chat_input_x = x
            self.chat_input_y = y
            print(f"[info] Chat input position saved: ({x}, {y})")
            return True
        return False
    
    def type_in_chat(self, message):
        """Type a message in the assistant chat box"""
        try:
            # Use saved chat input position or default to calibrated coordinates
            chat_x = getattr(self, 'chat_input_x', -356)  # Updated based on calibration
            chat_y = getattr(self, 'chat_input_y', 984)   # Updated based on calibration
            
            print(f"[info] Clicking chat input box at ({chat_x}, {chat_y})")
            pyautogui.click(chat_x, chat_y)
            time.sleep(0.5)
            
            print(f"[info] Typing message: '{message}'")
            pyautogui.typewrite(message)
            time.sleep(0.5)
            
            print("[info] Pressing Enter to send message")
            pyautogui.press('enter')
            
            print("[info] Message sent successfully!")
            return True
            
        except Exception as e:
            print(f"[error] Failed to type in chat: {e}")
            return False
            return False
    
    def interactive_chat(self):
        """Interactive chat mode with the assistant"""
        print("\n" + "="*60)
        print("INTERACTIVE CHAT MODE")
        print("="*60)
        print("Type 'exit' to quit the chat")
        print("Type 'find-input' to find the chat input position")
        print("="*60)
        
        while True:
            message = input("\nYour message: ")
            
            if message.lower() == 'exit':
                break
            elif message.lower() == 'find-input':
                self.find_chat_input_position()
                continue
            elif not message.strip():
                continue
                
            success = self.type_in_chat(message)
            if success:
                print("[info] Message sent! Check the assistant for response.")
            else:
                print("[error] Failed to send message. Try 'find-input' to recalibrate.")
        
        print("[info] Chat session ended.")

    def find_assistant_position(self):
        """Interactive mode to find Assistant button position"""
        print("\n" + "="*60)
        print("ASSISTANT BUTTON POSITION FINDER")
        print("="*60)
        print("1. Make sure Comet browser is open and visible")
        print("2. Move your mouse over the Assistant button (don't click)")
        print("3. Press Enter when positioned correctly")
        print("="*60)
        
        input("Press Enter when your mouse is over the Assistant button...")
        
        x, y = pyautogui.position()
        print(f"\nDetected position: ({x}, {y})")
        
        confirm = input(f"Save position ({x}, {y}) for future use? (y/n): ")
        if confirm.lower() == 'y':
            self.assistant_x = x
            self.assistant_y = y
            print(f"[info] Assistant position saved: ({x}, {y})")
            return True
        return False
    
    def test_assistant(self):
        """Test if assistant is working"""
        print("\n" + "="*60)
        print("COMET ASSISTANT IS NOW READY!")
        print("="*60)
        print("The Assistant should now be open. You can:")
        print("1. Type questions in the assistant chat")
        print("2. Test if it responds properly")
        print("3. Use it as your AI assistant")
        print("="*60)
        
        input("\nPress Enter when you're done testing the assistant...")

def screen_shot():
    img = ImageGrab.grab(bbox=(0, 0, 1920, 1080))
    img.save("region.png")

def main():
    ap = argparse.ArgumentParser(description="Comet Assistant Manager - Launch browser and open assistant")
    ap.add_argument("--binary", default="C:\\Users\\sheerg\\AppData\\Local\\Perplexity\\Comet\\Application\\comet.exe", 
                    help="Path to Comet browser executable")
    ap.add_argument("--launch-only", action="store_true", help="Only launch browser, don't click assistant")
    ap.add_argument("--click-only", action="store_true", help="Only click assistant (browser must be running)")
    ap.add_argument("--find-position", action="store_true", help="Find and save assistant button position")
    ap.add_argument("--chat", action="store_true", help="Start interactive chat mode after opening assistant")
    ap.add_argument("--message", type=str, help="Send a single message to the assistant")
    ap.add_argument("--find-chat-input", action="store_true", help="Find and save chat input position")
    ap.add_argument("--wait-time", type=int, default=3, help="Seconds to wait for browser to load")
    
    args = ap.parse_args()
    
    # Create manager instance
    manager = CometAssistantManager(args.binary)
    
    print("="*60)
    print("COMET ASSISTANT MANAGER")
    print("="*60)
    
    # Handle different modes
    if args.find_position:
        print("[mode] Finding Assistant button position...")
        if not manager.launch_comet():
            return
        manager.wait_for_load(args.wait_time)
        manager.find_assistant_position()
        manager.test_assistant()
        
    elif args.find_chat_input:
        print("[mode] Finding chat input position...")
        print("[info] Make sure Assistant is already open!")
        print("[info] Position the mouse over the chat input box and press Enter...")
        manager.find_chat_input_position()
        
    elif args.click_only:
        print("[mode] Clicking Assistant button only...")
        if manager.click_assistant():
            if args.chat:
                manager.interactive_chat()
            elif args.message:
                manager.type_in_chat(args.message)
            else:
                manager.test_assistant()
        
    elif args.launch_only:
        print("[mode] Launching browser only...")
        if manager.launch_comet():
            manager.wait_for_load(args.wait_time)
            print("[info] Browser launched. Please click Assistant manually.")
            if args.chat:
                manager.interactive_chat()
            elif args.message:
                manager.type_in_chat(args.message)
            else:
                manager.test_assistant()
    
    else:
        # Default mode: Launch and click assistant
        print("[mode] Launch browser and click Assistant...")
        
        # Step 1: Launch browser
        if not manager.launch_comet():
            return
        
        # Step 2: Wait for load
        manager.wait_for_load(args.wait_time)
        
        # Step 3: Click assistant
        if manager.click_assistant():
            # Step 4: Handle chat options
            if args.chat:
                print("[info] Starting interactive chat mode...")
                time.sleep(2)  # Give assistant time to fully load
                manager.interactive_chat()
            elif args.message:
                print(f"[info] Sending message: '{args.message}'")
                time.sleep(2)  # Give assistant time to fully load
                manager.type_in_chat(args.message)
                manager.test_assistant()
            else:
                # Step 4: Test assistant
                manager.test_assistant()
        else:
            print("[info] Auto-click failed. Please click Assistant manually.")
            if args.chat:
                manager.interactive_chat()
            elif args.message:
                manager.type_in_chat(args.message)
            else:
                manager.test_assistant()
    
    print("[info] Script completed. Browser continues running.")

if __name__ == "__main__":
    main()
