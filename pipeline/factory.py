"""
Pipeline Factory
================
Factory for creating browser-specific pipelines.

Supports different browsers with their own workflows:
- Comet: Sidecar + Assistant activation
- Chrome: (Future) Extension loading
- Firefox: (Future) DevTools configuration
"""

from enum import Enum
from typing import Dict, Type, Callable
from .base import BasePipeline, PipelineConfig
from .comet_pipeline import CometPipeline


class PipelineType(Enum):
    """Supported pipeline types."""
    COMET = "comet"
    # Future additions:
    # CHROME = "chrome"
    # FIREFOX = "firefox"
    # EDGE = "edge"


# Registry mapping pipeline types to their classes
_PIPELINE_CLASSES: Dict[PipelineType, Type[BasePipeline]] = {
    PipelineType.COMET: CometPipeline,
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
        browser_launcher,
        navigator_factory: Callable,
        config: PipelineConfig
    ) -> BasePipeline:
        """
        Create a pipeline instance for the specified browser type.
        
        Args:
            pipeline_type: Type of pipeline to create (from PipelineType enum)
            browser_launcher: BrowserLauncher instance for this browser
            navigator_factory: Callable that creates Navigator (takes driver as arg)
            config: Pipeline configuration
            
        Returns:
            Instance of the appropriate pipeline class
            
        Raises:
            ValueError: If pipeline_type is not supported
            
        Examples:
            >>> config = PipelineConfig(target_url="file:///path/to/file.html")
            >>> pipeline = PipelineFactory.create(
            ...     PipelineType.COMET,
            ...     browser_launcher=comet_launcher,
            ...     navigator_factory=nav_factory,
            ...     config=config
            ... )
        """
        if pipeline_type not in _PIPELINE_CLASSES:
            supported = ", ".join(pt.value for pt in _PIPELINE_CLASSES.keys())
            raise ValueError(
                f"Unsupported pipeline type: {pipeline_type.value}. "
                f"Supported types: {supported}"
            )
        
        pipeline_class = _PIPELINE_CLASSES[pipeline_type]
        return pipeline_class(
            browser_launcher=browser_launcher,
            navigator_factory=navigator_factory,
            config=config
        )
    
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
