"""
Navigator Factory
=================
Factory pattern for creating navigator instances.

Note: CometNavigator is now in browser.comet package.
This factory is kept for backward compatibility and extensibility.

Usage:
    from browser.comet import CometNavigator
    
    navigator = CometNavigator(driver)
    navigator.navigate_to_url("https://example.com")
"""

from enum import Enum
from typing import Any, Type, Optional
from .base import Navigator


class NavigatorType(Enum):
    """
    Supported navigator types.
    
    To add a new navigator:
    1. Add enum value here (e.g., CHROME = "chrome")
    2. Create navigator class inheriting from Navigator
    3. Register it in NavigatorFactory._NAVIGATOR_CLASSES
    """
    COMET = "comet"
    # Future navigators:
    # CHROME = "chrome"
    # EDGE = "edge"
    # FIREFOX = "firefox"


class NavigatorFactory:
    """
    Factory for creating navigator instances.
    
    Uses registry pattern to map NavigatorType enums to their
    corresponding navigator classes.
    
    Note: Comet-specific implementation is in browser.comet package.
    """
    
    # Registry of navigator types to classes
    _NAVIGATOR_CLASSES: dict[NavigatorType, Type[Navigator]] = {
        # Comet is now in browser.comet package
        # NavigatorType.COMET: CometNavigator,
        # Future navigators can be registered here:
        # NavigatorType.CHROME: ChromeNavigator,
        # NavigatorType.EDGE: EdgeNavigator,
    }
    
    @classmethod
    def create(
        cls,
        navigator_type: NavigatorType,
        driver: Any
    ) -> Navigator:
        """
        Create a navigator instance.
        
        Args:
            navigator_type: Type of navigator to create
            driver: Selenium WebDriver instance
        
        Returns:
            Navigator instance for the specified type
        
        Raises:
            ValueError: If navigator_type is not supported
        
        Examples:
            >>> driver = launch_browser()
            >>> navigator = NavigatorFactory.create(NavigatorType.COMET, driver)
            >>> navigator.navigate_to_url("https://example.com")
        """
        navigator_class = cls._NAVIGATOR_CLASSES.get(navigator_type)
        
        if navigator_class is None:
            available = ", ".join(nt.value for nt in cls._NAVIGATOR_CLASSES.keys())
            raise ValueError(
                f"Unsupported navigator type: {navigator_type.value}. "
                f"Available types: {available}"
            )
        
        return navigator_class(driver)
    
    @classmethod
    def register_navigator(
        cls,
        navigator_type: NavigatorType,
        navigator_class: Type[Navigator]
    ) -> None:
        """
        Register a new navigator class.
        
        Allows plugins to add new navigator types without modifying this file.
        
        Args:
            navigator_type: Enum value for the navigator type
            navigator_class: Class that implements Navigator
        
        Example:
            >>> class MyCustomNavigator(Navigator):
            ...     # Implementation
            ...     pass
            >>> NavigatorFactory.register_navigator(
            ...     NavigatorType.CUSTOM,
            ...     MyCustomNavigator
            ... )
        """
        if not issubclass(navigator_class, Navigator):
            raise TypeError(
                f"{navigator_class.__name__} must inherit from Navigator"
            )
        
        cls._NAVIGATOR_CLASSES[navigator_type] = navigator_class
    
    @classmethod
    def get_supported_navigators(cls) -> list[NavigatorType]:
        """
        Get list of currently supported navigator types.
        
        Returns:
            List of NavigatorType enums that can be used with create()
        """
        return list(cls._NAVIGATOR_CLASSES.keys())


# Convenience function for creating a navigator
def create_navigator(
    navigator_type: NavigatorType = NavigatorType.COMET,
    driver: Any = None
) -> Navigator:
    """
    Convenience function to quickly create a navigator.
    
    This is a shortcut for:
        navigator = NavigatorFactory.create(navigator_type, driver)
    
    Args:
        navigator_type: Type of navigator (default: Comet)
        driver: Selenium WebDriver instance
    
    Returns:
        Navigator instance
    
    Example:
        >>> driver = launch_browser()
        >>> navigator = create_navigator(driver=driver)
        >>> navigator.navigate_to_url("https://example.com")
    """
    if driver is None:
        raise ValueError("driver is required")
    
    return NavigatorFactory.create(navigator_type, driver)
