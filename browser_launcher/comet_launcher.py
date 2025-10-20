"""
Comet Browser Launcher
======================
Implementation for launching and controlling Perplexity Comet browser.
"""

from pathlib import Path
from typing import List, Any, Optional
import requests
import re

from .base import BrowserLauncher, BrowserConfig

try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False


class CometBrowserLauncher(BrowserLauncher):
    """
    Launcher for Perplexity Comet browser.
    
    Comet is a Chromium-based browser, so it uses Chrome DevTools Protocol
    and can be controlled via Selenium with ChromeDriver.
    """
    
    def __init__(self, config: Optional[BrowserConfig] = None):
        """
        Initialize Comet launcher.
        
        Args:
            config: Browser configuration (auto-detected if not provided)
        """
        if config is None:
            # Auto-detect Comet installation
            comet_path = Path(r"C:\Users") / Path.home().name / \
                        "AppData/Local/Perplexity/Comet/Application/comet.exe"
            
            config = BrowserConfig(
                executable_path=comet_path,
                debug_port=9222,
                start_maximized=True,
                allow_file_access=True,
                disable_web_security=True,
                user_data_dir=Path("./comet_profile_tmp")
            )
        
        super().__init__(config)
    
    def get_launch_args(self) -> List[str]:
        """Get Comet-specific launch arguments"""
        args = [
            str(self.config.executable_path),
            f"--remote-debugging-port={self.config.debug_port}",
        ]
        
        if self.config.start_maximized:
            args.append("--start-maximized")
        
        if self.config.allow_file_access:
            args.extend([
                "--allow-file-access-from-files",
                "--allow-file-access",
            ])
        
        if self.config.disable_web_security:
            args.append("--disable-web-security")
        
        if self.config.user_data_dir:
            args.append(f"--user-data-dir={self.config.user_data_dir}")
        
        # Add any extra custom arguments
        args.extend(self.config.extra_args)
        
        return args
    
    def get_process_names(self) -> List[str]:
        """Get process names for Comet browser"""
        return ["comet", "comet.exe", "perplexity"]
    
    def _get_chromedriver_path(self) -> Optional[str]:
        """
        Get or install ChromeDriver matching the Comet version.
        
        Returns:
            Path to ChromeDriver executable, or None if unavailable
        """
        driver_path = None
        
        # Try chromedriver_autoinstaller first
        try:
            import chromedriver_autoinstaller as cda
            
            # Detect Comet version
            try:
                r = requests.get(
                    f"http://127.0.0.1:{self.config.debug_port}/json/version",
                    timeout=1
                )
                if r.ok:
                    ver = r.json()
                    browser_str = ver.get("Browser", "")
                    m = re.search(r"/(\d+)\.", browser_str)
                    if m:
                        chrome_major = m.group(1)
                        print(f"[*] Detected Comet version: Chrome/{chrome_major}")
                        
                        try:
                            driver_path = cda.install(chrome_major)
                            
                            # Verify version match
                            if driver_path and "141" in driver_path and chrome_major == "140":
                                print(f"[!] Version mismatch detected, forcing fallback")
                                driver_path = None
                        except Exception:
                            driver_path = cda.install()
            except Exception as e:
                print(f"[!] Version detection failed: {e}")
                driver_path = cda.install()
            
            if driver_path:
                print(f"[*] chromedriver_autoinstaller provided: {driver_path}")
                return driver_path
        
        except ImportError:
            print("[*] chromedriver_autoinstaller not available")
        except Exception as e:
            print(f"[!] chromedriver_autoinstaller failed: {e}")
        
        # Fallback to manual download if needed
        driver_path = self._download_matching_chromedriver()
        if driver_path:
            return driver_path
        
        # Last resort: webdriver_manager
        try:
            from webdriver_manager.chrome import ChromeDriverManager
            print("[*] Falling back to webdriver_manager")
            driver_path = ChromeDriverManager().install()
            print(f"[*] webdriver_manager provided: {driver_path}")
            return driver_path
        except Exception as e:
            print(f"[!] webdriver_manager failed: {e}")
        
        return None
    
    def _download_matching_chromedriver(self) -> Optional[str]:
        """
        Download ChromeDriver matching the Comet Chrome version.
        
        Returns:
            Path to downloaded ChromeDriver, or None if failed
        """
        try:
            import os
            from urllib.request import urlretrieve
            import zipfile
            import tempfile
            
            # Get browser version
            r = requests.get(
                f"http://127.0.0.1:{self.config.debug_port}/json/version",
                timeout=1
            )
            if not r.ok:
                return None
            
            ver = r.json()
            browser_str = ver.get("Browser", "")
            m = re.search(r"/(\d+\.\d+\.\d+\.\d+)", browser_str)
            if not m:
                return None
            
            chrome_full_version = m.group(1)
            chrome_major = chrome_full_version.split('.')[0]
            
            print(f"[*] Downloading ChromeDriver for Chrome {chrome_full_version}")
            
            # Get matching ChromeDriver version from Google's API
            releases_url = "https://googlechromelabs.github.io/chrome-for-testing/known-good-versions-with-downloads.json"
            releases_resp = requests.get(releases_url, timeout=5)
            
            if not releases_resp.ok:
                return None
            
            releases_data = releases_resp.json()
            
            # Find matching version
            for version_info in releases_data.get("versions", []):
                version = version_info.get("version", "")
                if version.startswith(f"{chrome_major}.") and "downloads" in version_info:
                    downloads = version_info["downloads"]
                    if "chromedriver" in downloads:
                        for platform_info in downloads["chromedriver"]:
                            if platform_info.get("platform") == "win64":
                                chromedriver_version = version
                                download_url = platform_info.get("url")
                                
                                print(f"[*] Found ChromeDriver {chromedriver_version}")
                                
                                # Download and extract
                                with tempfile.TemporaryDirectory() as temp_dir:
                                    zip_path = os.path.join(temp_dir, "chromedriver.zip")
                                    urlretrieve(download_url, zip_path)
                                    
                                    extract_dir = os.path.join(
                                        os.getcwd(),
                                        f"chromedriver_{chromedriver_version}"
                                    )
                                    os.makedirs(extract_dir, exist_ok=True)
                                    
                                    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                                        zip_ref.extractall(extract_dir)
                                    
                                    # Find chromedriver.exe
                                    for root, dirs, files in os.walk(extract_dir):
                                        if "chromedriver.exe" in files:
                                            driver_path = os.path.join(root, "chromedriver.exe")
                                            print(f"[*] Downloaded to: {driver_path}")
                                            return driver_path
                                
                                return None
        
        except Exception as e:
            print(f"[!] Manual ChromeDriver download failed: {e}")
            return None
    
    def attach_selenium(self) -> Any:
        """Attach Selenium WebDriver to running Comet browser"""
        if not SELENIUM_AVAILABLE:
            print("[!] Selenium not installed")
            return None
        
        # Get ChromeDriver
        driver_path = self._get_chromedriver_path()
        if not driver_path:
            print("[!] No ChromeDriver available")
            return None
        
        # Configure Selenium options
        opts = Options()
        opts.debugger_address = f"127.0.0.1:{self.config.debug_port}"
        opts.add_argument("--remote-allow-origins=*")
        
        # Create service and driver
        service = Service(driver_path)
        driver = webdriver.Chrome(service=service, options=opts)
        
        return driver


# Convenience function for backward compatibility
def launch_comet() -> Any:
    """
    Launch Comet browser and attach Selenium (backward compatible interface).
    
    Returns:
        Selenium WebDriver instance
    """
    launcher = CometBrowserLauncher()
    return launcher.launch_and_attach()
