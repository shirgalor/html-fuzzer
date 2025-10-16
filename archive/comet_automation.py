import argparse
import subprocess
import time
import pyautogui
import json
from pathlib import Path

class CometAutomation:
    def __init__(self, binary_path):
        self.binary_path = binary_path
        self.process = None
        
        # Calibrated coordinates (based on your screen setup)
        self.assistant_x = -138
        self.assistant_y = 61
        self.chat_input_x = -356
        self.chat_input_y = 984
        self.url_bar_x = -1716
        self.url_bar_y = 60
        self.response_area_x = -368  # Recalibrated coordinates
        self.response_area_y = 632   # Recalibrated coordinates
        
        print(f"[info] Initialized with coordinates:")
        print(f"       Assistant button: ({self.assistant_x}, {self.assistant_y})")
        print(f"       Chat input: ({self.chat_input_x}, {self.chat_input_y})")
        print(f"       URL bar: ({self.url_bar_x}, {self.url_bar_y})")
        print(f"       Response area: ({self.response_area_x}, {self.response_area_y})")
    
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
    
    def wait_for_load(self, seconds=5):
        """Wait for browser to load"""
        print(f"[info] Waiting {seconds} seconds for browser to load...")
        time.sleep(seconds)
    
    def navigate_to_url(self, url):
        """Navigate to a specific URL"""
        try:
            print(f"[step] Navigating to URL: {url}")
            print(f"[info] Clicking URL bar at ({self.url_bar_x}, {self.url_bar_y})")
            pyautogui.click(self.url_bar_x, self.url_bar_y)
            time.sleep(0.5)
            
            # Select all text in URL bar and replace it
            print("[info] Selecting current URL...")
            pyautogui.hotkey('ctrl', 'a')
            time.sleep(0.3)
            
            print(f"[info] Typing URL: {url}")
            pyautogui.typewrite(url, interval=0.02)
            time.sleep(0.5)
            
            print("[info] Pressing Enter to navigate")
            pyautogui.press('enter')
            
            print(f"[success] Successfully navigated to: {url}")
            return True
            
        except Exception as e:
            print(f"[error] Failed to navigate to URL: {e}")
            return False
    
    def click_assistant(self):
        """Click the Assistant button"""
        try:
            print(f"[step] Opening Assistant")
            print(f"[info] Clicking Assistant button at ({self.assistant_x}, {self.assistant_y})")
            pyautogui.click(self.assistant_x, self.assistant_y)
            print("[success] Successfully clicked Assistant button!")
            time.sleep(2)  # Wait for assistant to load
            return True
        except Exception as e:
            print(f"[error] Failed to click Assistant button: {e}")
            return False
    
    def send_message_to_assistant(self, message):
        """Send a message to the Assistant"""
        try:
            print(f"[step] Sending message to Assistant: '{message}'")
            print(f"[info] Clicking chat input at ({self.chat_input_x}, {self.chat_input_y})")
            pyautogui.click(self.chat_input_x, self.chat_input_y)
            time.sleep(0.5)
            
            # Clear any existing text and type the message
            pyautogui.hotkey('ctrl', 'a')  # Select all text
            time.sleep(0.2)
            
            print(f"[info] Typing message: '{message}'")
            pyautogui.typewrite(message, interval=0.02)
            time.sleep(0.5)
            
            print("[info] Pressing Enter to send message")
            pyautogui.press('enter')
            
            print("[success] Message sent successfully!")
            return True
            
        except Exception as e:
            print(f"[error] Failed to send message: {e}")
            return False
    
    def find_assistant_response_area(self):
        """Interactive mode to find the Assistant response area"""
        print("\n" + "="*70)
        print("ASSISTANT RESPONSE AREA FINDER")
        print("="*70)
        print("1. Make sure the Assistant has responded to a message")
        print("2. Move your mouse over the Assistant's response text")
        print("3. Position it in the middle of the response area")
        print("4. Press Enter when positioned correctly")
        print("="*70)
        
        input("Press Enter when your mouse is over the Assistant response area...")
        
        x, y = pyautogui.position()
        print(f"\nDetected response area position: ({x}, {y})")
        
        confirm = input(f"Save response area position ({x}, {y}) for future use? (y/n): ")
        if confirm.lower() == 'y':
            self.response_area_x = x
            self.response_area_y = y
            print(f"[info] Response area position saved: ({x}, {y})")
            return True
        return False
    
    def select_assistant_response(self):
        """Select the Assistant's response text for copying"""
        try:
            # Use saved response area position or default
            response_x = getattr(self, 'response_area_x', -256)  # Calibrated coordinates
            response_y = getattr(self, 'response_area_y', 529)   # Calibrated coordinates
            
            print(f"[info] Clicking response area at ({response_x}, {response_y})")
            pyautogui.click(response_x, response_y)
            time.sleep(0.5)
            
            # Try multiple methods to select the full response
            print("[info] Attempting to select full response text...")
            
            # Method 1: Use Ctrl+A to select all visible text
            print("[info] Method 1: Selecting all text with Ctrl+A...")
            pyautogui.hotkey('ctrl', 'a')
            time.sleep(1)
            
            # If that doesn't work, try clicking at the start and dragging to end
            try:
                # Click at the beginning of the response area
                start_y = response_y - 100  # Start higher up
                end_y = response_y + 200    # End lower down
                
                print(f"[info] Method 2: Drag selection from ({response_x}, {start_y}) to ({response_x}, {end_y})")
                pyautogui.click(response_x, start_y)
                time.sleep(0.3)
                pyautogui.drag(0, end_y - start_y, duration=0.5, button='left')
                time.sleep(0.5)
                
            except:
                # Fallback: Triple-click and then extend selection
                print("[info] Method 3: Triple-click and extend selection...")
                pyautogui.click(response_x, response_y, clicks=3)
                time.sleep(0.5)
                
                # Try to extend selection by holding Shift and clicking lower
                pyautogui.keyDown('shift')
                pyautogui.click(response_x, response_y + 150)
                pyautogui.keyUp('shift')
                time.sleep(0.5)
            
            return True
            
        except Exception as e:
            print(f"[error] Failed to select response: {e}")
            return False
    
    def copy_assistant_response(self):
        """Copy the Assistant's response to clipboard"""
        try:
            print("[step] Copying Assistant response...")
            
            response_x = getattr(self, 'response_area_x', -256)
            response_y = getattr(self, 'response_area_y', 529)
            
            print(f"[info] Clicking in Assistant response area at ({response_x}, {response_y})")
            pyautogui.click(response_x, response_y)
            time.sleep(1)
            
            # Try a more targeted selection approach
            print("[info] Using triple-click to select the response paragraph...")
            pyautogui.click(response_x, response_y, clicks=3)
            time.sleep(0.5)
            
            # Extend selection downward to capture more content
            print("[info] Extending selection to capture full response...")
            pyautogui.keyDown('shift')
            # Click further down to extend selection
            for i in range(5):  # Try multiple extensions
                pyautogui.click(response_x, response_y + (i * 30))
                time.sleep(0.1)
            pyautogui.keyUp('shift')
            time.sleep(0.5)
            
            # Copy to clipboard
            print("[info] Copying selected text to clipboard...")
            pyautogui.hotkey('ctrl', 'c')
            time.sleep(1)
            
            # Try multiple methods to get clipboard content
            clipboard_content = None
            
            # Method 1: Try with pyperclip (most reliable)
            try:
                import pyperclip
                clipboard_content = pyperclip.paste()
                print(f"[info] Pyperclip retrieved {len(clipboard_content)} characters")
                
                # Clean up the content - remove command lines and focus on actual AI response
                if clipboard_content:
                    lines = clipboard_content.split('\n')
                    cleaned_lines = []
                    
                    for line in lines:
                        # Skip lines that look like commands or file paths
                        if any(skip_phrase in line.lower() for skip_phrase in [
                            'python comet_automation.py',
                            'c:\\users\\',
                            '--workflow',
                            '--save-workflow'
                        ]):
                            continue
                        # Keep lines that look like actual content
                        if line.strip() and not line.startswith('['):
                            cleaned_lines.append(line.strip())
                    
                    if cleaned_lines:
                        cleaned_content = '\n'.join(cleaned_lines)
                        print(f"[info] Cleaned response: {len(cleaned_content)} characters")
                        return cleaned_content
                    
            except ImportError:
                print("[info] pyperclip not available, trying alternatives...")
                
            # Method 2: PowerShell Get-Clipboard (Windows-specific)
            try:
                import subprocess
                result = subprocess.run(['powershell', '-command', 'Get-Clipboard'], 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    clipboard_content = result.stdout.strip()
                    print(f"[info] PowerShell retrieved {len(clipboard_content)} characters")
            except Exception as ps_error:
                print(f"[info] PowerShell method failed: {ps_error}")
            
            if clipboard_content and len(clipboard_content) > 10:
                print(f"[success] Response captured: {clipboard_content[:100]}...")
                return clipboard_content
            else:
                print("[warning] No substantial content captured")
                return "No response content found. Try positioning mouse over Assistant's actual response text."
                
        except Exception as e:
            print(f"[error] Failed to copy response: {e}")
            return None
    
    def save_ai_response_to_file(self, filename=None):
        """Save the Assistant's response to a text file"""
        try:
            # Get the response text
            response = self.copy_assistant_response()
            if not response or response == "Response copied to clipboard":
                print("[error] No response content to save")
                return False
            
            # Generate filename if not provided
            if not filename:
                from datetime import datetime
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"ai_response_{timestamp}.txt"
            
            # Save to file
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(f"AI Assistant Response\n")
                f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("="*50 + "\n\n")
                f.write(response)
            
            print(f"[success] AI response saved to: {filename}")
            return filename
            
        except Exception as e:
            print(f"[error] Failed to save response: {e}")
            return False
    
    def save_conversation_log(self, question, response, filename="conversation_log.txt"):
        """Save a question-response pair to a conversation log"""
        try:
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Append to conversation log
            with open(filename, 'a', encoding='utf-8') as f:
                f.write(f"\n[{timestamp}]\n")
                f.write(f"Question: {question}\n")
                f.write(f"Response: {response}\n")
                f.write("-" * 50 + "\n")
            
            print(f"[success] Conversation saved to: {filename}")
            return True
            
        except Exception as e:
            print(f"[error] Failed to save conversation: {e}")
            return False
    
    def screenshot_ai_response(self, filename=None):
        """Take a screenshot of the AI response area"""
        try:
            from datetime import datetime
            import pyautogui
            
            # Generate filename if not provided
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"ai_response_screenshot_{timestamp}.png"
            
            # Get response area coordinates
            response_x = getattr(self, 'response_area_x', -368)
            response_y = getattr(self, 'response_area_y', 632)
            
            # Define a much larger screenshot area to capture the full response
            left = response_x - 400    # Start 400px to the left
            top = response_y - 200     # Start 200px above
            width = 1000               # Capture 1000px wide (much wider)
            height = 600               # Capture 600px tall (much taller)
            
            print(f"[info] Taking screenshot of AI response area...")
            print(f"[info] Area: left={left}, top={top}, width={width}, height={height}")
            
            # Take screenshot of the specific region
            screenshot = pyautogui.screenshot(region=(left, top, width, height))
            
            # Save the screenshot
            screenshot.save(filename)
            print(f"[success] AI response screenshot saved: {filename}")
            return filename
            
        except Exception as e:
            print(f"[error] Failed to take screenshot: {e}")
            return False
    
    def screenshot_full_conversation(self, filename=None):
        """Take a screenshot of the entire conversation area"""
        try:
            from datetime import datetime
            import pyautogui
            
            # Generate filename if not provided
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"full_conversation_screenshot_{timestamp}.png"
            
            # Take a much larger screenshot to capture the whole conversation
            left = -1000   # Start much further left
            top = 100      # Start higher up
            width = 1400   # Much wider capture
            height = 800   # Much taller capture
            
            print(f"[info] Taking full conversation screenshot...")
            print(f"[info] Area: left={left}, top={top}, width={width}, height={height}")
            
            # Take screenshot of the conversation region
            screenshot = pyautogui.screenshot(region=(left, top, width, height))
            
            # Save the screenshot
            screenshot.save(filename)
            print(f"[success] Full conversation screenshot saved: {filename}")
            return filename
            
        except Exception as e:
            print(f"[error] Failed to take full screenshot: {e}")
            return False
    
    def screenshot_full_screen(self, filename=None):
        """Take a full screen screenshot"""
        try:
            from datetime import datetime
            import pyautogui
            
            # Generate filename if not provided
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"fullscreen_screenshot_{timestamp}.png"
            
            print(f"[info] Taking full screen screenshot...")
            
            # Take full screen screenshot
            screenshot = pyautogui.screenshot()
            
            # Save the screenshot
            screenshot.save(filename)
            print(f"[success] Full screen screenshot saved: {filename}")
            return filename
            
        except Exception as e:
            print(f"[error] Failed to take full screen screenshot: {e}")
            return False
    
    def get_monitor_info(self):
        """Get information about all monitors"""
        try:
            from screeninfo import get_monitors
            
            # Get all monitors
            monitors = get_monitors()
            print(f"[info] Found {len(monitors)} monitor(s):")
            
            for i, monitor in enumerate(monitors):
                print(f"       Monitor {i}: {monitor.width}x{monitor.height} at ({monitor.x}, {monitor.y})")
                if monitor.is_primary:
                    print(f"                  (Primary monitor)")
            
            return monitors
            
        except ImportError:
            print("[info] screeninfo not available, trying alternative method...")
            try:
                import pyautogui
                
                # Get screen size (primary monitor)
                width, height = pyautogui.size()
                print(f"[info] Primary monitor: {width}x{height}")
                print("[info] Multi-monitor detection requires screeninfo package")
                return [{"width": width, "height": height, "x": 0, "y": 0}]
                
            except Exception as e:
                print(f"[error] Failed to get monitor info: {e}")
                return []
        except Exception as e:
            print(f"[error] Failed to get monitor info: {e}")
            return []
    
    def screenshot_monitor(self, monitor_index=0, filename=None):
        """Take a screenshot of a specific monitor"""
        try:
            from datetime import datetime
            import pyautogui
            
            # Generate filename if not provided
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"monitor_{monitor_index}_screenshot_{timestamp}.png"
            
            # Get monitor information
            try:
                from screeninfo import get_monitors
                monitors = get_monitors()
                
                if monitor_index >= len(monitors):
                    print(f"[error] Monitor {monitor_index} not found. Available monitors: 0-{len(monitors)-1}")
                    return False
                
                monitor = monitors[monitor_index]
                print(f"[info] Taking screenshot of monitor {monitor_index}: {monitor.width}x{monitor.height} at ({monitor.x}, {monitor.y})")
                
                # Method 1: Try PIL ImageGrab first (more reliable for multi-monitor)
                try:
                    from PIL import ImageGrab
                    bbox = (monitor.x, monitor.y, 
                           monitor.x + monitor.width, 
                           monitor.y + monitor.height)
                    print(f"[info] Using PIL ImageGrab with bbox: {bbox}")
                    screenshot = ImageGrab.grab(bbox=bbox)
                    screenshot.save(filename)
                    print(f"[success] Monitor {monitor_index} screenshot saved with PIL: {filename}")
                    return filename
                    
                except Exception as pil_error:
                    print(f"[warning] PIL method failed: {pil_error}")
                    
                    # Method 2: Try pyautogui as fallback
                    try:
                        print("[info] Trying pyautogui method...")
                        screenshot = pyautogui.screenshot(region=(monitor.x, monitor.y, monitor.width, monitor.height))
                        screenshot.save(filename)
                        print(f"[success] Monitor {monitor_index} screenshot saved with pyautogui: {filename}")
                        return filename
                        
                    except Exception as pyautogui_error:
                        print(f"[warning] PyAutoGUI method failed: {pyautogui_error}")
                        
                        # Method 3: Full screen if it's primary monitor
                        if monitor_index == 0:
                            print("[info] Fallback: Taking full screen screenshot...")
                            screenshot = pyautogui.screenshot()
                            screenshot.save(filename)
                            print(f"[success] Full screen screenshot saved: {filename}")
                            return filename
                        else:
                            print(f"[error] Cannot capture monitor {monitor_index}")
                            return False
                
            except ImportError:
                print("[info] screeninfo not available, using primary monitor...")
                if monitor_index > 0:
                    print(f"[error] Cannot access monitor {monitor_index} without screeninfo package")
                    return False
                
                # Take full screen screenshot (primary monitor only)
                screenshot = pyautogui.screenshot()
                screenshot.save(filename)
                print(f"[success] Primary monitor screenshot saved: {filename}")
                return filename
            
        except Exception as e:
            print(f"[error] Failed to take monitor screenshot: {e}")
            return False
            
        except Exception as e:
            print(f"[error] Failed to take monitor screenshot: {e}")
            return False
    
    def screenshot_ai_response_monitor(self, monitor_index=None, filename=None):
        """Take a screenshot of AI response area on a specific monitor"""
        try:
            from datetime import datetime
            import pyautogui
            
            # Generate filename if not provided
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                monitor_suffix = f"_monitor{monitor_index}" if monitor_index is not None else ""
                filename = f"ai_response{monitor_suffix}_screenshot_{timestamp}.png"
            
            # Get response area coordinates
            response_x = getattr(self, 'response_area_x', -368)
            response_y = getattr(self, 'response_area_y', 632)
            
            # If monitor index is specified, adjust coordinates for that monitor
            if monitor_index is not None:
                try:
                    from screeninfo import get_monitors
                    monitors = get_monitors()
                    
                    if monitor_index < len(monitors):
                        monitor = monitors[monitor_index]
                        # Adjust coordinates to be relative to the specified monitor
                        response_x = monitor.x + abs(response_x)
                        response_y = monitor.y + response_y
                        print(f"[info] Adjusted coordinates for monitor {monitor_index}: ({response_x}, {response_y})")
                    else:
                        print(f"[error] Monitor {monitor_index} not found")
                        return False
                        
                except ImportError:
                    print("[warning] screeninfo not available, using original coordinates")
            
            # Define a large screenshot area to capture the full response
            left = response_x - 400
            top = response_y - 200
            width = 1000
            height = 600
            
            print(f"[info] Taking AI response screenshot...")
            print(f"[info] Area: left={left}, top={top}, width={width}, height={height}")
            
            # Take screenshot of the specific region
            screenshot = pyautogui.screenshot(region=(left, top, width, height))
            
            # Save the screenshot
            screenshot.save(filename)
            print(f"[success] AI response screenshot saved: {filename}")
            return filename
            
        except Exception as e:
            print(f"[error] Failed to take AI response screenshot: {e}")
            return False
    
    def full_automation_workflow(self, url=None, message=None, wait_time=5, save_response=False, response_filename=None):
        """Complete automation workflow: Launch → Navigate → Open Assistant → Send Message → Save Response"""
        print("\n" + "="*70)
        print("COMET FULL AUTOMATION WORKFLOW")
        print("="*70)
        
        # Step 1: Launch Comet
        print("[1/5] Launching Comet browser...")
        if not self.launch_comet():
            print("[error] Failed to launch browser. Aborting workflow.")
            return False
        
        # Step 2: Wait for load
        self.wait_for_load(wait_time)
        
        # Step 3: Navigate to URL (if provided)
        if url:
            print(f"[2/5] Navigating to URL: {url}")
            if not self.navigate_to_url(url):
                print("[warning] Failed to navigate to URL, continuing...")
            time.sleep(3)  # Wait for page to load
        else:
            print("[2/5] Skipping URL navigation (no URL provided)")
        
        # Step 4: Open Assistant
        print("[3/5] Opening Assistant...")
        if not self.click_assistant():
            print("[warning] Failed to open Assistant automatically")
            input("[manual] Please click the Assistant button manually, then press Enter...")
        
        # Step 5: Send message (if provided)
        if message:
            print(f"[4/5] Sending message to Assistant...")
            time.sleep(2)  # Give assistant time to fully load
            if self.send_message_to_assistant(message):
                print("[success] Message sent successfully!")
                
                # Step 6: Save response (if requested)
                if save_response:
                    print("[5/5] Waiting for AI response and saving...")
                    print("[info] Waiting 10 seconds for AI to respond...")
                    time.sleep(10)  # Wait for AI to generate response
                    
                    saved_file = self.save_ai_response_to_file(response_filename)
                    if saved_file:
                        print(f"[success] Full workflow completed! Response saved to: {saved_file}")
                        # Also save to conversation log
                        response = self.copy_assistant_response()
                        if response and response != "Response copied to clipboard":
                            self.save_conversation_log(message, response)
                        return True
                    else:
                        print("[warning] Message sent but failed to save response")
                        return False
                else:
                    print("[5/5] Skipping response saving")
                    print("[success] Full workflow completed successfully!")
                    return True
            else:
                print("[error] Failed to send message")
                return False
        else:
            print("[4/5] Skipping message sending (no message provided)")
            print("[5/5] Skipping response saving")
            print("[success] Workflow completed! Assistant is ready for manual use.")
            return True
    
    def interactive_mode(self):
        """Interactive mode for multiple operations"""
        print("\n" + "="*70)
        print("COMET AUTOMATION - INTERACTIVE MODE")
        print("="*70)
        print("Commands:")
        print("  url <website>          - Navigate to URL")
        print("  assistant              - Open Assistant")
        print("  message <text>         - Send message to Assistant")
        print("  copy-response          - Copy Assistant's latest response")
        print("  save-response          - Save Assistant's response to file")
        print("  screenshot             - Take screenshot of AI response")
        print("  screenshot-full        - Take screenshot of full conversation")
        print("  screenshot-screen      - Take full screen screenshot")
        print("  screenshot-monitor <n> - Take screenshot of monitor N")
        print("  monitor-info           - Show monitor information")
        print("  find-response          - Find Assistant response area")
        print("  workflow <url> <msg>   - Full workflow (optional params)")
        print("  google <query>         - Search Google")
        print("  help                   - Show this help")
        print("  exit                   - Quit")
        print("="*70)
        
        while True:
            command = input("\n> ").strip()
            
            if command.lower() == 'exit':
                break
            elif command.lower() == 'help':
                print("Available commands:")
                print("  url https://example.com")
                print("  assistant")
                print("  message Hello, how are you?")
                print("  copy-response")
                print("  find-response")
                print("  workflow https://google.com What is AI?")
                print("  google python programming")
            elif command.lower() == 'assistant':
                self.click_assistant()
            elif command.lower() == 'copy-response':
                response = self.copy_assistant_response()
                if response:
                    print(f"[success] Response: {response[:200]}...")
            elif command.lower() == 'save-response':
                filename = self.save_ai_response_to_file()
                if filename:
                    print(f"[success] Response saved to: {filename}")
            elif command.lower() == 'screenshot':
                filename = self.screenshot_ai_response()
                if filename:
                    print(f"[success] Screenshot saved to: {filename}")
            elif command.lower() == 'screenshot-full':
                filename = self.screenshot_full_conversation()
                if filename:
                    print(f"[success] Full screenshot saved to: {filename}")
            elif command.lower() == 'screenshot-screen':
                filename = self.screenshot_full_screen()
                if filename:
                    print(f"[success] Full screen screenshot saved to: {filename}")
            elif command.lower() == 'monitor-info':
                self.get_monitor_info()
            elif command.lower().startswith('screenshot-monitor '):
                try:
                    monitor_num = int(command.split()[1])
                    filename = self.screenshot_monitor(monitor_num)
                    if filename:
                        print(f"[success] Monitor {monitor_num} screenshot saved to: {filename}")
                except (IndexError, ValueError):
                    print("[error] Please provide monitor number. Example: screenshot-monitor 1")
            elif command.lower() == 'find-response':
                self.find_assistant_response_area()
            elif command.lower().startswith('url '):
                url = command[4:].strip()
                if url:
                    self.navigate_to_url(url)
                else:
                    print("[error] Please provide a URL")
            elif command.lower().startswith('message '):
                msg = command[8:].strip()
                if msg:
                    self.send_message_to_assistant(msg)
                    print("[info] Tip: Use 'copy-response' to get the Assistant's answer")
                else:
                    print("[error] Please provide a message")
            elif command.lower().startswith('google '):
                query = command[7:].strip()
                if query:
                    google_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
                    self.navigate_to_url(google_url)
                else:
                    print("[error] Please provide a search query")
            elif command.lower().startswith('workflow'):
                parts = command.split(' ', 2)
                url = parts[1] if len(parts) > 1 else None
                message = parts[2] if len(parts) > 2 else None
                self.full_automation_workflow(url, message, save_response=True)
            elif not command:
                continue
            else:
                print("[error] Unknown command. Type 'help' for available commands.")
        
        print("[info] Interactive session ended.")
    
    def quick_search_and_ask(self, search_query, assistant_question):
        """Quick workflow: Search Google + Ask Assistant"""
        print(f"[workflow] Quick Search & Ask: '{search_query}' + '{assistant_question}'")
        
        # Search Google
        google_url = f"https://www.google.com/search?q={search_query.replace(' ', '+')}"
        if not self.navigate_to_url(google_url):
            return False
        
        time.sleep(3)  # Wait for search results
        
        # Open Assistant and ask question
        if self.click_assistant():
            time.sleep(2)
            return self.send_message_to_assistant(assistant_question)
        
        return False

def main():
    ap = argparse.ArgumentParser(description="Comet Full Automation - Launch, Navigate, Assistant, and Search")
    ap.add_argument("--binary", default="C:\\Users\\sheerg\\AppData\\Local\\Perplexity\\Comet\\Application\\comet.exe", 
                    help="Path to Comet browser executable")
    
    # Workflow options
    ap.add_argument("--workflow", action="store_true", help="Run full automation workflow")
    ap.add_argument("--save-workflow", action="store_true", help="Save AI response when using workflow")
    ap.add_argument("--url", type=str, help="URL to navigate to")
    ap.add_argument("--message", type=str, help="Message to send to Assistant")
    ap.add_argument("--google", type=str, help="Search Google for query")
    
    # Quick combinations
    ap.add_argument("--search-and-ask", nargs=2, metavar=('SEARCH', 'QUESTION'), 
                    help="Search Google then ask Assistant (two arguments)")
    
    # Individual actions
    ap.add_argument("--launch-only", action="store_true", help="Only launch browser")
    ap.add_argument("--assistant-only", action="store_true", help="Only open Assistant")
    ap.add_argument("--interactive", action="store_true", help="Interactive mode")
    
    # Response area functionality
    ap.add_argument("--find-response", action="store_true", help="Find Assistant response area")
    ap.add_argument("--copy-response", action="store_true", help="Copy Assistant's latest response")
    ap.add_argument("--save-response", type=str, nargs='?', const='auto', help="Save Assistant's response to file (optional filename)")
    ap.add_argument("--screenshot", type=str, nargs='?', const='auto', help="Take screenshot of AI response (optional filename)")
    ap.add_argument("--screenshot-full", type=str, nargs='?', const='auto', help="Take screenshot of full conversation (optional filename)")
    ap.add_argument("--screenshot-screen", type=str, nargs='?', const='auto', help="Take full screen screenshot (optional filename)")
    ap.add_argument("--screenshot-monitor", type=int, help="Take screenshot of specific monitor (0, 1, etc.)")
    ap.add_argument("--monitor-info", action="store_true", help="Show information about all monitors")
    
    # Settings
    ap.add_argument("--wait-time", type=int, default=5, help="Seconds to wait for browser to load")
    
    args = ap.parse_args()
    
    # Create automation instance
    automation = CometAutomation(args.binary)
    
    print("="*70)
    print("COMET AUTOMATION SUITE")
    print("="*70)
    
    # Handle different modes
    if args.find_response:
        print("[mode] Finding Assistant response area...")
        print("[info] Make sure Assistant has responded to a message first!")
        automation.find_assistant_response_area()
        
    elif args.copy_response:
        print("[mode] Copying Assistant response...")
        response = automation.copy_assistant_response()
        if response:
            print(f"[success] Response copied: {response}")
    
    elif args.save_response:
        print("[mode] Saving Assistant response...")
        filename = args.save_response if args.save_response != 'auto' else None
        saved_file = automation.save_ai_response_to_file(filename)
        if saved_file:
            print(f"[success] Response saved to: {saved_file}")
    
    elif args.screenshot:
        print("[mode] Taking screenshot of AI response...")
        filename = args.screenshot if args.screenshot != 'auto' else None
        screenshot_file = automation.screenshot_ai_response(filename)
        if screenshot_file:
            print(f"[success] Screenshot saved to: {screenshot_file}")
    
    elif args.screenshot_full:
        print("[mode] Taking full conversation screenshot...")
        filename = args.screenshot_full if args.screenshot_full != 'auto' else None
        screenshot_file = automation.screenshot_full_conversation(filename)
        if screenshot_file:
            print(f"[success] Full screenshot saved to: {screenshot_file}")
    
    elif args.screenshot_screen:
        print("[mode] Taking full screen screenshot...")
        filename = args.screenshot_screen if args.screenshot_screen != 'auto' else None
        screenshot_file = automation.screenshot_full_screen(filename)
        if screenshot_file:
            print(f"[success] Full screen screenshot saved to: {screenshot_file}")
    
    elif args.screenshot_monitor is not None:
        print(f"[mode] Taking screenshot of monitor {args.screenshot_monitor}...")
        screenshot_file = automation.screenshot_monitor(args.screenshot_monitor)
        if screenshot_file:
            print(f"[success] Monitor {args.screenshot_monitor} screenshot saved to: {screenshot_file}")
    
    elif args.monitor_info:
        print("[mode] Showing monitor information...")
        automation.get_monitor_info()
        
    elif args.search_and_ask:
        search_query, question = args.search_and_ask
        print(f"[mode] Search & Ask: '{search_query}' → '{question}'")
        if not automation.launch_comet():
            return
        automation.wait_for_load(args.wait_time)
        automation.quick_search_and_ask(search_query, question)
        
    elif args.workflow:
        print("[mode] Full automation workflow")
        save_response = args.save_workflow or args.save_response
        response_filename = args.save_response if args.save_response and args.save_response != 'auto' else None
        automation.full_automation_workflow(args.url, args.message, args.wait_time, save_response, response_filename)
        
    elif args.interactive:
        print("[mode] Interactive mode")
        if not automation.launch_comet():
            return
        automation.wait_for_load(args.wait_time)
        automation.interactive_mode()
        
    elif args.launch_only:
        print("[mode] Launch browser only")
        automation.launch_comet()
        automation.wait_for_load(args.wait_time)
        
    elif args.assistant_only:
        print("[mode] Open Assistant only")
        automation.click_assistant()
        
    elif args.google:
        print(f"[mode] Google search: {args.google}")
        if not automation.launch_comet():
            return
        automation.wait_for_load(args.wait_time)
        google_url = f"https://www.google.com/search?q={args.google.replace(' ', '+')}"
        automation.navigate_to_url(google_url)
        
    elif args.url and args.message:
        print(f"[mode] Navigate + Message: {args.url} → '{args.message}'")
        automation.full_automation_workflow(args.url, args.message, args.wait_time)
        
    elif args.url:
        print(f"[mode] Navigate to URL: {args.url}")
        if not automation.launch_comet():
            return
        automation.wait_for_load(args.wait_time)
        automation.navigate_to_url(args.url)
        
    elif args.message:
        print(f"[mode] Send message: '{args.message}'")
        if not automation.launch_comet():
            return
        automation.wait_for_load(args.wait_time)
        automation.click_assistant()
        time.sleep(2)
        automation.send_message_to_assistant(args.message)
        
    else:
        # Default: Launch and show help
        print("[mode] Launch browser and show interactive help")
        if not automation.launch_comet():
            return
        automation.wait_for_load(args.wait_time)
        print("\n[info] Browser launched! Use --interactive for interactive mode")
        print("[info] Or use --workflow for full automation")
        print("[info] Run with --help to see all options")
    
    print("\n[info] Script completed. Browser continues running.")

if __name__ == "__main__":
    main()
