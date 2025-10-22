"""
Browser Launcher Factory
=========================
Factory pattern for creating browser launchers.

Note: CometBrowserLauncher is now in browser.comet package.
This factory is kept for backward compatibility and extensibility.

Usage:
    from browser.comet import CometBrowserLauncher
    
    launcher = CometBrowserLauncher()
    driver = launcher.launch_and_attach()
"""

from enum import Enum
from typing import Optional, Type
from .base import BrowserLauncher, BrowserConfig


class BrowserType(Enum):
    """
    Supported browser types.
    
    To add a new browser:
    1. Add enum value here (e.g., CHROME = "chrome")
    2. Create a new launcher class inheriting from BrowserLauncher
    3. Register it in BrowserFactory._BROWSER_CLASSES
    """
    COMET = "comet"
    # Future browsers can be added here:
    # CHROME = "chrome"
    # EDGE = "edge"
    # FIREFOX = "firefox"
    # BRAVE = "brave"


class BrowserFactory:
    """
    Factory for creating browser launcher instances.
    
    This factory uses a registry pattern to map BrowserType enums to
    their corresponding launcher classes.
    
    Note: Comet-specific implementation is in browser.comet package.
    """
    
    # Registry of browser types to launcher classes
    _BROWSER_CLASSES: dict[BrowserType, Type[BrowserLauncher]] = {
        # Comet is now in browser.comet package
        # BrowserType.COMET: CometBrowserLauncher,
        # Future browser launchers can be registered here:
        # BrowserType.CHROME: ChromeBrowserLauncher,
        # BrowserType.EDGE: EdgeBrowserLauncher,
    }
    
    @classmethod
    def create(
        cls,
        browser_type: BrowserType,
        config: Optional[BrowserConfig] = None
    ) -> BrowserLauncher:
        """
        Create a browser launcher instance.
        
        Args:
            browser_type: Type of browser to launch
            config: Optional browser configuration (uses defaults if None)
        
        Returns:
            BrowserLauncher instance for the specified browser
        
        Raises:
            ValueError: If browser_type is not supported
        
        Examples:
            >>> launcher = BrowserFactory.create(BrowserType.COMET)
            >>> driver = launcher.launch_and_attach()
            
            >>> custom_config = BrowserConfig(debug_port=9223)
            >>> launcher = BrowserFactory.create(BrowserType.COMET, custom_config)
        """
        launcher_class = cls._BROWSER_CLASSES.get(browser_type)
        
        if launcher_class is None:
            available = ", ".join(bt.value for bt in cls._BROWSER_CLASSES.keys())
            raise ValueError(
                f"Unsupported browser type: {browser_type.value}. "
                f"Available types: {available}"
            )
        
        return launcher_class(config)
    
    @classmethod
    def register_browser(
        cls,
        browser_type: BrowserType,
        launcher_class: Type[BrowserLauncher]
    ) -> None:
        """
        Register a new browser launcher class.
        
        This allows plugins or extensions to add new browser types
        without modifying this file.
        
        Args:
            browser_type: Enum value for the browser type
            launcher_class: Class that implements BrowserLauncher
        
        Example:
            >>> class MyCustomBrowser(BrowserLauncher):
            ...     # Implementation
            ...     pass
            >>> BrowserFactory.register_browser(
            ...     BrowserType.CUSTOM,
            ...     MyCustomBrowser
            ... )
        """
        if not issubclass(launcher_class, BrowserLauncher):
            raise TypeError(
                f"{launcher_class.__name__} must inherit from BrowserLauncher"
            )
        
        cls._BROWSER_CLASSES[browser_type] = launcher_class
    
    @classmethod
    def get_supported_browsers(cls) -> list[BrowserType]:
        """
        Get list of currently supported browser types.
        
        Returns:
            List of BrowserType enums that can be used with create()
        """
        return list(cls._BROWSER_CLASSES.keys())


# Convenience function for most common use case
def launch_browser(
    browser_type: BrowserType = BrowserType.COMET,
    config: Optional[BrowserConfig] = None,
    kill_existing: bool = True
) -> any:
    """
    Convenience function to quickly launch a browser and get a driver.
    
    This is a shortcut for:
        launcher = BrowserFactory.create(browser_type, config)
        driver = launcher.launch_and_attach(kill_existing)
    
    Args:
        browser_type: Type of browser to launch (default: Comet)
        config: Optional browser configuration
        kill_existing: Whether to kill existing browser processes first
    
    Returns:
        Selenium WebDriver instance
    
    Example:
        >>> driver = launch_browser()  # Launch Comet with defaults
        >>> driver.get("https://example.com")
    """
    launcher = BrowserFactory.create(browser_type, config)
    return launcher.launch_and_attach(kill_existing=kill_existing)
