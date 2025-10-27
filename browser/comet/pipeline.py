"""
Comet Pipeline
==============
Pipeline implementation for Perplexity Comet browser.

Workflow (after Browser facade has launched and navigated to Sidecar):
1. Pre-workflow: Verify Sidecar loaded correctly
2. Execute workflow: Send query to Sidecar input (if query provided)
3. NEW: Conversion stage - Use conversion module for query/response
4. Post-workflow: Wait for response (if query submitted)
"""

import time
from typing import Optional

# Import from parent package's pipeline
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from pipeline.base import BasePipeline, PipelineConfig, PipelineResult
# NOTE: ConversionFactory imported lazily when needed (not at module level)


class CometPipeline(BasePipeline):
    """
    Pipeline implementation for Comet browser.
    
    Browser facade has already:
    - Launched Comet
    - Navigated to Perplexity Sidecar
    
    Pipeline workflow:
    - Verify Sidecar loaded
    - Optionally send query to Sidecar input field
    """
    
    def __init__(self, driver, navigator, config, **kwargs):
        """
        Initialize Comet pipeline.
        
        Args:
            driver: Selenium WebDriver (already attached to Comet)
            navigator: CometNavigator instance (already created)
            config: Pipeline configuration
            **kwargs: Optional parameters (query, submit, conversation, read_responses, use_conversion, save_text)
        """
        super().__init__(driver, navigator, config, **kwargs)
        
        # Extract optional query parameters
        self.query: Optional[str] = kwargs.get('query', None)
        self.submit_query: bool = kwargs.get('submit', False)
        
        # New conversation mode parameters
        self.conversation: Optional[list] = kwargs.get('conversation', None)
        self.read_responses: bool = kwargs.get('read_responses', True)
        
        # NEW: Conversion module flag
        self.use_conversion: bool = kwargs.get('use_conversion', False)
        self.conversion = None  # Will be initialized if needed
        
        # NEW: Text saving
        self.save_text: Optional[str] = kwargs.get('save_text', None)
    
    def get_browser_name(self) -> str:
        """Return the browser name."""
        return "Comet"
    
    def pre_workflow_steps(self) -> bool:
        """
        Pre-workflow: Navigate to Sidecar and verify it loaded.
        
        Returns:
            True if successful
        """
        print(f"[COMET] Navigating to Sidecar...")
        
        # Check if multiple tabs are open
        all_handles = self.driver.window_handles
        print(f"[DEBUG] Number of tabs open: {len(all_handles)}")
        
        if len(all_handles) > 1:
            print(f"[COMET] Multiple tabs detected - finding correct one...")
            
            SIDECAR_URL = "https://www.perplexity.ai/sidecar?copilot=true"
            correct_handle = None
            
            # Find the correct tab (first one with copilot=true)
            for handle in all_handles:
                self.driver.switch_to.window(handle)
                current_url = self.driver.current_url
                print(f"[DEBUG] Tab URL: {current_url}")
                
                if "copilot=true" in current_url:
                    print(f"[COMET] ✓ Found tab with copilot=true - using this one")
                    correct_handle = handle
                    break
            
            if correct_handle:
                self.driver.switch_to.window(correct_handle)
                print(f"[COMET] ✓ Switched to correct tab (ignoring other tabs)")
            else:
                # No correct tab found, use first tab
                self.driver.switch_to.window(all_handles[0])
                print(f"[COMET] No copilot=true tab found, will navigate to correct URL")
        
        # Navigate to Sidecar URL
        SIDECAR_URL = "https://www.perplexity.ai/sidecar?copilot=true"
        
        # Check current URL
        current_url = self.navigator.get_current_url()
        print(f"[COMET] Current URL before navigation: {current_url}")
        
        # Always navigate to ensure we have the correct URL with copilot parameter
        print(f"[COMET] Navigating to: {SIDECAR_URL}")
        nav_result = self.navigator.navigate_to_url(SIDECAR_URL, wait_time=5)
        
        if not nav_result.success:
            print(f"[COMET] ✗ Failed to navigate to Sidecar: {nav_result.message}")
            return False
        
        print(f"[COMET] Verifying Sidecar loaded...")
        current_url = self.navigator.get_current_url()
        print(f"[COMET] Current URL: {current_url}")
        
        if "sidecar" in current_url.lower():
            print(f"[COMET] ✓ Sidecar page confirmed")
            return True
        else:
            print(f"[COMET] ⚠ Warning: Not on Sidecar page, continuing anyway...")
            return True
    
    def execute_workflow(self) -> bool:
        """
        Execute workflow: Send query/conversation to Sidecar if provided.
        
        Supports two modes:
        1. Conversion mode (RECOMMENDED): Use conversion module for query/response
        2. Conversation mode: Multi-turn conversation (legacy - to be migrated to conversion)
        
        Returns:
            True if successful (or no query provided)
        """
        # Mode 1: Conversion module mode (RECOMMENDED!)
        if self.query and (self.use_conversion or self.submit_query):
            print(f"[COMET] === CONVERSION MODULE MODE ===")
            print(f"[COMET] Query: '{self.query}'")
            print(f"[COMET] Using conversion module for clean query/response...")
            
            # Lazy import to avoid circular dependencies
            from conversion import ConversionFactory, ConversionType
            
            # Create conversion handler
            if not self.conversion:
                print(f"[COMET] Creating conversion handler...")
                self.conversion = ConversionFactory.create(
                    ConversionType.COMET,
                    self.driver,
                    self.navigator
                )
            
            # Execute conversion: send query + capture response
            conversion_result = self.conversion.execute(
                query=self.query,
                capture=self.read_responses,
                save_text=self.save_text,  # Save text if specified
                max_wait=60.0
            )
            
            # Store result
            self.metadata['conversion_result'] = {
                'success': conversion_result.success,
                'query': conversion_result.query,
                'response': conversion_result.response,
                'text_filepath': conversion_result.text_filepath,
                'error': conversion_result.error
            }
            
            if conversion_result.success:
                print(f"[COMET] ✓ Conversion completed successfully")
                if conversion_result.response:
                    print(f"[COMET] ✓ Response captured ({len(conversion_result.response)} chars)")
                if conversion_result.text_filepath:
                    print(f"[COMET] ✓ Text saved to: {conversion_result.text_filepath}")
            else:
                print(f"[COMET] ✗ Conversion failed: {conversion_result.error}")
                return False
            
            return True
        
        # Mode 2: Conversation mode (legacy - will be migrated to conversion module later)
        if self.conversation:
            print(f"[COMET] === CONVERSATION MODE (LEGACY) ===")
            print(f"[COMET] ⚠ Conversation mode not yet migrated to conversion module")
            print(f"[COMET] Messages to send: {len(self.conversation)}")
            print(f"[COMET] This mode is deprecated - use single query conversion for now")
            
            # TODO: Implement multi-turn conversation in conversion module
            # For now, just return success and note it in metadata
            self.metadata['conversation'] = [
                {'role': 'system', 'content': 'Conversation mode not yet implemented with conversion module'}
            ]
            
            return True
        
        # No query or conversation provided
        print(f"[COMET] No query or conversation provided, skipping")
        return True
    
    def post_workflow_steps(self) -> bool:
        """
        Post-workflow: Wait for response if query was submitted.
        
        Returns:
            True (always succeeds)
        """
        print(f"[COMET] Workflow complete!")
        
        if self.query and self.submit_query:
            print(f"[COMET] Waiting for Perplexity response...")
            time.sleep(3)  # Wait for response to start loading
        
        return True
