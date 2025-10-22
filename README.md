# HTML Fuzzer - Comet Browser Automation# HTML Fuzzer - Comet Browser Automation# HTML Fuzzer - Browser Automation Project



Python-based browser automation framework for Perplexity Comet with clean, package-based architecture.



## 🎯 OverviewPython-based browser automation framework for Perplexity Comet with clean, package-based architecture.A modular browser automation framework for testing HTML files with AI-powered browser agents.



This project provides a modular framework for automating Perplexity Comet browser. It's built around a **Hybrid Facade + Pipeline Pattern** that separates infrastructure setup from business logic, making it easy to add new browsers and workflows.



## ✨ Features## 🎯 Overview## Features



- **Comet Browser Support**: Launch and control Perplexity Comet

- **Sidecar Automation**: Send queries to Perplexity Sidecar

- **Package-Based Organization**: All browser-specific code grouped in `browser/<name>/` packagesThis project provides a modular framework for automating Perplexity Comet browser. It's built around a **Hybrid Facade + Pipeline Pattern** that separates infrastructure setup from business logic, making it easy to add new browsers and workflows.- **Modular Browser Architecture**: Easy-to-extend abstract base classes

- **Clean Architecture**: Facade for setup, Pipeline for workflows

- **Selenium WebDriver**: Full automation capabilities with explicit waits- **Comet Browser Support**: Launch and control Perplexity Comet browser

- **Session Persistence**: Maintains user data across launches

## ✨ Features- **Selenium Integration**: Automated ChromeDriver version matching

## 📁 Project Structure

- **Local HTML Testing**: Open multiple HTML files in tabs

```

browser/- **Comet Browser Support**: Launch and control Perplexity Comet- **AI Agent Ready**: Integration with browser-use for LLM-powered automation

├── base.py              # BaseBrowser (orchestrator facade)

├── factory.py           # BrowserFactory for creating browsers- **Sidecar Automation**: Send queries to Perplexity Sidecar

└── comet/               # ← ALL COMET CODE HERE

    ├── __init__.py      # Package exports- **Package-Based Organization**: All browser-specific code grouped in `browser/<name>/` packages## Installation

    ├── browser.py       # CometBrowser (facade)

    ├── launcher.py      # CometBrowserLauncher- **Clean Architecture**: Facade for setup, Pipeline for workflows

    ├── navigator.py     # CometNavigator (navigation + Sidecar)

    └── pipeline.py      # CometPipeline (workflow)- **Selenium WebDriver**: Full automation capabilities with explicit waits### Prerequisites



browser_launcher/        # Base launcher abstractions- **Session Persistence**: Maintains user data across launches

├── base.py

└── factory.py- Python 3.12+



navigator/               # Base navigator abstractions## 📁 Project Structure- Windows (currently)

├── base.py

└── factory.py- Perplexity Comet browser installed



pipeline/                # Base pipeline abstractions```

├── base.py

└── factory.pybrowser/### Setup



main.py                  # Main entry point├── base.py              # BaseBrowser (orchestrator facade)

requirements.txt

```├── factory.py           # BrowserFactory for creating browsers```powershell



## 🏗️ Architecture└── comet/               # ← ALL COMET CODE HERE# Create virtual environment with uv



### Component Responsibilities    ├── __init__.py      # Package exportsuv venv --python 3.12



| Component | Purpose | Location |    ├── browser.py       # CometBrowser (facade).\.venv\Scripts\Activate.ps1

|-----------|---------|----------|

| **Browser** | High-level orchestrator - launches browser, creates components, manages lifecycle | `browser/comet/browser.py` |    ├── launcher.py      # CometBrowserLauncher

| **Launcher** | Start Comet executable, attach Selenium WebDriver | `browser/comet/launcher.py` |

| **Navigator** | Page navigation, element interaction, send Sidecar queries | `browser/comet/navigator.py` |    ├── navigator.py     # CometNavigator (navigation + Sidecar)# Install dependencies

| **Pipeline** | Complete workflow: navigate → execute → finalize | `browser/comet/pipeline.py` |

    └── pipeline.py      # CometPipeline (workflow)uv pip install -r requirements.txt

### Design Pattern: Hybrid Facade + Pipeline



```

┌─────────────────────────────────────────────────────────┐browser_launcher/        # Base launcher abstractions# Optional: Install browser-use for AI agents

│                   CometBrowser (Facade)                 │

│  • Launches browser                                      │├── base.pyuv pip install browser-use langchain-openai playwright

│  • Creates launcher, navigator, pipeline                │

│  • Manages lifecycle                                     │└── factory.py```

└─────────────────────────────────────────────────────────┘

                          │

                          ↓

              ┌───────────────────────┐navigator/               # Base navigator abstractions## Project Structure

              │  CometPipeline        │

              │  • Navigation         │├── base.py

              │  • Workflow execution │

              │  • Business logic     │└── factory.py```

              └───────────────────────┘

```html-fuzzer/



**Why this architecture?**pipeline/                # Base pipeline abstractions├── browser_launcher/          # Modular browser launcher framework



- ✅ **Separation of Concerns**: Infrastructure (Browser) vs. Logic (Pipeline)├── base.py│   ├── __init__.py           # Public API exports

- ✅ **Timing Control**: Pipeline handles navigation after browser setup (critical for Comet's saved sessions)

- ✅ **Package Isolation**: All Comet code in one place (`browser/comet/`)└── factory.py│   ├── base.py               # Abstract BrowserLauncher base class

- ✅ **Easy Extension**: Add new browsers by creating `browser/<name>/` packages

│   ├── comet_launcher.py     # Comet browser implementation

## 🚀 Quick Start

main_browser_abstraction.py  # Test entry point│   └── factory.py            # BrowserFactory with BrowserType enum

### Installation

requirements.txt├── navigator/                # Modular navigation framework

```powershell

# Create virtual environment```│   ├── __init__.py           # Public API exports

uv venv --python 3.12

.\.venv\Scripts\Activate.ps1│   ├── base.py               # Abstract Navigator base class



# Install dependencies## 🏗️ Architecture│   ├── comet_navigator.py    # Comet navigator implementation

pip install -r requirements.txt

```│   └── factory.py            # NavigatorFactory with NavigatorType enum



### Basic Usage### Component Responsibilities├── pipeline/                 # Browser-specific workflow pipelines (NEW!)



```python│   ├── __init__.py           # Public API exports

from browser.comet import CometBrowser

from pipeline import PipelineConfig| Component | Purpose | Location |│   ├── base.py               # Abstract BasePipeline class



# Create browser facade|-----------|---------|----------|│   ├── comet_pipeline.py     # Comet workflow (Sidecar + Assistant)

browser = CometBrowser()

| **Browser** | High-level orchestrator - launches browser, creates components, manages lifecycle | `browser/comet/browser.py` |│   └── factory.py            # PipelineFactory with PipelineType enum

# Configure workflow

config = PipelineConfig(| **Launcher** | Start Comet executable, attach Selenium WebDriver | `browser/comet/launcher.py` |├── htmls/                    # HTML test files

    target_url="https://www.perplexity.ai/sidecar?copilot=true",

    keep_open=True  # Keep browser open after completion| **Navigator** | Page navigation, element interaction, send Sidecar queries | `browser/comet/navigator.py` |│   ├── test.html

)

| **Pipeline** | Complete workflow: navigate → execute → finalize | `browser/comet/pipeline.py` |│   ├── test2.html

# Run with query

result = browser.run_pipeline(│   └── test3.html

    config,

    query="What is Python?",### Design Pattern: Hybrid Facade + Pipeline├── archive/                  # Legacy automation code

    submit=False  # True to submit query, False to just type it

)│   └── comet_ui_automation.py # PyAutoGUI Assistant button clicking

```

```├── main.py                   # Entry point using pipeline architecture

### Main Entry Point

┌─────────────────────────────────────────────────────────┐├── pipeline_old.py           # Old single pipeline (backup)

```powershell

python main.py│                   CometBrowser (Facade)                 │├── navigation.py             # Legacy navigation utilities

```

│  • Launches browser                                      │├── launch_comet.py           # Legacy Comet launcher

## 📋 Workflow

│  • Creates launcher, navigator, pipeline                │├── ARCHITECTURE.md           # Browser launcher architecture docs

Here's what happens when you run the pipeline:

│  • Manages lifecycle                                     │├── NAVIGATOR_ARCHITECTURE.md # Navigator architecture docs

```

1. browser.run_pipeline(config, query="...")└─────────────────────────────────────────────────────────┘├── PIPELINE_ARCHITECTURE.md  # Pipeline architecture docs (NEW!)

   ↓

2. Launch Comet browser                          │└── requirements.txt          # Python dependencies

   • Start Comet.exe with --remote-debugging-port

   • Attach Selenium WebDriver                          ↓```

   • Returns driver instance

   ↓              ┌───────────────────────┐

3. Create navigator with driver

   ↓              │  CometPipeline        │## Architecture

4. Create pipeline with (driver, navigator, config, **kwargs)

   ↓              │  • Navigation         │

5. pipeline.run()

   ├─→ pre_workflow_steps()              │  • Workflow execution │This project follows a **consistent 3-layer modular architecture**:

   │   └─→ Navigate to Sidecar URL

   │              │  • Business logic     │

   ├─→ execute_workflow()

   │   └─→ Send query to Sidecar              └───────────────────────┘### 1. Browser Launcher Layer

   │

   └─→ post_workflow_steps()```- **Purpose**: Launch and attach to different browsers

       └─→ Wait for response

   ↓- **Pattern**: Abstract base class + Factory

6. Return result

```**Why this architecture?**- **Files**: `browser_launcher/`



## 🎓 Key Design Decisions- **Extensible**: Add new browsers by implementing `BrowserLauncher`



### 1. Package-Based Organization- ✅ **Separation of Concerns**: Infrastructure (Browser) vs. Logic (Pipeline)



All browser-specific code lives in `browser/<browser_name>/`:- ✅ **Timing Control**: Pipeline handles navigation after browser setup (critical for Comet's saved sessions)### 2. Navigator Layer



```python- ✅ **Package Isolation**: All Comet code in one place (`browser/comet/`)- **Purpose**: Navigate and interact with pages

# ✅ GOOD: Import from package

from browser.comet import CometBrowser, CometNavigator, CometPipeline- ✅ **Easy Extension**: Add new browsers by creating `browser/<name>/` packages- **Pattern**: Abstract base class + Factory



# ❌ BAD: Scattered across folders- **Files**: `navigator/`

from browser_launcher.comet_launcher import CometBrowserLauncher

from navigator.comet_navigator import CometNavigator## 🚀 Quick Start- **Extensible**: Add browser-specific navigation by implementing `Navigator`

from pipeline.comet_pipeline import CometPipeline

```



### 2. Navigation Responsibility### Installation### 3. Pipeline Layer (NEW!)



**Pipeline handles navigation**, not Browser facade.- **Purpose**: Complete automation workflows with browser-specific steps



**Why?** Comet uses `user_data_dir=Path("./comet_profile_tmp")` for session persistence. Navigating too early (in Browser facade) causes Selenium session crashes. Pipeline navigation happens **after** browser setup completes, avoiding conflicts.```powershell- **Pattern**: Template Method + Factory



```python# Create virtual environment- **Files**: `pipeline/`

# browser/base.py (Browser Facade)

def run_pipeline(self, config, **kwargs):uv venv --python 3.12- **Extensible**: Add browser workflows by implementing `BasePipeline`

    # Step 1: Launch and setup

    if not self._is_launched:.\.venv\Scripts\Activate.ps1

        self.launch()  # → driver ready

    **Why this architecture?**

    # Step 2: Create pipeline and let it handle navigation

    self._pipeline = self.create_pipeline(...)# Install dependencies- ✅ **Separation of Concerns**: Each layer has one responsibility

    return self._pipeline.run()  # Pipeline navigates here

pip install -r requirements.txt- ✅ **Open/Closed Principle**: Add new browsers without modifying existing code

# browser/comet/pipeline.py (Pipeline)

def pre_workflow_steps(self) -> bool:```- ✅ **Testability**: Each component can be tested independently

    # Navigate AFTER browser is fully initialized

    SIDECAR_URL = "https://www.perplexity.ai/sidecar?copilot=true"- ✅ **Consistency**: All three modules follow identical extension patterns

    return self.navigator.navigate_to_url(SIDECAR_URL, wait_time=3)

```### Basic Usage



### 3. Composition Over InheritanceSee detailed docs:



Components are **composed at runtime**, not inherited:```python- [Browser Launcher Architecture](ARCHITECTURE.md)



```pythonfrom browser.comet import CometBrowser- [Navigator Architecture](NAVIGATOR_ARCHITECTURE.md)

class CometBrowser(BaseBrowser):

    def create_launcher(self):from pipeline import PipelineConfig- [Pipeline Architecture](PIPELINE_ARCHITECTURE.md) ← **NEW!**

        return CometBrowserLauncher(self.config)

    

    def create_navigator(self, driver):

        return CometNavigator(driver)# Create browser facade## Usage

    

    def create_pipeline(self, driver, navigator, config, **kwargs):browser = CometBrowser()

        return CometPipeline(driver, navigator, config, **kwargs)

```### Option 1: Using Pipeline (Recommended for Complete Workflows)



## ⚙️ Configuration# Configure workflow



Edit `main.py` to customize:config = PipelineConfig(The pipeline handles the complete workflow including browser-specific initialization:



```python    target_url="https://www.perplexity.ai/sidecar?copilot=true",

# Target URL

SIDECAR_URL = "https://www.perplexity.ai/sidecar?copilot=true"    keep_open=True  # Keep browser open after completion```python



# Query to send)from pipeline import PipelineFactory, PipelineType, PipelineConfig

QUERY = "What is Python?"

from browser_launcher import BrowserFactory, BrowserType

# Submit query or just type it

SUBMIT_QUERY = False  # False = type but don't submit# Run with queryfrom navigator import NavigatorFactory, NavigatorType



# Keep browser open after completionresult = browser.run_pipeline(

config = PipelineConfig(

    target_url=SIDECAR_URL,    config,# Create dependencies

    keep_open=True

)    query="What is Python?",browser_launcher = BrowserFactory.create(BrowserType.COMET)

```

    submit=False  # True to submit query, False to just type itnavigator_factory = lambda driver: NavigatorFactory.create(NavigatorType.COMET, driver)

## 🔧 Adding a New Browser

)

The architecture makes adding new browsers straightforward:

```# Configure workflow

### 1. Create Package Structure

config = PipelineConfig(

```

browser/### Main Entry Point    target_url="https://example.com",

└── mybrowser/

    ├── __init__.py       # Export classes    load_wait_time=5,

    ├── browser.py        # MyBrowser(BaseBrowser)

    ├── launcher.py       # MyBrowserLauncher```powershell    keep_open=True

    ├── navigator.py      # MyNavigator

    └── pipeline.py       # MyPipelinepython main_browser_abstraction.py)

```

```

### 2. Implement Components

# Run pipeline (opens Sidecar, navigates, activates Assistant)

```python

# browser/mybrowser/launcher.py## 📋 Workflowpipeline = PipelineFactory.create(

from browser_launcher.base import BrowserLauncher

    PipelineType.COMET,

class MyBrowserLauncher(BrowserLauncher):

    def get_launch_args(self) -> List[str]:Here's what happens when you run the pipeline:    browser_launcher=browser_launcher,

        return ["--my-flag", "--another-flag"]

        navigator_factory=navigator_factory,

    def attach_selenium(self):

        # Attach to your browser```    config=config

        pass

1. browser.run_pipeline(config, query="..."))

# browser/mybrowser/navigator.py

from navigator.base import Navigator   ↓



class MyNavigator(Navigator):2. Launch Comet browserresult = pipeline.run()

    def navigate_to_url(self, url: str, wait_time: int = 2) -> bool:

        # Browser-specific navigation   • Start Comet.exe with --remote-debugging-port```

        pass

   • Attach Selenium WebDriver

# browser/mybrowser/pipeline.py

from pipeline.base import BasePipeline   • Returns driver instance**Comet Pipeline automatically:**



class MyPipeline(BasePipeline):   ↓1. Launches Comet browser

    def pre_workflow_steps(self) -> bool:

        # Navigate to your target3. Create navigator with driver2. Opens Perplexity Sidecar (https://www.perplexity.ai/sidecar?copilot=true)

        pass

       ↓3. Navigates to your target URL

    def execute_workflow(self) -> bool:

        # Your business logic4. Create pipeline with (driver, navigator, config, **kwargs)4. Activates the Assistant button

        pass

       ↓5. Handles cleanup

    def post_workflow_steps(self) -> bool:

        # Cleanup/finalization5. pipeline.run()

        pass

   ├─→ pre_workflow_steps()### Option 2: Using Individual Components

# browser/mybrowser/browser.py

from browser.base import BaseBrowser   │   └─→ Navigate to Sidecar URL



class MyBrowser(BaseBrowser):   │For more control, use the modular components directly:

    def create_launcher(self):

        return MyBrowserLauncher(self.config)   ├─→ execute_workflow()

    

    def create_navigator(self, driver):   │   └─→ Send query to Sidecar```python

        return MyNavigator(driver)

       │from browser_launcher import launch_browser, BrowserType

    def create_pipeline(self, driver, navigator, config, **kwargs):

        return MyPipeline(driver, navigator, config, **kwargs)   └─→ post_workflow_steps()from navigator import NavigatorFactory, NavigatorType

```

       └─→ Wait for response

### 3. Export in Package

   ↓# Launch browser

```python

# browser/mybrowser/__init__.py6. Return resultdriver = launch_browser(browser_type=BrowserType.COMET)

from .browser import MyBrowser

from .launcher import MyBrowserLauncher```

from .navigator import MyNavigator

from .pipeline import MyPipeline# Create navigator



__all__ = ["MyBrowser", "MyBrowserLauncher", "MyNavigator", "MyPipeline"]## 🎓 Key Design Decisionsnavigator = NavigatorFactory.create(NavigatorType.COMET, driver)

```



### 4. Register in Factory

### 1. Package-Based Organization# Navigate

```python

# browser/factory.pyresult = navigator.navigate_to_url("https://example.com")

from enum import Enum

All browser-specific code lives in `browser/<browser_name>/`:

class BrowserType(Enum):

    COMET = "comet"# Clean up

    MYBROWSER = "mybrowser"  # Add your browser

```pythondriver.quit()

_BROWSER_CLASSES = {

    BrowserType.COMET: lambda: __import__("browser.comet").comet.CometBrowser,# ✅ GOOD: Import from package```

    BrowserType.MYBROWSER: lambda: __import__("browser.mybrowser").mybrowser.MyBrowser,

}from browser.comet import CometBrowser, CometNavigator, CometPipeline

```

### Option 3: Factory Pattern for Custom Configuration

### 5. Use It

# ❌ BAD: Scattered across folders

```python

from browser.factory import BrowserFactory, BrowserTypefrom browser_launcher.comet_launcher import CometBrowserLauncher```python



browser = BrowserFactory.create(BrowserType.MYBROWSER)from navigator.comet_navigator import CometNavigatorfrom browser_launcher import BrowserFactory, BrowserType, BrowserConfig

result = browser.run_pipeline(config, query="test")

```from pipeline.comet_pipeline import CometPipelinefrom pathlib import Path



## 🔍 Troubleshooting```



### Navigation Not Working# Create custom configuration



**Symptom**: Browser launches but doesn't navigate to Sidecar URL### 2. Navigation Responsibilityconfig = BrowserConfig(



**Solution**: Ensure navigation happens in `Pipeline.pre_workflow_steps()`, not in `Browser.run_pipeline()`. This timing is critical for browsers with saved sessions.    executable_path=Path("C:/path/to/comet.exe"),



### Selenium Session Crashes**Pipeline handles navigation**, not Browser facade.    debug_port=9222,



**Symptom**: "invalid session id" errors after launch    start_maximized=True,



**Causes**:**Why?** Comet uses `user_data_dir=Path("./comet_profile_tmp")` for session persistence. Navigating too early (in Browser facade) causes Selenium session crashes. Pipeline navigation happens **after** browser setup completes, avoiding conflicts.    allow_file_access=True,

- Navigating before browser fully initialized

- Multiple windows causing driver confusion    disable_web_security=True,

- Saved user data directory conflicts

```python    user_data_dir=Path("./comet_profile")

**Solution**: Let Pipeline handle navigation, add explicit waits:

```python# browser/base.py (Browser Facade))

from selenium.webdriver.support.ui import WebDriverWait

from selenium.webdriver.support import expected_conditions as ECdef run_pipeline(self, config, **kwargs):



element = WebDriverWait(driver, 10).until(    # Step 1: Launch and setup# Create launcher

    EC.visibility_of_element_located((By.ID, "my-element"))

)    if not self._is_launched:launcher = BrowserFactory.create(BrowserType.COMET, config)

```

        self.launch()  # → driver ready

### Element Not Found

    # Launch and attach

**Symptom**: Can't find input field or button after navigation

    # Step 2: Create pipeline and let it handle navigationdriver = launcher.launch_and_attach(kill_existing=True)

**Solution**: Use explicit waits, not `time.sleep()`:

```python    self._pipeline = self.create_pipeline(...)

# ❌ BAD

time.sleep(3)    return self._pipeline.run()  # Pipeline navigates here# Use the driver

element = driver.find_element(By.ID, "ask-input")

driver.get("file:///C:/path/to/test.html")

# ✅ GOOD

from selenium.webdriver.support.ui import WebDriverWait# browser/comet/pipeline.py (Pipeline)

from selenium.webdriver.support import expected_conditions as EC

def pre_workflow_steps(self) -> bool:# Clean up

element = WebDriverWait(driver, 10).until(

    EC.presence_of_element_located((By.ID, "ask-input"))    # Navigate AFTER browser is fully initializedlauncher.quit()

)

```    SIDECAR_URL = "https://www.perplexity.ai/sidecar?copilot=true"```



## 📚 API Reference    return self.navigator.navigate_to_url(SIDECAR_URL, wait_time=3)



### CometBrowser```### Context Manager Support



**Methods:**

- `run_pipeline(config, **kwargs)` - Run complete workflow

- `launch()` - Launch Comet and attach Selenium### 3. Composition Over Inheritance```python

- `quit()` - Close browser and cleanup

from browser_launcher import BrowserFactory, BrowserType

### CometNavigator

Components are **composed at runtime**, not inherited:

**Methods:**

- `navigate_to_url(url, wait_time=2)` - Navigate to URL with waitwith BrowserFactory.create(BrowserType.COMET) as driver:

- `send_query_to_sidecar(query, submit=False)` - Type/submit query to Sidecar input

```python    driver.get("https://example.com")

### CometPipeline

class CometBrowser(BaseBrowser):    print(driver.title)

**Methods:**

- `run()` - Execute complete pipeline    def create_launcher(self):# Automatically cleaned up

- `pre_workflow_steps()` - Navigation phase

- `execute_workflow()` - Business logic phase        return CometBrowserLauncher(self.config)```

- `post_workflow_steps()` - Finalization phase

    

### PipelineConfig

    def create_navigator(self, driver):### Opening Multiple HTML Files

**Attributes:**

- `target_url: str` - URL to navigate to        return CometNavigator(driver)

- `keep_open: bool` - Keep browser open after completion

- `load_wait_time: int` - Wait time after navigation    ```python



## 🧪 Testing    def create_pipeline(self, driver, navigator, config, **kwargs):from browser_launcher import launch_browser



Run the main script:        return CometPipeline(driver, navigator, config, **kwargs)from pathlib import Path



```powershell```import navigation

python main.py

```



Expected behavior:## ⚙️ Configurationdriver = launch_browser()

1. Comet browser launches

2. Navigates to Sidecar URL

3. Types query into input field

4. Waits (doesn't submit if `SUBMIT_QUERY=False`)Edit `main_browser_abstraction.py` to customize:# Open all HTML files in the htmls folder

5. Browser stays open if `keep_open=True`

html_dir = Path("htmls")

## 📦 Requirements

```pythonurls = navigation.open_local_html_files(

- Python 3.12+

- Selenium WebDriver 4.x# Target URL    driver, 

- Perplexity Comet browser installed

- ChromeDriver (auto-managed)SIDECAR_URL = "https://www.perplexity.ai/sidecar?copilot=true"    html_dir, 



## 📄 License    pattern="*.html",



MIT License# Query to send    new_tabs=True,



## 🤝 ContributingQUERY = "What is Python?"    wait_per_page=0.5



Contributions welcome! When adding features:)



1. Follow the package-based structure (`browser/<name>/`)# Submit query or just type it

2. Keep components focused (one responsibility per class)

3. Use explicit waits, not `time.sleep()`SUBMIT_QUERY = False  # False = type but don't submitprint(f"Opened {len(urls)} HTML files")

4. Document architectural decisions

5. Test with Comet browser before submitting```



## 🔗 Resources# Keep browser open after completion



- [Selenium WebDriver Documentation](https://www.selenium.dev/documentation/webdriver/)config = PipelineConfig(## Extending for New Browsers

- [Python Type Hints](https://docs.python.org/3/library/typing.html)

- [Perplexity Sidecar](https://www.perplexity.ai/sidecar)    target_url=SIDECAR_URL,


    keep_open=TrueThe architecture is designed to make adding new browsers easy:

)

```### 1. Add Browser Type to Enum



## 🔧 Adding a New Browser```python

# browser_launcher/factory.py

The architecture makes adding new browsers straightforward:class BrowserType(Enum):

    COMET = "comet"

### 1. Create Package Structure    CHROME = "chrome"  # Add new type here

```

```

browser/### 2. Create Launcher Class

└── mybrowser/

    ├── __init__.py       # Export classes```python

    ├── browser.py        # MyBrowser(BaseBrowser)# browser_launcher/chrome_launcher.py

    ├── launcher.py       # MyBrowserLauncherfrom .base import BrowserLauncher, BrowserConfig

    ├── navigator.py      # MyNavigator

    └── pipeline.py       # MyPipelineclass ChromeBrowserLauncher(BrowserLauncher):

```    def get_launch_args(self) -> List[str]:

        # Return Chrome-specific arguments

### 2. Implement Components        return [...]

    

```python    def get_process_names(self) -> List[str]:

# browser/mybrowser/launcher.py        return ["chrome", "chrome.exe"]

from browser_launcher.base import BrowserLauncher    

    def attach_selenium(self):

class MyBrowserLauncher(BrowserLauncher):        # Implement Selenium attachment

    def get_launch_args(self) -> List[str]:        pass

        return ["--my-flag", "--another-flag"]```

    

    def attach_selenium(self):### 3. Register in Factory

        # Attach to your browser

        pass```python

# browser_launcher/factory.py

# browser/mybrowser/navigator.py_BROWSER_CLASSES = {

from navigator.base import Navigator    BrowserType.COMET: CometBrowserLauncher,

    BrowserType.CHROME: ChromeBrowserLauncher,  # Register here

class MyNavigator(Navigator):}

    def navigate_to_url(self, url: str, wait_time: int = 2) -> bool:```

        # Browser-specific navigation

        passThat's it! The new browser is now available:



# browser/mybrowser/pipeline.py```python

from pipeline.base import BasePipelinedriver = launch_browser(BrowserType.CHROME)

```

class MyPipeline(BasePipeline):

    def pre_workflow_steps(self) -> bool:## API Reference

        # Navigate to your target

        pass### BrowserConfig

    

    def execute_workflow(self) -> bool:Configuration dataclass for browser launchers.

        # Your business logic

        pass**Attributes:**

    - `executable_path: Path` - Path to browser executable

    def post_workflow_steps(self) -> bool:- `debug_port: int` - Chrome DevTools debugging port (default: 9222)

        # Cleanup/finalization- `start_maximized: bool` - Start browser maximized (default: True)

        pass- `allow_file_access: bool` - Allow file:// URLs (default: True)

- `disable_web_security: bool` - Disable web security (default: False)

# browser/mybrowser/browser.py- `user_data_dir: Optional[Path]` - Custom user data directory

from browser.base import BaseBrowser- `extra_args: List[str]` - Additional command-line arguments

- `timeout: float` - DevTools connection timeout (default: 12.0)

class MyBrowser(BaseBrowser):

    def create_launcher(self):### BrowserLauncher (Abstract Base Class)

        return MyBrowserLauncher(self.config)

    **Methods:**

    def create_navigator(self, driver):- `launch_and_attach(kill_existing=True)` - Complete workflow to launch browser and attach Selenium

        return MyNavigator(driver)- `launch_browser(try_alternate_format=False)` - Launch the browser process

    - `wait_for_devtools()` - Wait for DevTools endpoint to be ready

    def create_pipeline(self, driver, navigator, config, **kwargs):- `attach_selenium()` - Attach Selenium WebDriver (abstract, must implement)

        return MyPipeline(driver, navigator, config, **kwargs)- `kill_existing_processes()` - Kill any running browser instances

```- `quit()` - Clean up resources



### 3. Export in Package### BrowserFactory



```python**Methods:**

# browser/mybrowser/__init__.py- `create(browser_type, config=None)` - Create a browser launcher instance

from .browser import MyBrowser- `register_browser(browser_type, launcher_class)` - Register new browser type

from .launcher import MyBrowserLauncher- `get_supported_browsers()` - Get list of supported browsers

from .navigator import MyNavigator

from .pipeline import MyPipeline### Convenience Functions



__all__ = ["MyBrowser", "MyBrowserLauncher", "MyNavigator", "MyPipeline"]- `launch_browser(browser_type=BrowserType.COMET, config=None, kill_existing=True)` - Quick launch shortcut

```

## Troubleshooting

### 4. Register in Factory

### "No module named 'requests'"

```python

# browser/factory.pyInstall dependencies in your virtual environment:

from enum import Enum```powershell

python -m pip install -r requirements.txt

class BrowserType(Enum):```

    COMET = "comet"

    MYBROWSER = "mybrowser"  # Add your browser### "ChromeDriver version mismatch"



_BROWSER_CLASSES = {The Comet launcher automatically detects browser version and downloads matching ChromeDriver. If issues persist:

    BrowserType.COMET: lambda: __import__("browser.comet").comet.CometBrowser,1. Delete cached ChromeDriver folders

    BrowserType.MYBROWSER: lambda: __import__("browser.mybrowser").mybrowser.MyBrowser,2. Run again - it will download fresh

}

```### "DevTools not reachable"



### 5. Use It- Ensure no other Comet instances are running

- Try increasing timeout in BrowserConfig

```python- Check if Comet supports `--remote-debugging-port` flag

from browser.factory import BrowserFactory, BrowserType

## License

browser = BrowserFactory.create(BrowserType.MYBROWSER)

result = browser.run_pipeline(config, query="test")MIT

```

## Contributing

## 🔍 Troubleshooting

When adding new browser support:

### Navigation Not Working1. Inherit from `BrowserLauncher`

2. Implement all abstract methods

**Symptom**: Browser launches but doesn't navigate to Sidecar URL3. Add to `BrowserType` enum

4. Register in `BrowserFactory`

**Solution**: Ensure navigation happens in `Pipeline.pre_workflow_steps()`, not in `Browser.run_pipeline()`. This timing is critical for browsers with saved sessions.5. Add tests

6. Update this README

### Selenium Session Crashes

**Symptom**: "invalid session id" errors after launch

**Causes**:
- Navigating before browser fully initialized
- Multiple windows causing driver confusion
- Saved user data directory conflicts

**Solution**: Let Pipeline handle navigation, add explicit waits:
```python
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

element = WebDriverWait(driver, 10).until(
    EC.visibility_of_element_located((By.ID, "my-element"))
)
```

### Element Not Found

**Symptom**: Can't find input field or button after navigation

**Solution**: Use explicit waits, not `time.sleep()`:
```python
# ❌ BAD
time.sleep(3)
element = driver.find_element(By.ID, "ask-input")

# ✅ GOOD
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

element = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.ID, "ask-input"))
)
```

## 📚 API Reference

### CometBrowser

**Methods:**
- `run_pipeline(config, **kwargs)` - Run complete workflow
- `launch()` - Launch Comet and attach Selenium
- `quit()` - Close browser and cleanup

### CometNavigator

**Methods:**
- `navigate_to_url(url, wait_time=2)` - Navigate to URL with wait
- `send_query_to_sidecar(query, submit=False)` - Type/submit query to Sidecar input

### CometPipeline

**Methods:**
- `run()` - Execute complete pipeline
- `pre_workflow_steps()` - Navigation phase
- `execute_workflow()` - Business logic phase
- `post_workflow_steps()` - Finalization phase

### PipelineConfig

**Attributes:**
- `target_url: str` - URL to navigate to
- `keep_open: bool` - Keep browser open after completion
- `load_wait_time: int` - Wait time after navigation

## 🧪 Testing

Run the test script:

```powershell
python main_browser_abstraction.py
```

Expected behavior:
1. Comet browser launches
2. Navigates to Sidecar URL
3. Types query into input field
4. Waits (doesn't submit if `SUBMIT_QUERY=False`)
5. Browser stays open if `keep_open=True`

## 📦 Requirements

- Python 3.12+
- Selenium WebDriver 4.x
- Perplexity Comet browser installed
- ChromeDriver (auto-managed)

## 📄 License

MIT License

## 🤝 Contributing

Contributions welcome! When adding features:

1. Follow the package-based structure (`browser/<name>/`)
2. Keep components focused (one responsibility per class)
3. Use explicit waits, not `time.sleep()`
4. Document architectural decisions
5. Test with Comet browser before submitting

## 🔗 Resources

- [Selenium WebDriver Documentation](https://www.selenium.dev/documentation/webdriver/)
- [Python Type Hints](https://docs.python.org/3/library/typing.html)
- [Perplexity Sidecar](https://www.perplexity.ai/sidecar)
