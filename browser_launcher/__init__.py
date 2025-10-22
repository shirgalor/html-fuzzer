"""
Browser Launcher Module
=======================
Modular architecture for launching and controlling different browsers.

Currently supports:
- Comet (Perplexity browser)

Easy to extend for future browsers (Chrome, Edge, Firefox, etc.)

Usage:
    from browser_launcher import BrowserFactory, BrowserType, launch_browser
    
    # Simple usage - just launch Comet
    driver = launch_browser()
    
    # Factory pattern - more control
    launcher = BrowserFactory.create(BrowserType.COMET)
    driver = launcher.launch_and_attach()
    
    # Custom configuration
    from browser_launcher import BrowserConfig
    from pathlib import Path
    
    config = BrowserConfig(
        executable_path=Path("C:/path/to/comet.exe"),
        debug_port=9223,
        start_maximized=True,
        allow_file_access=True
    )
    launcher = BrowserFactory.create(BrowserType.COMET, config)
    driver = launcher.launch_and_attach()
"""

from .base import BrowserLauncher, BrowserConfig
from .factory import BrowserFactory, BrowserType, launch_browser

__all__ = [
    'BrowserLauncher',
    'BrowserConfig',
    'BrowserFactory',
    'BrowserType',
    'launch_browser',
]
