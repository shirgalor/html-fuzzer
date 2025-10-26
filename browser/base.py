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
    def create_pipeline(self, driver, navigator, config, **kwargs):
        """
        Create the pipeline for this browser type.
        
        Pipeline receives driver and navigator from Browser (facade).
        It does NOT launch or navigate - just runs workflow steps.
        
        Args:
            driver: Selenium WebDriver instance (already launched)
            navigator: Navigator instance (already created)
            config: PipelineConfig instance
            **kwargs: Additional pipeline-specific parameters (e.g., query, submit)
            
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
    
    def run_pipeline(self, config, **kwargs):
        """
        Run the complete browser automation pipeline (FACADE ORCHESTRATOR).
        
        This is the main facade method that coordinates all components:
        1. Launch browser (via Launcher) → get driver
        2. Create navigator with driver
        3. Navigate to target URL (via Navigator)
        4. Create pipeline with driver & navigator
        5. Run workflow (via Pipeline)
        6. Handle keep_open option
        
        Browser is THE BOSS that manages the entire lifecycle.
        
        Args:
            config: PipelineConfig with target URL and settings
            **kwargs: Additional pipeline-specific arguments
                     (e.g., query="text" and submit=True for CometPipeline)
            
        Returns:
            PipelineResult object
        """
        print("=" * 60)
        print(f"BROWSER FACADE - {self.get_browser_info().name}")
        print("=" * 60)
        
        try:
            # Step 1: Launch browser (if not already launched)
            if not self._is_launched:
                print("\n[FACADE] Step 1: Launching browser...")
                if not self.launch():
                    from pipeline.base import PipelineResult
                    return PipelineResult(
                        success=False,
                        message="Failed to launch browser",
                        steps_completed=[]
                    )
                print(f"[FACADE] ✓ Browser launched")
            else:
                print(f"\n[FACADE] Browser already launched, reusing...")
            
            # Step 2: Create and run pipeline workflow
            # Pipeline will handle navigation to target URL
            print(f"\n[FACADE] Step 2: Creating and running pipeline...")
            self._pipeline = self.create_pipeline(
                driver=self._driver,
                navigator=self._navigator,
                config=config,
                **kwargs
            )
            
            result = self._pipeline.run()
            
            # Step 4: Handle keep_open option
            if config.keep_open and result.success:
                print("\n" + "=" * 60)
                print(f"✓ FACADE COMPLETE - Browser remains open")
                print("=" * 60)
                print("[INFO] Press Enter to close browser and exit...")
                input()
                self.quit()
            
            return result
            
        except Exception as e:
            print(f"[FACADE ERROR] Pipeline execution failed: {e}")
            import traceback
            traceback.print_exc()
            
            from pipeline.base import PipelineResult
            return PipelineResult(
                success=False,
                message=f"Facade error: {e}",
                driver=self._driver,
                steps_completed=[]
            )
    
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
