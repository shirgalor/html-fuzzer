"""
Base Pipeline
=============
Abstract base class defining the pipeline interface for browser automation workflows.

Each browser type can have its own pipeline implementation with custom steps.
"""

from abc import ABC, abstractmethod
from typing import Any, Optional
from dataclasses import dataclass
from selenium.webdriver.remote.webdriver import WebDriver


@dataclass
class PipelineConfig:
    """Configuration for pipeline execution."""
    target_url: str
    load_wait_time: int = 5
    stability_wait_time: int = 2
    keep_open: bool = False
    activate_features: bool = True  # e.g., click Assistant button
    

@dataclass
class PipelineResult:
    """Result of pipeline execution."""
    success: bool
    message: str
    driver: Optional[WebDriver] = None
    steps_completed: list[str] = None
    
    def __post_init__(self):
        if self.steps_completed is None:
            self.steps_completed = []


class BasePipeline(ABC):
    """
    Abstract base class for browser automation pipelines.
    
    Different browsers may have different workflows:
    - Comet: Open Sidecar → Navigate → Activate Assistant
    - Chrome: Navigate → Run extensions
    - Firefox: Navigate → Configure dev tools
    
    Subclasses should implement:
    - setup_browser(): Browser-specific initialization
    - pre_navigation_steps(): Steps before main navigation
    - post_navigation_steps(): Steps after main navigation
    - cleanup(): Browser-specific cleanup
    """
    
    def __init__(
        self,
        browser_launcher,
        navigator_factory,
        config: PipelineConfig
    ):
        """
        Initialize pipeline with dependencies.
        
        Args:
            browser_launcher: BrowserLauncher instance for this browser
            navigator_factory: Factory to create Navigator instances
            config: Pipeline configuration
        """
        self.browser_launcher = browser_launcher
        self.navigator_factory = navigator_factory
        self.config = config
        self.driver: Optional[WebDriver] = None
        self.navigator = None
        self._owns_browser = True
        self._steps_completed = []
    
    def run(self) -> PipelineResult:
        """
        Execute the complete pipeline workflow.
        
        Template method that orchestrates the pipeline steps:
        1. Setup browser
        2. Pre-navigation steps (browser-specific)
        3. Navigate to target URL
        4. Post-navigation steps (browser-specific)
        5. Cleanup
        
        Returns:
            PipelineResult with success status and details
        """
        print("=" * 60)
        print(f"BROWSER AUTOMATION PIPELINE - {self.get_browser_name()}")
        print("=" * 60)
        print(f"Target URL: {self.config.target_url}")
        print(f"Load wait time: {self.config.load_wait_time}s")
        print("=" * 60)
        
        try:
            # Step 1: Setup browser
            print("\n[1/?] Setting up browser...")
            setup_result = self.setup_browser()
            if not setup_result:
                return PipelineResult(
                    success=False,
                    message="Failed to setup browser",
                    steps_completed=self._steps_completed
                )
            self._steps_completed.append("Browser setup")
            
            # Step 2: Pre-navigation steps (browser-specific)
            print("\n[2/?] Running pre-navigation steps...")
            pre_nav_result = self.pre_navigation_steps()
            if not pre_nav_result:
                return PipelineResult(
                    success=False,
                    message="Pre-navigation steps failed",
                    driver=self.driver,
                    steps_completed=self._steps_completed
                )
            
            # Step 3: Navigate to target URL
            print(f"\n[3/?] Navigating to target URL...")
            nav_result = self.navigate_to_target()
            if not nav_result:
                return PipelineResult(
                    success=False,
                    message="Navigation to target failed",
                    driver=self.driver,
                    steps_completed=self._steps_completed
                )
            self._steps_completed.append(f"Navigated to {self.config.target_url}")
            
            # Step 4: Post-navigation steps (browser-specific)
            print(f"\n[4/?] Running post-navigation steps...")
            post_nav_result = self.post_navigation_steps()
            if not post_nav_result:
                # Don't fail pipeline for optional post-nav steps
                print("[WARNING] Post-navigation steps had issues")
            
            # Success!
            self.print_success_summary()
            
            if not self.config.keep_open and self._owns_browser:
                print("\n[INFO] Browser will remain open for interaction")
                print("[INFO] Press Enter to close and exit...")
                input()
            
            return PipelineResult(
                success=True,
                message="Pipeline completed successfully",
                driver=self.driver,
                steps_completed=self._steps_completed
            )
            
        except Exception as e:
            print(f"\n[ERROR] Pipeline failed: {e}")
            import traceback
            traceback.print_exc()
            return PipelineResult(
                success=False,
                message=f"Exception: {str(e)}",
                driver=self.driver,
                steps_completed=self._steps_completed
            )
        
        finally:
            if not self.config.keep_open:
                self.cleanup()
    
    def setup_browser(self) -> bool:
        """
        Launch browser and create navigator.
        
        Returns:
            True if setup successful, False otherwise
        """
        try:
            # Launch browser
            self.driver = self.browser_launcher.launch_and_attach()
            if not self.driver:
                print("[ERROR] Failed to launch browser")
                return False
            
            # Create navigator
            self.navigator = self.navigator_factory(self.driver)
            
            return True
            
        except Exception as e:
            print(f"[ERROR] Browser setup failed: {e}")
            return False
    
    @abstractmethod
    def pre_navigation_steps(self) -> bool:
        """
        Execute browser-specific steps before navigating to target URL.
        
        Examples:
        - Comet: Open Perplexity Sidecar page
        - Chrome: Load extensions
        - Firefox: Configure devtools
        
        Returns:
            True if steps successful, False otherwise
        """
        pass
    
    def navigate_to_target(self) -> bool:
        """
        Navigate to the target URL specified in config.
        
        Returns:
            True if navigation successful, False otherwise
        """
        try:
            result = self.navigator.navigate_to_url(
                self.config.target_url,
                wait_time=self.config.load_wait_time
            )
            
            if not result.success:
                print(f"[ERROR] Navigation failed: {result.message}")
                return False
            
            # Verify navigation
            current_url = self.navigator.get_current_url()
            print(f"[INFO] Current URL: {current_url}")
            print(f"[SUCCESS] {result.message}")
            
            return True
            
        except Exception as e:
            print(f"[ERROR] Navigation exception: {e}")
            return False
    
    @abstractmethod
    def post_navigation_steps(self) -> bool:
        """
        Execute browser-specific steps after navigating to target URL.
        
        Examples:
        - Comet: Activate Assistant button
        - Chrome: Run automation scripts
        - Firefox: Inject content scripts
        
        Returns:
            True if steps successful, False otherwise
        """
        pass
    
    @abstractmethod
    def get_browser_name(self) -> str:
        """
        Get the display name of this browser.
        
        Returns:
            Browser name (e.g., "Comet", "Chrome", "Firefox")
        """
        pass
    
    @abstractmethod
    def print_success_summary(self):
        """
        Print browser-specific success summary.
        
        This is called when pipeline completes successfully.
        Should print a formatted summary of completed steps.
        """
        pass
    
    def cleanup(self):
        """
        Clean up browser resources.
        
        Override this if you need custom cleanup logic.
        """
        if self._owns_browser and self.driver:
            print("\n[INFO] Closing browser connection...")
            try:
                if self.browser_launcher:
                    self.browser_launcher.quit()
                else:
                    self.driver.quit()
            except Exception as e:
                print(f"[WARNING] Error closing browser: {e}")
