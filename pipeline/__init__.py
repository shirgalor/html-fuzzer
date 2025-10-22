"""
Pipeline Module
===============
Modular pipeline system for browser automation workflows.

This module provides browser-specific pipeline implementations that handle
complete automation workflows from launch to cleanup.

Usage:
    from pipeline import PipelineFactory, PipelineType, PipelineConfig
    from browser_launcher import BrowserFactory, BrowserType
    from navigator import NavigatorFactory, NavigatorType
    
    # Create dependencies
    browser_launcher = BrowserFactory.create(BrowserType.COMET)
    nav_factory = lambda driver: NavigatorFactory.create(NavigatorType.COMET, driver)
    
    # Configure pipeline
    config = PipelineConfig(
        target_url="https://example.com",
        load_wait_time=5,
        keep_open=True
    )
    
    # Create and run pipeline
    pipeline = PipelineFactory.create(
        PipelineType.COMET,
        browser_launcher=browser_launcher,
        navigator_factory=nav_factory,
        config=config
    )
    
    result = pipeline.run()
    if result.success:
        print("Pipeline completed!")

Architecture:
    BasePipeline (abstract)
    ├── CometPipeline    - Perplexity Comet workflow
    ├── ChromePipeline   - (Future) Chrome workflow  
    └── FirefoxPipeline  - (Future) Firefox workflow

Each pipeline controls its own workflow:
- Pre-navigation steps (e.g., open Sidecar for Comet)
- Navigation to target URL
- Post-navigation steps (e.g., activate Assistant for Comet)
"""

from .base import BasePipeline, PipelineConfig, PipelineResult
from .factory import PipelineFactory, PipelineType, create_pipeline

__all__ = [
    # Base classes
    "BasePipeline",
    "PipelineConfig",
    "PipelineResult",
    
    # Factory
    "PipelineFactory",
    "PipelineType",
    "create_pipeline",
]
