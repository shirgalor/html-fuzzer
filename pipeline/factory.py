"""
Pipeline Factory
================
Factory for creating browser-specific pipelines.

Note: CometPipeline is now in browser.comet package.
This factory is kept for backward compatibility and extensibility.

Usage:
    from browser.comet import CometPipeline
    
    pipeline = CometPipeline(driver, navigator, config, **kwargs)
    pipeline.run()
"""

from enum import Enum
from typing import Dict, Type, Callable
from .base import BasePipeline, PipelineConfig


class PipelineType(Enum):
    """Supported pipeline types."""
    COMET = "comet"
    # Future additions:
    # CHROME = "chrome"
    # FIREFOX = "firefox"
    # EDGE = "edge"


# Registry mapping pipeline types to their classes
_PIPELINE_CLASSES: Dict[PipelineType, Type[BasePipeline]] = {
    # Comet is now in browser.comet package
    # PipelineType.COMET: CometPipeline,
}


class PipelineFactory:
    """
    Factory for creating browser-specific pipeline instances.
    
    Examples:
        # Create a Comet pipeline
        >>> from browser_launcher import BrowserFactory, BrowserType
        >>> from navigator import NavigatorFactory, NavigatorType
        >>> 
        >>> browser_launcher = BrowserFactory.create(BrowserType.COMET)
        >>> navigator_factory = lambda driver: NavigatorFactory.create(NavigatorType.COMET, driver)
        >>> config = PipelineConfig(target_url="https://example.com")
        >>> 
        >>> pipeline = PipelineFactory.create(
        ...     PipelineType.COMET,
        ...     browser_launcher=browser_launcher,
        ...     navigator_factory=navigator_factory,
        ...     config=config
        ... )
        >>> result = pipeline.run()
    """
    
    @staticmethod
    def create(
        pipeline_type: PipelineType,
        driver,
        navigator,
        config: PipelineConfig,
        **kwargs
    ) -> BasePipeline:
        """
        Create a pipeline instance for the specified browser type.
        
        Args:
            pipeline_type: Type of pipeline to create (from PipelineType enum)
            driver: Selenium WebDriver instance (already launched)
            navigator: Navigator instance (already created)
            config: Pipeline configuration
            **kwargs: Additional pipeline-specific parameters
            
        Returns:
            Instance of the appropriate pipeline class
            
        Raises:
            ValueError: If pipeline_type is not supported
            
        Examples:
            >>> config = PipelineConfig(target_url="https://www.perplexity.ai/sidecar?copilot=true")
            >>> pipeline = PipelineFactory.create(
            ...     PipelineType.COMET,
            ...     driver=driver,
            ...     navigator=navigator,
            ...     config=config,
            ...     query="What is Python?",
            ...     submit=False
            ... )
            >>> result = pipeline.run()
        """
        
        # Get the pipeline class
        if pipeline_type not in _PIPELINE_CLASSES:
            raise ValueError(
                f"Unsupported pipeline type: {pipeline_type}. "
                f"Supported types: {list(_PIPELINE_CLASSES.keys())}"
            )
        
        pipeline_class = _PIPELINE_CLASSES[pipeline_type]
        
        # Create and return the pipeline instance
        return pipeline_class(driver, navigator, config, **kwargs)
    
    @staticmethod
    def register_pipeline(
        pipeline_type: PipelineType,
        pipeline_class: Type[BasePipeline]
    ):
        """
        Register a new pipeline type.
        
        This allows external code to add support for new browsers
        without modifying this module.
        
        Args:
            pipeline_type: Pipeline type enum value
            pipeline_class: Class implementing BasePipeline
            
        Examples:
            >>> class MyCustomPipeline(BasePipeline):
            ...     def pre_navigation_steps(self): ...
            ...     def post_navigation_steps(self): ...
            ...     def get_browser_name(self): return "MyBrowser"
            ...     def print_success_summary(self): ...
            >>> 
            >>> PipelineFactory.register_pipeline(
            ...     PipelineType.CUSTOM,
            ...     MyCustomPipeline
            ... )
        """
        if not issubclass(pipeline_class, BasePipeline):
            raise TypeError(
                f"{pipeline_class.__name__} must inherit from BasePipeline"
            )
        
        _PIPELINE_CLASSES[pipeline_type] = pipeline_class
        print(f"[INFO] Registered pipeline: {pipeline_type.value} -> {pipeline_class.__name__}")
    
    @staticmethod
    def get_supported_types() -> list[PipelineType]:
        """
        Get list of all supported pipeline types.
        
        Returns:
            List of PipelineType enum values that can be created
        """
        return list(_PIPELINE_CLASSES.keys())


# Convenience function for simpler imports
def create_pipeline(
    pipeline_type: PipelineType,
    browser_launcher,
    navigator_factory: Callable,
    config: PipelineConfig
) -> BasePipeline:
    """
    Convenience function to create a pipeline.
    
    Equivalent to PipelineFactory.create() but shorter to type.
    
    Args:
        pipeline_type: Type of pipeline to create
        browser_launcher: BrowserLauncher instance
        navigator_factory: Callable that creates Navigator
        config: Pipeline configuration
        
    Returns:
        Pipeline instance
    """
    return PipelineFactory.create(
        pipeline_type,
        browser_launcher,
        navigator_factory,
        config
    )
