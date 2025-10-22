"""
Comet Browser
=============
Complete Comet browser implementation with all components.

Bundles together:
- CometBrowserLauncher: Launch Perplexity Comet
- CometNavigator: Navigate with file:// URL fallbacks
- CometPipeline: Workflow with Sidecar + Assistant
- Attack names: Comet-specific vulnerabilities
"""

from typing import List
from .base import BaseBrowser, BrowserInfo
from browser_launcher import BrowserFactory, BrowserType
from navigator import NavigatorFactory, NavigatorType
from pipeline import PipelineFactory, PipelineType


class CometBrowser(BaseBrowser):
    """
    Complete Comet browser implementation.
    
    Comet is a Chromium-based browser by Perplexity with:
    - Built-in AI Assistant
    - Perplexity Sidecar integration
    - Chrome DevTools Protocol support
    
    Example:
        >>> browser = CometBrowser()
        >>> browser.launch()
        >>> browser.navigate_to("https://example.com")
        >>> attacks = browser.get_attack_names()
        >>> browser.quit()
        
        # Or using context manager
        >>> with CometBrowser() as browser:
        ...     browser.navigate_to("https://test.com")
    """
    
    def get_browser_info(self) -> BrowserInfo:
        """Get Comet browser information."""
        return BrowserInfo(
            name="Perplexity Comet",
            version=None,  # Could be detected from executable
            executable_path=None,  # Set by launcher
            supports_devtools=True,
            supports_extensions=False  # Comet doesn't support Chrome extensions
        )
    
    def create_launcher(self):
        """
        Create CometBrowserLauncher.
        
        Returns:
            CometBrowserLauncher instance
        """
        return BrowserFactory.create(BrowserType.COMET)
    
    def create_navigator(self, driver):
        """
        Create CometNavigator.
        
        Args:
            driver: Selenium WebDriver instance
            
        Returns:
            CometNavigator instance
        """
        return NavigatorFactory.create(NavigatorType.COMET, driver)
    
    def create_pipeline(self, driver, navigator, config, **kwargs):
        """
        Create CometPipeline.
        
        The Comet pipeline receives driver and navigator from Browser facade.
        Browser has already navigated to Sidecar URL.
        Pipeline just runs workflow (e.g., send query).
        
        Args:
            driver: Selenium WebDriver (already attached to Comet)
            navigator: CometNavigator instance (already created)
            config: PipelineConfig instance
            **kwargs: Optional parameters (query, submit)
            
        Returns:
            CometPipeline instance
        """
        return PipelineFactory.create(
            PipelineType.COMET,
            driver=driver,
            navigator=navigator,
            config=config,
            **kwargs
        )
    
    def get_attack_names(self) -> List[str]:
        """
        Get Comet-specific attack/vulnerability names.
        
        These are test cases specific to Comet browser:
        - Chromium-based attacks (inherited)
        - Comet-specific features (Assistant, Sidecar)
        - AI integration vulnerabilities
        
        Returns:
            List of attack names for fuzzing/testing
        """
        return [
            # Standard web attacks (Chromium-based)
            "XSS_REFLECTED",
            "XSS_STORED",
            "XSS_DOM",
            "CSRF",
            "CLICKJACKING",
            "OPEN_REDIRECT",
            "PATH_TRAVERSAL",
            "SQL_INJECTION",
            "COMMAND_INJECTION",
            "XXE",
            "SSRF",
            
            # Browser-specific attacks
            "PROTOTYPE_POLLUTION",
            "POSTMESSAGE_XSS",
            "CORS_MISCONFIGURATION",
            "CSP_BYPASS",
            "SRI_BYPASS",
            "DANGLING_MARKUP",
            "MUTATION_XSS",
            
            # Comet-specific (AI/Sidecar related)
            "SIDECAR_INJECTION",
            "ASSISTANT_PROMPT_INJECTION",
            "AI_CONTEXT_POISONING",
            "DEVTOOLS_PROTOCOL_ABUSE",
            
            # File handling (especially for file:// URLs)
            "LOCAL_FILE_INCLUSION",
            "FILE_URI_LEAK",
            "SAME_ORIGIN_BYPASS",
            
            # Chromium engine attacks
            "V8_EXPLOITATION",
            "RENDERER_RCE",
            "SANDBOX_ESCAPE",
            "USE_AFTER_FREE",
            "TYPE_CONFUSION",
            "BUFFER_OVERFLOW",
        ]
    
    def activate_assistant(self) -> bool:
        """
        Comet-specific: Activate the Assistant UI button.
        
        Returns:
            True if activation successful, False otherwise
        """
        if not self._is_launched:
            raise RuntimeError("Browser not launched. Call launch() first.")
        
        try:
            import archive.comet_ui_automation as comet_ui
            print("[INFO] Activating Comet Assistant...")
            success = comet_ui.click_assistant_button_ui()
            
            if success:
                print("[SUCCESS] Assistant activated")
            else:
                print("[WARNING] Failed to activate Assistant")
            
            return success
            
        except Exception as e:
            print(f"[ERROR] Assistant activation failed: {e}")
            return False
    
    def open_sidecar(self, wait_time: int = 3) -> bool:
        """
        Comet-specific: Open Perplexity Sidecar.
        
        Args:
            wait_time: Seconds to wait for Sidecar to load
            
        Returns:
            True if Sidecar opened successfully, False otherwise
        """
        if not self._is_launched:
            raise RuntimeError("Browser not launched. Call launch() first.")
        
        SIDECAR_URL = "https://www.perplexity.ai/sidecar?copilot=true"
        
        print(f"[INFO] Opening Perplexity Sidecar...")
        result = self.navigate_to(SIDECAR_URL, wait_time=wait_time)
        
        if result.success:
            print(f"[SUCCESS] Sidecar opened")
            return True
        else:
            print(f"[WARNING] Failed to open Sidecar: {result.message}")
            return False
