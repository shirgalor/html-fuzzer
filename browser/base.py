"""
Base Browser
============
Abstract base class representing a complete browser with all its components.

A Browser encapsulates:
- Browser launcher (how to launch and attach)
- Navigator (how to navigate and interact)
- Pipeline (complete workflow including browser-specific steps)
- Attack names (browser-specific vulnerability names)
"""

from abc import ABC, abstractmethod
from typing import Optional, List, Any
from dataclasses import dataclass


@dataclass
class BrowserInfo:
    """Information about a browser."""
    name: str
    version: Optional[str] = None
    executable_path: Optional[str] = None
    supports_devtools: bool = True
    supports_extensions: bool = True


class BaseBrowser(ABC):
    """
    Abstract base class representing a complete browser system.
    
    A Browser is a high-level abstraction that composes:
    - BrowserLauncher: Launch and attach to the browser
    - Navigator: Navigate pages and manage tabs
    - Pipeline: Complete automation workflows
    - Attack names: Browser-specific vulnerabilities to test
    
    Each browser implementation (Comet, Chrome, Firefox) should:
    1. Provide its own launcher, navigator, and pipeline
    2. Define browser-specific attack names
    3. Implement browser-specific initialization
    
    Example:
        >>> browser = BrowserFactory.create(BrowserType.COMET)
        >>> browser.launch()
        >>> browser.navigate_to("https://example.com")
        >>> browser.run_pipeline(target_url="https://test.com")
        >>> attacks = browser.get_attack_names()
    """
    
    def __init__(self):
        """Initialize browser (subclasses may override)."""
        self._launcher = None
        self._navigator = None
        self._pipeline = None
        self._driver = None
        self._is_launched = False
    
    # ==================== Abstract Methods ====================
    
    @abstractmethod
    def get_browser_info(self) -> BrowserInfo:
        """
        Get information about this browser.
        
        Returns:
            BrowserInfo with name, version, capabilities
        """
        pass
    
    @abstractmethod
    def create_launcher(self):
        """
        Create the browser launcher for this browser type.
        
        Returns:
            BrowserLauncher instance specific to this browser
        """
        pass
    
    @abstractmethod
    def create_navigator(self, driver):
        """
        Create the navigator for this browser type.
        
        Args:
            driver: WebDriver instance
            
        Returns:
            Navigator instance specific to this browser
        """
        pass
    
    @abstractmethod
    def create_pipeline(self, config):
        """
        Create the pipeline for this browser type.
        
        Args:
            config: PipelineConfig instance
            
        Returns:
            Pipeline instance specific to this browser
        """
        pass
    
    @abstractmethod
    def get_attack_names(self) -> List[str]:
        """
        Get list of attack/vulnerability names specific to this browser.
        
        These are browser-specific vulnerabilities or test cases
        that can be used for fuzzing or security testing.
        
        Returns:
            List of attack names (e.g., ["XSS", "CSRF", "ClickJacking"])
        """
        pass
    
    # ==================== Concrete Methods ====================
    
    def launch(self, kill_existing: bool = True) -> bool:
        """
        Launch the browser and attach Selenium WebDriver.
        
        Args:
            kill_existing: Kill existing browser processes first
            
        Returns:
            True if launch successful, False otherwise
        """
        if self._is_launched:
            print("[INFO] Browser already launched")
            return True
        
        try:
            print(f"[INFO] Launching {self.get_browser_info().name}...")
            
            # Create launcher if not exists
            if not self._launcher:
                self._launcher = self.create_launcher()
            
            # Launch and attach
            self._driver = self._launcher.launch_and_attach()
            
            if not self._driver:
                print("[ERROR] Failed to launch browser")
                return False
            
            # Create navigator
            self._navigator = self.create_navigator(self._driver)
            
            self._is_launched = True
            print(f"[SUCCESS] {self.get_browser_info().name} launched")
            return True
            
        except Exception as e:
            print(f"[ERROR] Launch failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def navigate_to(self, url: str, wait_time: int = 5):
        """
        Navigate to a URL.
        
        Args:
            url: URL to navigate to
            wait_time: Seconds to wait after navigation
            
        Returns:
            NavigationResult object
        """
        if not self._is_launched:
            raise RuntimeError("Browser not launched. Call launch() first.")
        
        return self._navigator.navigate_to_url(url, wait_time=wait_time)
    
    def open_local_files(self, folder, pattern: str = "*.html", **kwargs):
        """
        Open multiple local HTML files.
        
        Args:
            folder: Path to folder containing HTML files
            pattern: Glob pattern for files
            **kwargs: Additional arguments for navigator
            
        Returns:
            List of opened file URLs
        """
        if not self._is_launched:
            raise RuntimeError("Browser not launched. Call launch() first.")
        
        return self._navigator.open_local_html_files(folder, pattern, **kwargs)
    
    def run_pipeline(self, config):
        """
        Run the complete browser automation pipeline.
        
        Args:
            config: PipelineConfig with target URL and settings
            
        Returns:
            PipelineResult object
        """
        if not self._is_launched:
            # Pipeline will launch browser itself
            self._pipeline = self.create_pipeline(config)
            result = self._pipeline.run()
            
            # Update our state
            self._driver = result.driver
            if result.success:
                self._navigator = self.create_navigator(self._driver)
                self._is_launched = True
            
            return result
        else:
            # Browser already launched, create pipeline with existing driver
            # Note: This would require pipeline to support existing driver
            print("[INFO] Browser already launched, pipeline will use existing driver")
            self._pipeline = self.create_pipeline(config)
            return self._pipeline.run()
    
    def get_driver(self):
        """
        Get the underlying WebDriver instance.
        
        Returns:
            Selenium WebDriver or None if not launched
        """
        return self._driver
    
    def get_navigator(self):
        """
        Get the navigator instance.
        
        Returns:
            Navigator instance or None if not launched
        """
        return self._navigator
    
    def get_window_handles(self):
        """
        Get all window handles (tabs).
        
        Returns:
            List of window handle IDs
        """
        if not self._is_launched:
            raise RuntimeError("Browser not launched. Call launch() first.")
        
        return self._navigator.get_window_handles()
    
    def switch_to_window(self, handle):
        """
        Switch to a specific window/tab.
        
        Args:
            handle: Window handle ID
        """
        if not self._is_launched:
            raise RuntimeError("Browser not launched. Call launch() first.")
        
        self._navigator.switch_to_window(handle)
    
    def quit(self):
        """
        Close the browser and clean up resources.
        """
        if self._driver:
            try:
                print(f"[INFO] Closing {self.get_browser_info().name}...")
                self._driver.quit()
                self._is_launched = False
                print("[SUCCESS] Browser closed")
            except Exception as e:
                print(f"[WARNING] Error closing browser: {e}")
    
    def __enter__(self):
        """Context manager entry."""
        self.launch()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.quit()
    
    def __repr__(self):
        """String representation."""
        info = self.get_browser_info()
        status = "launched" if self._is_launched else "not launched"
        return f"<{info.name} ({status})>"
