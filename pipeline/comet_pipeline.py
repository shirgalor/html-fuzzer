"""
Comet Pipeline
==============
Pipeline implementation for Perplexity Comet browser.

Workflow:
1. Launch Comet browser
2. Open Perplexity Sidecar (https://www.perplexity.ai/sidecar?copilot=true) using Selenium
"""

import time
from typing import Any
from .base import BasePipeline, PipelineConfig, PipelineResult


class CometPipeline(BasePipeline):
    """
    Pipeline implementation for Comet browser.
    
    Simple workflow:
    - Launch Comet browser
    - Open Perplexity Sidecar using Selenium (overrides target URL)
    """
    
    SIDECAR_URL = "https://www.perplexity.ai/sidecar?copilot=true"
    
    def __init__(self, browser_launcher, navigator_factory, config):
        """Initialize Comet pipeline and override target URL to Sidecar."""
        # Override the target URL to always be Sidecar for Comet
        config.target_url = self.SIDECAR_URL
        super().__init__(browser_launcher, navigator_factory, config)
    
    def get_browser_name(self) -> str:
        """Return the browser name."""
        return "Comet"
    
    def pre_navigation_steps(self) -> bool:
        """
        No pre-navigation steps - we go directly to Sidecar.
        
        Returns:
            True
        """
        print(f"[INFO] Comet pipeline: Will navigate to Sidecar")
        return True
    
    def post_navigation_steps(self) -> bool:
        """
        No post-navigation steps - just open Sidecar and done.
        
        Returns:
            True
        """
        print(f"[INFO] Sidecar opened successfully")
        self._steps_completed.append("Opened Perplexity Sidecar")
        return True
    
    def print_success_summary(self):
        """Print Comet-specific success summary."""
        print("\n" + "=" * 60)
        print("COMET PIPELINE - WORKFLOW COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        
        for step in self._steps_completed:
            print(f"✓ {step}")
        
        print("=" * 60)
