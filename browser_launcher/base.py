"""
Abstract Base Classes for Browser Launchers
============================================
Defines the interface that all browser launchers must implement.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, List, Dict, Any
import subprocess
import time
import requests


@dataclass
class BrowserConfig:
    """Configuration for browser launching"""
    executable_path: Path
    debug_port: int = 9222
    start_maximized: bool = True
    allow_file_access: bool = True
    disable_web_security: bool = False
    user_data_dir: Optional[Path] = None
    extra_args: List[str] = field(default_factory=list)
    timeout: float = 12.0
    
    def __post_init__(self):
        """Validate configuration after initialization"""
        if not isinstance(self.executable_path, Path):
            self.executable_path = Path(self.executable_path)
        if self.user_data_dir and not isinstance(self.user_data_dir, Path):
            self.user_data_dir = Path(self.user_data_dir)


class BrowserLauncher(ABC):
    """
    Abstract base class for browser launchers.
    
    All browser implementations must inherit from this class and implement
    the abstract methods.
    """
    
    def __init__(self, config: BrowserConfig):
        """
        Initialize the browser launcher.
        
        Args:
            config: Browser configuration object
        """
        self.config = config
        self.process: Optional[subprocess.Popen] = None
        self.driver = None
        
    @abstractmethod
    def get_launch_args(self) -> List[str]:
        """
        Get browser-specific launch arguments.
        
        Returns:
            List of command-line arguments for launching the browser
        """
        pass
    
    @abstractmethod
    def get_process_names(self) -> List[str]:
        """
        Get the process names associated with this browser.
        
        Returns:
            List of process names to look for when killing processes
        """
        pass
    
    def kill_existing_processes(self) -> int:
        """
        Kill any existing browser processes.
        
        Returns:
            Number of processes killed
        """
        try:
            import psutil
        except ImportError:
            print("[WARN] psutil not installed - cannot kill existing processes")
            return 0
        
        killed_count = 0
        process_names = self.get_process_names()
        
        for proc in psutil.process_iter(['pid', 'name', 'exe', 'cmdline']):
            try:
                name = (proc.info.get('name') or '').lower()
                exe = (proc.info.get('exe') or '').lower()
                cmd = ' '.join(proc.info.get('cmdline') or []).lower()
                
                # Check if process matches any of our target names
                if any(pname.lower() in name or pname.lower() in exe or pname.lower() in cmd 
                       for pname in process_names):
                    print(f"[+] Killing existing process pid={proc.pid} ({name})")
                    proc.kill()
                    killed_count += 1
            except Exception:
                pass
        
        return killed_count
    
    def launch_browser(self, try_alternate_format: bool = False) -> subprocess.Popen:
        """
        Launch the browser process.
        
        Args:
            try_alternate_format: Whether to try alternate argument format (e.g., with --)
            
        Returns:
            The subprocess.Popen object for the browser process
        """
        if not self.config.executable_path.exists():
            raise FileNotFoundError(f"Browser executable not found: {self.config.executable_path}")
        
        # Get browser-specific arguments
        args = self.get_launch_args()
        
        # Alternate format (some apps require -- before flags)
        if try_alternate_format:
            args = [str(self.config.executable_path), "--"] + args[1:]
        
        print(f"[*] Launching {self.__class__.__name__}:", " ".join(args))
        
        # Launch from exe folder as working directory
        cwd = str(self.config.executable_path.parent)
        
        self.process = subprocess.Popen(
            args,
            cwd=cwd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        
        return self.process
    
    def wait_for_devtools(self, url: Optional[str] = None) -> Dict[str, Any]:
        """
        Wait for DevTools endpoint to become available.
        
        Args:
            url: DevTools URL (defaults to http://127.0.0.1:{port}/json/version)
            
        Returns:
            DevTools version information as JSON
        """
        if url is None:
            url = f"http://127.0.0.1:{self.config.debug_port}/json/version"
        
        deadline = time.time() + self.config.timeout
        last_exc = None
        
        while time.time() < deadline:
            try:
                r = requests.get(url, timeout=0.5)
                if r.ok:
                    return r.json()
            except Exception as e:
                last_exc = e
            time.sleep(0.25)
        
        raise RuntimeError(
            f"DevTools not reachable at {url} after {self.config.timeout}s. "
            f"Last error: {last_exc}"
        )
    
    @abstractmethod
    def attach_selenium(self) -> Any:
        """
        Attach Selenium WebDriver to the running browser.
        
        Returns:
            Selenium WebDriver instance
        """
        pass
    
    def launch_and_attach(self, kill_existing: bool = True) -> Any:
        """
        Complete workflow: kill existing processes, launch browser, attach Selenium.
        
        Args:
            kill_existing: Whether to kill existing browser processes first
            
        Returns:
            Selenium WebDriver instance
        """
        # Step 1: Kill existing processes
        if kill_existing:
            killed = self.kill_existing_processes()
            if killed > 0:
                time.sleep(1)  # Give processes time to fully terminate
            
            # Clean user data directory to start fresh (prevents tab accumulation)
            if self.config.user_data_dir:
                import shutil
                user_data_path = Path(self.config.user_data_dir)
                if user_data_path.exists():
                    try:
                        print(f"[*] Cleaning profile directory: {user_data_path}")
                        shutil.rmtree(user_data_path)
                        print(f"[*] Profile cleaned successfully")
                    except Exception as e:
                        print(f"[WARN] Could not clean profile: {e}")
        
        # Step 2: Launch browser
        try:
            self.launch_browser(try_alternate_format=False)
            devtools_info = self.wait_for_devtools()
        except RuntimeError:
            # Try alternate argument format
            print("[*] Retrying with alternate argument format...")
            if self.process:
                try:
                    self.process.kill()
                except Exception:
                    pass
            
            self.launch_browser(try_alternate_format=True)
            devtools_info = self.wait_for_devtools()
        
        print(f"[*] DevTools available. Browser: {devtools_info.get('Browser')}")
        print(f"[*] WebSocket URL: {devtools_info.get('webSocketDebuggerUrl')}")
        
        # Step 3: Attach Selenium
        print("[*] Attaching Selenium WebDriver...")
        self.driver = self.attach_selenium()
        
        if self.driver:
            print("[*] Selenium attached successfully!")
        else:
            print("[!] Selenium attach failed")
        
        return self.driver
    
    def quit(self):
        """Clean up resources"""
        if self.driver:
            try:
                self.driver.quit()
            except Exception as e:
                print(f"[WARN] Error closing driver: {e}")
        
        if self.process:
            try:
                self.process.terminate()
            except Exception:
                pass
    
    def __enter__(self):
        """Context manager entry"""
        return self.launch_and_attach()
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.quit()
