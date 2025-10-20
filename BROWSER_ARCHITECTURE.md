# Browser Abstraction Architecture

## Overview

The `browser/` module provides the **highest level of abstraction** - a complete Browser class that bundles all browser-specific components into a single, easy-to-use interface.

## What is a Browser?

A `Browser` is a complete package that includes:

1. **Launcher**: How to launch and attach to the browser (from `browser_launcher/`)
2. **Navigator**: How to navigate pages and manage tabs (from `navigator/`)
3. **Pipeline**: Complete automation workflows (from `pipeline/`)
4. **Attack Names**: Browser-specific vulnerability test cases for fuzzing

## Architecture Layers

```
┌─────────────────────────────────────────────────────────┐
│           LAYER 4: BROWSER (HIGHEST)                    │
│         Complete browser system abstraction             │
│              (FACADE PATTERN)                           │
│                                                         │
│  Browser provides access to all components:             │
│  ├── Launcher   (Layer 1 - independent)                │
│  ├── Navigator  (Layer 2 - independent)                │
│  ├── Pipeline   (Layer 3 - uses Launcher+Navigator)    │
│  └── Attack names (browser-specific tests)             │
│                                                         │
│  Created by: BrowserFactory.create(BrowserType)        │
└───────────────┬─────────────────────────────────────────┘
                │
    ┌───────────┼──────────┬──────────────┐
    ▼           ▼          ▼              ▼
┌────────────┐ ┌──────────┐ ┌──────────┐ ┌─────────┐
│ LAYER 1:   │ │ LAYER 2: │ │ LAYER 3: │ │ ATTACKS │
│ LAUNCHER   │ │ NAVIGATOR│ │ PIPELINE │ │  NAMES  │
│            │ │          │ │          │ │         │
│ Launching  │ │Navigation│ │Workflows │ │ Testing │
└────────────┘ └──────────┘ └────┬─────┘ └─────────┘
                                  │
                         Uses Launcher + Navigator
```

**Important Design Decision:**

Browser is a **FACADE**, not a hierarchy. It owns all 3 layers as **siblings**:
- Launcher and Navigator are **independent** - can be used separately
- Pipeline **composes** Launcher + Navigator for complete workflows
- Browser provides **direct access** to all three

This means you can:
- Use just the launcher: `browser.launch()`
- Use just the navigator: `browser.navigate_to(url)`
- Use the complete pipeline: `browser.run_pipeline(config)`

## Design Pattern

The Browser uses the **Facade Pattern** to provide a simple interface to a complex subsystem:

```python
class BaseBrowser(ABC):
    # Creates all components
    @abstractmethod
    def create_launcher(self) -> BrowserLauncher
    
    @abstractmethod
    def create_navigator(self, driver) -> Navigator
    
    @abstractmethod
    def create_pipeline(self, config) -> Pipeline
    
    @abstractmethod
    def get_attack_names(self) -> List[str]
    
    # High-level methods
    def launch(self)
    def navigate_to(self, url)
    def run_pipeline(self, config)
    def quit()
```

## File Structure

```
browser/
├── __init__.py          # Public API exports
├── base.py              # BaseBrowser abstract class
├── comet_browser.py     # CometBrowser implementation
└── factory.py           # BrowserFactory for creating browsers
```

## Implementation: CometBrowser

```python
class CometBrowser(BaseBrowser):
    """Complete Comet browser with all components."""
    
    def create_launcher(self):
        # Returns CometBrowserLauncher
        return BrowserFactory.create(BrowserType.COMET)
    
    def create_navigator(self, driver):
        # Returns CometNavigator
        return NavigatorFactory.create(NavigatorType.COMET, driver)
    
    def create_pipeline(self, config):
        # Returns CometPipeline
        return PipelineFactory.create(
            PipelineType.COMET,
            browser_launcher=self.create_launcher(),
            navigator_factory=lambda d: self.create_navigator(d),
            config=config
        )
    
    def get_attack_names(self):
        return [
            "XSS_REFLECTED", "XSS_STORED", "CSRF",
            "SIDECAR_INJECTION",  # Comet-specific
            "ASSISTANT_PROMPT_INJECTION",  # Comet-specific
            # ... and more
        ]
    
    # Comet-specific methods
    def open_sidecar(self):
        """Open Perplexity Sidecar."""
        
    def activate_assistant(self):
        """Click Assistant button."""
```

## Usage Examples

### Example 1: Simple Navigation

```python
from browser import BrowserFactory, BrowserType

# Create browser
browser = BrowserFactory.create(BrowserType.COMET)

# Launch and navigate
browser.launch()
browser.navigate_to("https://example.com")

# Get info
info = browser.get_browser_info()
print(f"Browser: {info.name}")
print(f"Tabs: {len(browser.get_window_handles())}")

# Clean up
browser.quit()
```

### Example 2: Context Manager (Recommended)

```python
from browser import BrowserFactory, BrowserType

# Auto-launch and auto-cleanup
with BrowserFactory.create(BrowserType.COMET) as browser:
    browser.navigate_to("https://example.com")
    print(f"Tabs: {len(browser.get_window_handles())}")
    # Browser automatically closes when exiting with block
```

### Example 3: Using Pipeline

```python
from browser import BrowserFactory, BrowserType
from pipeline import PipelineConfig

browser = BrowserFactory.create(BrowserType.COMET)

# Configure pipeline
config = PipelineConfig(
    target_url="https://example.com",
    keep_open=True
)

# Run complete workflow (launch → Sidecar → navigate → Assistant)
result = browser.run_pipeline(config)

if result.success:
    print(f"Steps completed: {result.steps_completed}")
    browser.quit()
```

### Example 4: Attack Names for Fuzzing

```python
from browser import BrowserFactory, BrowserType

browser = BrowserFactory.create(BrowserType.COMET)
attacks = browser.get_attack_names()

print(f"Testing {len(attacks)} attack vectors:")
for attack in attacks:
    print(f"  - {attack}")

# Use for fuzzing
browser.launch()
for attack in attacks:
    # Run attack test
    print(f"Testing {attack}...")
```

### Example 5: Comet-Specific Features

```python
from browser import BrowserFactory, BrowserType

with BrowserFactory.create(BrowserType.COMET) as browser:
    # Comet-specific method
    browser.open_sidecar()
    
    # Navigate
    browser.navigate_to("https://example.com")
    
    # Comet-specific method
    browser.activate_assistant()
```

### Example 6: Multiple HTML Files

```python
from pathlib import Path
from browser import BrowserFactory, BrowserType

htmls_folder = Path("htmls")

with BrowserFactory.create(BrowserType.COMET) as browser:
    # Open Sidecar first
    browser.open_sidecar()
    
    # Open all HTML files
    files = browser.open_local_files(
        htmls_folder,
        pattern="*.html",
        new_tabs=True
    )
    
    print(f"Opened {len(files)} files")
    
    # Activate Assistant
    browser.activate_assistant()
```

## Comparison: Before vs After

### Before (Low-Level Components)

```python
# Had to manually create and wire up components
from browser_launcher import BrowserFactory as LauncherFactory, BrowserType as LauncherType
from navigator import NavigatorFactory as NavFactory, NavigatorType as NavType
from pipeline import PipelineFactory as PipeFactory, PipelineType as PipeType, PipelineConfig

# Step 1: Create launcher
launcher = LauncherFactory.create(LauncherType.COMET)

# Step 2: Launch browser
driver = launcher.launch_and_attach()

# Step 3: Create navigator
navigator = NavFactory.create(NavType.COMET, driver)

# Step 4: Navigate
navigator.navigate_to_url("https://example.com")

# Step 5: Cleanup
driver.quit()
```

**Problems:**
- ❌ Too many imports from different modules
- ❌ Manual component wiring
- ❌ Need to know internal architecture
- ❌ Verbose code

### After (Browser Abstraction)

```python
# Simple high-level interface
from browser import BrowserFactory, BrowserType

with BrowserFactory.create(BrowserType.COMET) as browser:
    browser.navigate_to("https://example.com")
```

**Benefits:**
- ✅ Single import
- ✅ Automatic component wiring
- ✅ Don't need to know internals
- ✅ Clean, readable code

## Adding New Browsers

To add a new browser (e.g., Chrome):

### Step 1: Add to BrowserType Enum

```python
# browser/factory.py
class BrowserType(Enum):
    COMET = "comet"
    CHROME = "chrome"  # NEW
```

### Step 2: Create Browser Class

```python
# browser/chrome_browser.py
from .base import BaseBrowser, BrowserInfo
from browser_launcher import BrowserFactory as LauncherFactory, BrowserType as LauncherType
from navigator import NavigatorFactory as NavFactory, NavigatorType as NavType
from pipeline import PipelineFactory as PipeFactory, PipelineType as PipeType

class ChromeBrowser(BaseBrowser):
    def get_browser_info(self):
        return BrowserInfo(
            name="Google Chrome",
            supports_devtools=True,
            supports_extensions=True
        )
    
    def create_launcher(self):
        return LauncherFactory.create(LauncherType.CHROME)
    
    def create_navigator(self, driver):
        return NavFactory.create(NavType.CHROME, driver)
    
    def create_pipeline(self, config):
        launcher = self.create_launcher()
        nav_factory = lambda d: self.create_navigator(d)
        return PipeFactory.create(
            PipeType.CHROME,
            browser_launcher=launcher,
            navigator_factory=nav_factory,
            config=config
        )
    
    def get_attack_names(self):
        return [
            "XSS_REFLECTED",
            "CHROME_EXTENSION_XSS",  # Chrome-specific
            # ... more
        ]
```

### Step 3: Register in Factory

```python
# browser/factory.py
from .chrome_browser import ChromeBrowser

_BROWSER_CLASSES = {
    BrowserType.COMET: CometBrowser,
    BrowserType.CHROME: ChromeBrowser,  # NEW
}
```

### Step 4: Update Exports

```python
# browser/__init__.py
from .chrome_browser import ChromeBrowser

__all__ = [
    "BaseBrowser",
    "CometBrowser",
    "ChromeBrowser",  # NEW
    "BrowserFactory",
    "BrowserType",
]
```

That's it! Usage is identical:

```python
browser = BrowserFactory.create(BrowserType.CHROME)
browser.launch()
browser.navigate_to("https://example.com")
```

## Attack Names

Each browser defines its own attack/vulnerability test cases:

### CometBrowser Attack Names

```python
attacks = CometBrowser().get_attack_names()

# Returns:
[
    # Standard web attacks
    "XSS_REFLECTED", "XSS_STORED", "XSS_DOM",
    "CSRF", "CLICKJACKING", "OPEN_REDIRECT",
    "SQL_INJECTION", "COMMAND_INJECTION",
    
    # Browser-specific
    "PROTOTYPE_POLLUTION", "POSTMESSAGE_XSS",
    "CORS_MISCONFIGURATION", "CSP_BYPASS",
    
    # Comet-specific (AI features)
    "SIDECAR_INJECTION",
    "ASSISTANT_PROMPT_INJECTION",
    "AI_CONTEXT_POISONING",
    "DEVTOOLS_PROTOCOL_ABUSE",
    
    # File handling
    "LOCAL_FILE_INCLUSION", "FILE_URI_LEAK",
    
    # Chromium engine
    "V8_EXPLOITATION", "RENDERER_RCE",
    "SANDBOX_ESCAPE", "USE_AFTER_FREE",
]
```

These can be used for:
- **Fuzzing**: Test each attack vector systematically
- **Security testing**: Verify browser handles attacks safely
- **Reporting**: Document which attacks were tested

## Browser Composition

The Browser class uses **composition** to assemble components:

```
CometBrowser
├─ _launcher: CometBrowserLauncher
│  ├─ Finds Comet executable
│  ├─ Manages ChromeDriver version
│  ├─ Launches with DevTools port
│  └─ Attaches Selenium
│
├─ _navigator: CometNavigator
│  ├─ navigate_to_url()
│  ├─ open_local_html_files()
│  ├─ File:// URL fallbacks
│  └─ Tab management
│
├─ _pipeline: CometPipeline
│  ├─ Pre-nav: Open Sidecar
│  ├─ Navigate to target
│  └─ Post-nav: Activate Assistant
│
└─ get_attack_names()
   └─ Returns Comet-specific attack list
```

## Benefits of Browser Abstraction

### 1. Simplicity
```python
# Before: 10+ lines of setup code
# After:
browser = BrowserFactory.create(BrowserType.COMET)
browser.launch()
```

### 2. Encapsulation
- Internal components are hidden
- Users don't need to understand the 4-layer architecture
- Implementation can change without affecting user code

### 3. Consistency
- Same interface for all browsers
- Switch browsers by changing one line: `BrowserType.COMET` → `BrowserType.CHROME`

### 4. Context Manager Support
```python
with BrowserFactory.create(BrowserType.COMET) as browser:
    # Auto-launch on entry
    browser.navigate_to("https://example.com")
    # Auto-cleanup on exit
```

### 5. Browser-Specific Features
```python
# Comet-specific methods
browser.open_sidecar()
browser.activate_assistant()

# Chrome-specific methods (future)
browser.load_extensions()
browser.open_devtools()
```

### 6. Attack Testing
```python
# Easy access to browser-specific vulnerabilities
attacks = browser.get_attack_names()
for attack in attacks:
    run_fuzzing_test(attack)
```

## When to Use Each Layer

### Use Browser (Layer 4) When:
- ✅ You want the simplest interface
- ✅ You need a complete browser system
- ✅ You want browser-specific attack names
- ✅ You're building an end-user application

### Use Pipeline (Layer 3) When:
- ✅ You need custom workflow orchestration
- ✅ You want to customize pre/post-navigation steps
- ✅ You're building complex automation

### Use Navigator (Layer 2) When:
- ✅ You only need navigation, not launching
- ✅ You have an existing WebDriver instance
- ✅ You need fine-grained control over navigation

### Use BrowserLauncher (Layer 1) When:
- ✅ You only need to launch the browser
- ✅ You're building your own navigation layer
- ✅ You need maximum control

## Real-World Example: Fuzzing Application

```python
from browser import BrowserFactory, BrowserType
from pathlib import Path

def fuzz_html_files(folder: Path):
    """Fuzz all HTML files with all attack vectors."""
    
    # Create browser
    browser = BrowserFactory.create(BrowserType.COMET)
    browser.launch()
    
    # Get attack names
    attacks = browser.get_attack_names()
    html_files = list(folder.glob("*.html"))
    
    print(f"Fuzzing {len(html_files)} files with {len(attacks)} attacks")
    
    # Test each file with each attack
    for html_file in html_files:
        for attack in attacks:
            print(f"\nTesting {html_file.name} with {attack}...")
            
            # Navigate to file
            browser.navigate_to(html_file.as_uri())
            
            # Run attack-specific test
            run_attack_test(browser, attack)
    
    browser.quit()

# Usage
fuzz_html_files(Path("htmls"))
```

## Summary

The Browser abstraction is the **capstone** of the 4-layer architecture:

- **Layer 1 (BrowserLauncher)**: Launch browsers
- **Layer 2 (Navigator)**: Navigate pages
- **Layer 3 (Pipeline)**: Complete workflows
- **Layer 4 (Browser)**: Everything bundled together ← **YOU ARE HERE**

**Key Points:**
- ✅ Simplest interface for complete browser operations
- ✅ Bundles launcher, navigator, pipeline, and attack names
- ✅ Context manager support for auto-cleanup
- ✅ Browser-specific features (like Sidecar, Assistant)
- ✅ Attack names for fuzzing and security testing
- ✅ Same extension pattern as other layers (enum → class → register)

Use the Browser class when you want **simplicity and completeness**!
