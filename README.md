# HTML Fuzzer - Browser Automation Project

A modular browser automation framework for testing HTML files with AI-powered browser agents.

## Features

- **Modular Browser Architecture**: Easy-to-extend abstract base classes
- **Comet Browser Support**: Launch and control Perplexity Comet browser
- **Selenium Integration**: Automated ChromeDriver version matching
- **Local HTML Testing**: Open multiple HTML files in tabs
- **AI Agent Ready**: Integration with browser-use for LLM-powered automation

## Installation

### Prerequisites

- Python 3.12+
- Windows (currently)
- Perplexity Comet browser installed

### Setup

```powershell
# Create virtual environment with uv
uv venv --python 3.12
.\.venv\Scripts\Activate.ps1

# Install dependencies
uv pip install -r requirements.txt

# Optional: Install browser-use for AI agents
uv pip install browser-use langchain-openai playwright
```

## Project Structure

```
html-fuzzer/
├── browser_launcher/          # Modular browser launcher framework
│   ├── __init__.py           # Public API exports
│   ├── base.py               # Abstract BrowserLauncher base class
│   ├── comet_launcher.py     # Comet browser implementation
│   └── factory.py            # BrowserFactory with BrowserType enum
├── navigator/                # Modular navigation framework
│   ├── __init__.py           # Public API exports
│   ├── base.py               # Abstract Navigator base class
│   ├── comet_navigator.py    # Comet navigator implementation
│   └── factory.py            # NavigatorFactory with NavigatorType enum
├── pipeline/                 # Browser-specific workflow pipelines (NEW!)
│   ├── __init__.py           # Public API exports
│   ├── base.py               # Abstract BasePipeline class
│   ├── comet_pipeline.py     # Comet workflow (Sidecar + Assistant)
│   └── factory.py            # PipelineFactory with PipelineType enum
├── htmls/                    # HTML test files
│   ├── test.html
│   ├── test2.html
│   └── test3.html
├── archive/                  # Legacy automation code
│   └── comet_ui_automation.py # PyAutoGUI Assistant button clicking
├── main.py                   # Entry point using pipeline architecture
├── pipeline_old.py           # Old single pipeline (backup)
├── navigation.py             # Legacy navigation utilities
├── launch_comet.py           # Legacy Comet launcher
├── ARCHITECTURE.md           # Browser launcher architecture docs
├── NAVIGATOR_ARCHITECTURE.md # Navigator architecture docs
├── PIPELINE_ARCHITECTURE.md  # Pipeline architecture docs (NEW!)
└── requirements.txt          # Python dependencies
```

## Architecture

This project follows a **consistent 3-layer modular architecture**:

### 1. Browser Launcher Layer
- **Purpose**: Launch and attach to different browsers
- **Pattern**: Abstract base class + Factory
- **Files**: `browser_launcher/`
- **Extensible**: Add new browsers by implementing `BrowserLauncher`

### 2. Navigator Layer
- **Purpose**: Navigate and interact with pages
- **Pattern**: Abstract base class + Factory
- **Files**: `navigator/`
- **Extensible**: Add browser-specific navigation by implementing `Navigator`

### 3. Pipeline Layer (NEW!)
- **Purpose**: Complete automation workflows with browser-specific steps
- **Pattern**: Template Method + Factory
- **Files**: `pipeline/`
- **Extensible**: Add browser workflows by implementing `BasePipeline`

**Why this architecture?**
- ✅ **Separation of Concerns**: Each layer has one responsibility
- ✅ **Open/Closed Principle**: Add new browsers without modifying existing code
- ✅ **Testability**: Each component can be tested independently
- ✅ **Consistency**: All three modules follow identical extension patterns

See detailed docs:
- [Browser Launcher Architecture](ARCHITECTURE.md)
- [Navigator Architecture](NAVIGATOR_ARCHITECTURE.md)
- [Pipeline Architecture](PIPELINE_ARCHITECTURE.md) ← **NEW!**

## Usage

### Option 1: Using Pipeline (Recommended for Complete Workflows)

The pipeline handles the complete workflow including browser-specific initialization:

```python
from pipeline import PipelineFactory, PipelineType, PipelineConfig
from browser_launcher import BrowserFactory, BrowserType
from navigator import NavigatorFactory, NavigatorType

# Create dependencies
browser_launcher = BrowserFactory.create(BrowserType.COMET)
navigator_factory = lambda driver: NavigatorFactory.create(NavigatorType.COMET, driver)

# Configure workflow
config = PipelineConfig(
    target_url="https://example.com",
    load_wait_time=5,
    keep_open=True
)

# Run pipeline (opens Sidecar, navigates, activates Assistant)
pipeline = PipelineFactory.create(
    PipelineType.COMET,
    browser_launcher=browser_launcher,
    navigator_factory=navigator_factory,
    config=config
)

result = pipeline.run()
```

**Comet Pipeline automatically:**
1. Launches Comet browser
2. Opens Perplexity Sidecar (https://www.perplexity.ai/sidecar?copilot=true)
3. Navigates to your target URL
4. Activates the Assistant button
5. Handles cleanup

### Option 2: Using Individual Components

For more control, use the modular components directly:

```python
from browser_launcher import launch_browser, BrowserType
from navigator import NavigatorFactory, NavigatorType

# Launch browser
driver = launch_browser(browser_type=BrowserType.COMET)

# Create navigator
navigator = NavigatorFactory.create(NavigatorType.COMET, driver)

# Navigate
result = navigator.navigate_to_url("https://example.com")

# Clean up
driver.quit()
```

### Option 3: Factory Pattern for Custom Configuration

```python
from browser_launcher import BrowserFactory, BrowserType, BrowserConfig
from pathlib import Path

# Create custom configuration
config = BrowserConfig(
    executable_path=Path("C:/path/to/comet.exe"),
    debug_port=9222,
    start_maximized=True,
    allow_file_access=True,
    disable_web_security=True,
    user_data_dir=Path("./comet_profile")
)

# Create launcher
launcher = BrowserFactory.create(BrowserType.COMET, config)

# Launch and attach
driver = launcher.launch_and_attach(kill_existing=True)

# Use the driver
driver.get("file:///C:/path/to/test.html")

# Clean up
launcher.quit()
```

### Context Manager Support

```python
from browser_launcher import BrowserFactory, BrowserType

with BrowserFactory.create(BrowserType.COMET) as driver:
    driver.get("https://example.com")
    print(driver.title)
# Automatically cleaned up
```

### Opening Multiple HTML Files

```python
from browser_launcher import launch_browser
from pathlib import Path
import navigation

driver = launch_browser()

# Open all HTML files in the htmls folder
html_dir = Path("htmls")
urls = navigation.open_local_html_files(
    driver, 
    html_dir, 
    pattern="*.html",
    new_tabs=True,
    wait_per_page=0.5
)

print(f"Opened {len(urls)} HTML files")
```

## Extending for New Browsers

The architecture is designed to make adding new browsers easy:

### 1. Add Browser Type to Enum

```python
# browser_launcher/factory.py
class BrowserType(Enum):
    COMET = "comet"
    CHROME = "chrome"  # Add new type here
```

### 2. Create Launcher Class

```python
# browser_launcher/chrome_launcher.py
from .base import BrowserLauncher, BrowserConfig

class ChromeBrowserLauncher(BrowserLauncher):
    def get_launch_args(self) -> List[str]:
        # Return Chrome-specific arguments
        return [...]
    
    def get_process_names(self) -> List[str]:
        return ["chrome", "chrome.exe"]
    
    def attach_selenium(self):
        # Implement Selenium attachment
        pass
```

### 3. Register in Factory

```python
# browser_launcher/factory.py
_BROWSER_CLASSES = {
    BrowserType.COMET: CometBrowserLauncher,
    BrowserType.CHROME: ChromeBrowserLauncher,  # Register here
}
```

That's it! The new browser is now available:

```python
driver = launch_browser(BrowserType.CHROME)
```

## API Reference

### BrowserConfig

Configuration dataclass for browser launchers.

**Attributes:**
- `executable_path: Path` - Path to browser executable
- `debug_port: int` - Chrome DevTools debugging port (default: 9222)
- `start_maximized: bool` - Start browser maximized (default: True)
- `allow_file_access: bool` - Allow file:// URLs (default: True)
- `disable_web_security: bool` - Disable web security (default: False)
- `user_data_dir: Optional[Path]` - Custom user data directory
- `extra_args: List[str]` - Additional command-line arguments
- `timeout: float` - DevTools connection timeout (default: 12.0)

### BrowserLauncher (Abstract Base Class)

**Methods:**
- `launch_and_attach(kill_existing=True)` - Complete workflow to launch browser and attach Selenium
- `launch_browser(try_alternate_format=False)` - Launch the browser process
- `wait_for_devtools()` - Wait for DevTools endpoint to be ready
- `attach_selenium()` - Attach Selenium WebDriver (abstract, must implement)
- `kill_existing_processes()` - Kill any running browser instances
- `quit()` - Clean up resources

### BrowserFactory

**Methods:**
- `create(browser_type, config=None)` - Create a browser launcher instance
- `register_browser(browser_type, launcher_class)` - Register new browser type
- `get_supported_browsers()` - Get list of supported browsers

### Convenience Functions

- `launch_browser(browser_type=BrowserType.COMET, config=None, kill_existing=True)` - Quick launch shortcut

## Troubleshooting

### "No module named 'requests'"

Install dependencies in your virtual environment:
```powershell
python -m pip install -r requirements.txt
```

### "ChromeDriver version mismatch"

The Comet launcher automatically detects browser version and downloads matching ChromeDriver. If issues persist:
1. Delete cached ChromeDriver folders
2. Run again - it will download fresh

### "DevTools not reachable"

- Ensure no other Comet instances are running
- Try increasing timeout in BrowserConfig
- Check if Comet supports `--remote-debugging-port` flag

## License

MIT

## Contributing

When adding new browser support:
1. Inherit from `BrowserLauncher`
2. Implement all abstract methods
3. Add to `BrowserType` enum
4. Register in `BrowserFactory`
5. Add tests
6. Update this README
