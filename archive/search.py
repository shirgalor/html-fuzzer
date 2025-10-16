import argparse
import subprocess
import time
import pyautogui
import json
from pathlib import Path

class CometSearchManager:
    def __init__(self, binary_path):
        self.binary_path = binary_path
        self.process = None
        self.config_file = Path("comet_search_config.json")
        
        # Load saved coordinates
        self.url_bar_x, self.url_bar_y = self.load_coordinates()
    
    def load_coordinates(self):
        """Load saved URL bar coordinates from config file"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    x = config.get('url_bar_x')
                    y = config.get('url_bar_y')
                    if x is not None and y is not None:
                        print(f"[info] Loaded saved URL bar position: ({x}, {y})")
                        return x, y
        except Exception as e:
            print(f"[warning] Could not load coordinates: {e}")
        
        # Return calibrated default coordinates
        print(f"[info] Using calibrated default URL bar position: (-1716, 60)")
        return -1716, 60
    
    def save_coordinates(self, x, y):
        """Save URL bar coordinates to config file"""
        try:
            config = {
                'url_bar_x': x,
                'url_bar_y': y
            }
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
            print(f"[info] Coordinates saved to {self.config_file}")
            return True
        except Exception as e:
            print(f"[error] Could not save coordinates: {e}")
            return False
    
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
    
    def find_url_bar_position(self):
        """Interactive mode to find the URL/address bar position"""
        print("\n" + "="*60)
        print("URL BAR POSITION FINDER")
        print("="*60)
        print("1. Make sure Comet browser is open and visible")
        print("2. Move your mouse over the URL/address bar")
        print("3. The URL bar is usually at the top of the browser window")
        print("4. Press Enter when positioned correctly")
        print("="*60)
        
        input("Press Enter when your mouse is over the URL bar...")
        
        x, y = pyautogui.position()
        print(f"\nDetected URL bar position: ({x}, {y})")
        
        confirm = input(f"Save URL bar position ({x}, {y}) for future use? (y/n): ")
        if confirm.lower() == 'y':
            self.url_bar_x = x
            self.url_bar_y = y
            if self.save_coordinates(x, y):
                print(f"[info] URL bar position saved: ({x}, {y})")
                return True
        return False
    
    def navigate_to_url(self, url):
        """Navigate to a specific URL"""
        try:
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
            
            print(f"[info] Successfully navigated to: {url}")
            return True
            
        except Exception as e:
            print(f"[error] Failed to navigate to URL: {e}")
            return False
    
    def search_google(self, query):
        """Search Google for a specific query"""
        google_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
        return self.navigate_to_url(google_url)
    
    def open_website(self, domain):
        """Open a specific website (adds https:// if needed)"""
        if not domain.startswith(('http://', 'https://')):
            url = f"https://{domain}"
        else:
            url = domain
        return self.navigate_to_url(url)
    
    def interactive_search(self):
        """Interactive mode for searching/navigating"""
        print("\n" + "="*60)
        print("INTERACTIVE SEARCH MODE")
        print("="*60)
        print("Commands:")
        print("  url <website>     - Navigate to specific URL")
        print("  google <query>    - Search Google")
        print("  find-bar          - Find URL bar position")
        print("  exit              - Quit")
        print("="*60)
        
        while True:
            command = input("\nEnter command: ").strip()
            
            if command.lower() == 'exit':
                break
            elif command.lower() == 'find-bar':
                self.find_url_bar_position()
                continue
            elif command.lower().startswith('url '):
                url = command[4:].strip()
                if url:
                    self.navigate_to_url(url)
                else:
                    print("[error] Please provide a URL. Example: url https://example.com")
            elif command.lower().startswith('google '):
                query = command[7:].strip()
                if query:
                    self.search_google(query)
                else:
                    print("[error] Please provide a search query. Example: google python programming")
            elif not command:
                continue
            else:
                print("[error] Unknown command. Type 'exit' to quit.")
        
        print("[info] Search session ended.")
    
    def test_url_bar(self):
        """Test if URL bar position is working"""
        print("\n" + "="*60)
        print("URL BAR TEST")
        print("="*60)
        print("Testing URL bar position...")
        
        if self.url_bar_x is None or self.url_bar_y is None:
            print("[info] URL bar position not set. Please find it first.")
            return self.find_url_bar_position()
        
        # Test by clicking the URL bar
        try:
            print(f"[info] Testing click at ({self.url_bar_x}, {self.url_bar_y})")
            pyautogui.click(self.url_bar_x, self.url_bar_y)
            time.sleep(1)
            print("[info] URL bar clicked successfully!")
            
            # Test typing
            test_url = "https://example.com"
            pyautogui.hotkey('ctrl', 'a')
            time.sleep(0.3)
            pyautogui.typewrite(test_url)
            time.sleep(1)
            
            confirm = input("\nDid the URL appear in the address bar? (y/n): ")
            if confirm.lower() == 'y':
                print("[info] URL bar test successful!")
                # Clear the test URL
                pyautogui.hotkey('ctrl', 'a')
                pyautogui.press('delete')
                return True
            else:
                print("[info] URL bar test failed. Please recalibrate position.")
                return False
                
        except Exception as e:
            print(f"[error] URL bar test failed: {e}")
            return False

def main():
    ap = argparse.ArgumentParser(description="Comet Search Manager - Navigate to URLs and search")
    ap.add_argument("--binary", default="C:\\Users\\sheerg\\AppData\\Local\\Perplexity\\Comet\\Application\\comet.exe", 
                    help="Path to Comet browser executable")
    ap.add_argument("--launch-only", action="store_true", help="Only launch browser")
    ap.add_argument("--find-url-bar", action="store_true", help="Find and save URL bar position")
    ap.add_argument("--url", type=str, help="Navigate to specific URL")
    ap.add_argument("--google", type=str, help="Search Google for query")
    ap.add_argument("--website", type=str, help="Open website (adds https:// automatically)")
    ap.add_argument("--interactive", action="store_true", help="Start interactive search mode")
    ap.add_argument("--test", action="store_true", help="Test URL bar position")
    ap.add_argument("--wait-time", type=int, default=5, help="Seconds to wait for browser to load")
    
    args = ap.parse_args()
    
    # Create manager instance
    manager = CometSearchManager(args.binary)
    
    print("="*60)
    print("COMET SEARCH MANAGER")
    print("="*60)
    
    # Handle different modes
    if args.find_url_bar:
        print("[mode] Finding URL bar position...")
        if not manager.launch_comet():
            return
        manager.wait_for_load(args.wait_time)
        manager.find_url_bar_position()
        
    elif args.test:
        print("[mode] Testing URL bar...")
        manager.test_url_bar()
        
    elif args.launch_only:
        print("[mode] Launching browser only...")
        manager.launch_comet()
        manager.wait_for_load(args.wait_time)
        print("[info] Browser launched. Ready for manual navigation.")
        
    elif args.url:
        print(f"[mode] Navigating to URL: {args.url}")
        if not manager.launch_comet():
            return
        manager.wait_for_load(args.wait_time)
        manager.navigate_to_url(args.url)
        
    elif args.google:
        print(f"[mode] Searching Google: {args.google}")
        if not manager.launch_comet():
            return
        manager.wait_for_load(args.wait_time)
        manager.search_google(args.google)
        
    elif args.website:
        print(f"[mode] Opening website: {args.website}")
        if not manager.launch_comet():
            return
        manager.wait_for_load(args.wait_time)
        manager.open_website(args.website)
        
    elif args.interactive:
        print("[mode] Interactive search mode...")
        if not manager.launch_comet():
            return
        manager.wait_for_load(args.wait_time)
        manager.interactive_search()
        
    else:
        # Default mode: Launch and find URL bar
        print("[mode] Launch browser and find URL bar...")
        if not manager.launch_comet():
            return
        manager.wait_for_load(args.wait_time)
        manager.find_url_bar_position()
    
    print("[info] Script completed. Browser continues running.")

if __name__ == "__main__":
    main()
