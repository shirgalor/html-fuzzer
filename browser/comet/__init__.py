"""
Perplexity Comet Browser Package
=================================
All Comet-specific implementations in one place.

Components:
- CometBrowser: Main browser class (facade)
- CometBrowserLauncher: Launches Comet executable
- CometNavigator: Navigation with Sidecar support
- CometPipeline: Workflow execution

Usage:
    from browser.comet import CometBrowser
    
    browser = CometBrowser()
    browser.launch()
"""

from .browser import CometBrowser
from .launcher import CometBrowserLauncher
from .navigator import CometNavigator
from .pipeline import CometPipeline

__all__ = [
    'CometBrowser',
    'CometBrowserLauncher',
    'CometNavigator',
    'CometPipeline'
]
