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
    metadata: dict = None
    
    def __post_init__(self):
        if self.steps_completed is None:
            self.steps_completed = []
        if self.metadata is None:
            self.metadata = {}


class BasePipeline(ABC):
    """
    Abstract base class for browser automation pipelines.
    
    Pipeline receives driver and navigator from Browser (facade).
    It does NOT launch browser or navigate - just runs workflow steps.
    
    Different browsers may have different workflows:
    - Comet: Send query to Sidecar → Wait for response
    - Chrome: Run extensions → Capture results
    - Firefox: Execute dev tools commands → Export data
    
    Subclasses should implement:
    - get_browser_name(): Return browser name
    - pre_workflow_steps(): Steps before main workflow
    - execute_workflow(): Main workflow logic
    - post_workflow_steps(): Steps after main workflow
    """
    
    def __init__(
        self,
        driver: WebDriver,
        navigator,
        config: PipelineConfig,
        **kwargs
    ):
        """
        Initialize pipeline with driver and navigator (provided by Browser facade).
        
        Args:
            driver: Selenium WebDriver instance (already launched and navigated)
            navigator: Navigator instance (already created)
            config: Pipeline configuration
            **kwargs: Additional browser-specific parameters
        """
        self.driver = driver
        self.navigator = navigator
        self.config = config
        self.extra_params = kwargs
        self._steps_completed = []
        self.metadata = {}  # Initialize metadata dictionary
    
    def run(self) -> PipelineResult:
        """
        Execute the pipeline workflow.
        
        Browser (facade) has already:
        - Launched browser
        - Created driver and navigator
        - Navigated to target URL
        
        Pipeline just runs workflow steps:
        1. Pre-workflow steps (optional browser-specific prep)
        2. Execute main workflow (core automation logic)
        3. Post-workflow steps (optional browser-specific cleanup)
        
        Returns:
            PipelineResult with success status and details
        """
        print("=" * 60)
        print(f"PIPELINE WORKFLOW - {self.get_browser_name()}")
        print("=" * 60)
        print(f"Current URL: {self.navigator.get_current_url()}")
        print("=" * 60)
        
        try:
            # Step 1: Pre-workflow steps (browser-specific)
            print("\n[PIPELINE] Step 1: Pre-workflow steps...")
            pre_result = self.pre_workflow_steps()
            if not pre_result:
                return PipelineResult(
                    success=False,
                    message="Pre-workflow steps failed",
                    driver=self.driver,
                    steps_completed=self._steps_completed
                )
            self._steps_completed.append("Pre-workflow steps")
            
            # Step 2: Execute main workflow
            print("\n[PIPELINE] Step 2: Executing main workflow...")
            workflow_result = self.execute_workflow()
            if not workflow_result:
                return PipelineResult(
                    success=False,
                    message="Workflow execution failed",
                    driver=self.driver,
                    steps_completed=self._steps_completed
                )
            self._steps_completed.append("Main workflow")
            
            # Step 3: Post-workflow steps
            print("\n[PIPELINE] Step 3: Post-workflow steps...")
            post_result = self.post_workflow_steps()
            if not post_result:
                # Don't fail pipeline for optional post-workflow steps
                print("[WARNING] Post-workflow steps had issues")
            else:
                self._steps_completed.append("Post-workflow steps")
            
            # Success!
            self.print_success_summary()
            
            return PipelineResult(
                success=True,
                message="Pipeline workflow completed successfully",
                driver=self.driver,
                steps_completed=self._steps_completed,
                metadata=self.metadata  # Include metadata
            )
            
        except Exception as e:
            print(f"[PIPELINE ERROR] Workflow failed: {e}")
            import traceback
            traceback.print_exc()
            return PipelineResult(
                success=False,
                message=f"Pipeline error: {e}",
                driver=self.driver,
                steps_completed=self._steps_completed
            )
    
    # ==================== Abstract Methods (subclasses must implement) ====================
    
    @abstractmethod
    def get_browser_name(self) -> str:
        """
        Return the name of the browser.
        
        Returns:
            Browser name (e.g., "Comet", "Chrome", "Firefox")
        """
        pass
    
    @abstractmethod
    def pre_workflow_steps(self) -> bool:
        """
        Execute browser-specific steps before main workflow.
        
        Examples:
        - Comet: Verify Sidecar page loaded correctly
        - Chrome: Verify extensions are loaded
        - Firefox: Configure dev tools settings
        
        Returns:
            True if steps successful, False otherwise
        """
        pass
    
    @abstractmethod
    def execute_workflow(self) -> bool:
        """
        Execute the main workflow logic (core automation).
        
        Examples:
        - Comet: Send query to Sidecar → Wait for response
        - Chrome: Run extension automation → Capture screenshots
        - Firefox: Execute dev tools commands → Export data
        
        Returns:
            True if workflow successful, False otherwise
        """
        pass
    
    @abstractmethod
    def post_workflow_steps(self) -> bool:
        """
        Execute browser-specific steps after main workflow.
        
        Examples:
        - Comet: Verify Assistant response received
        - Chrome: Clean up extension state
        - Firefox: Save dev tools logs
        
        Returns:
            True if steps successful, False otherwise
        """
        pass
    
    # ==================== Helper Methods ====================
    
    def print_success_summary(self):
        """Print success summary after pipeline completion."""
        print("\n" + "=" * 60)
        print(f"✓ {self.get_browser_name().upper()} PIPELINE COMPLETED SUCCESSFULLY")
        print("=" * 60)
        print(f"Steps completed: {len(self._steps_completed)}")
        for i, step in enumerate(self._steps_completed, 1):
            print(f"  {i}. {step}")
        print("=" * 60)
