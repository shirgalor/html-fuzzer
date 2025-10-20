# launch_and_attach_comet.py
# pip install requests psutil selenium webdriver-manager chromedriver-autoinstaller
# (chromedriver packages only needed if you want the Selenium attach step)

import subprocess
import time
import requests
from pathlib import Path
import sys

# optional: used to kill existing comet processes so flags take effect
try:
    import psutil
except Exception:
    psutil = None

# Optional Selenium attach section - set to True to attempt attaching after launch
DO_ATTACH = True

# EDIT THIS: path to your Comet exe
COMET_EXE = Path(r"C:\Users\sheerg\AppData\Local\Perplexity\Comet\Application\comet.exe")
DEBUG_PORT = 9222
DEVTOOLS_URL = f"http://127.0.0.1:{DEBUG_PORT}/json/version"

def kill_comet_processes():
    if psutil is None:
        return
    for p in psutil.process_iter(["pid", "name", "exe", "cmdline"]):
        try:
            name = (p.info.get("name") or "").lower()
            exe = (p.info.get("exe") or "") or ""
            cmd = " ".join(p.info.get("cmdline") or [])
            if "comet" in name or "perplexity" in name or "comet.exe" in exe.lower() or "perplexity" in cmd.lower():
                print(f"[+] Killing existing process pid={p.pid} ({name})")
                p.kill()
        except Exception:
            pass

def launch_comet(exe_path: Path, port: int, try_double_dash: bool = False):
    if not exe_path.exists():
        raise FileNotFoundError(f"Comet executable not found: {exe_path}")
    # Launch from exe folder as working dir (some apps require this)
    cwd = str(exe_path.parent)
    
    # Add fullscreen/maximized arguments
    args = [
        str(exe_path),
        f"--remote-debugging-port={port}",
        "--start-maximized",
        # Allow local file access and mixed content to simplify local testing
        "--allow-file-access-from-files",
        "--allow-file-access",
        "--disable-web-security",
        "--user-data-dir=./comet_profile_tmp"
    ]
    if try_double_dash:
        # some apps require a literal "--" before flags
        args = [str(exe_path), "--", f"--remote-debugging-port={port}", "--start-maximized"]

    print("[*] Launching Comet in fullscreen:", " ".join(args))
    # start detached so this script can continue; do not use shell=True
    proc = subprocess.Popen(args, cwd=cwd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return proc

def wait_for_devtools(url: str, timeout: float = 12.0):
    deadline = time.time() + timeout
    last_exc = None
    while time.time() < deadline:
        try:
            r = requests.get(url, timeout=0.5)
            if r.ok:
                return r.json()
        except Exception as e:
            last_exc = e
        time.sleep(0.25)
    raise RuntimeError(f"DevTools not reachable at {url}. Last error: {last_exc}")

def attach_with_selenium(port: int):
    # This block is optional; it requires selenium and a chromedriver installer
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.chrome.service import Service
    except Exception as e:
        print("[!] Selenium not installed:", e)
        return None

    # Try to get/install chromedriver automatically
    driver_path = None
    try:
        import chromedriver_autoinstaller as cda
        # Attempt to detect the remote browser version (Comet/Chrome) and request a matching driver
        try:
            import re
            ver = None
            try:
                r = requests.get(f"http://127.0.0.1:{port}/json/version", timeout=1)
                if r.ok:
                    ver = r.json()
            except Exception:
                ver = None

            chrome_major = None
            if ver:
                browser_str = ver.get("Browser", "") or ""
                m = re.search(r"/(\d+)\.", browser_str)
                if m:
                    chrome_major = m.group(1)

            if chrome_major:
                print(f"[*] Detected remote browser major version: {chrome_major}")
                try:
                    # chromedriver_autoinstaller accepts a version string; pass major to find a matching driver
                    driver_path = cda.install(chrome_major)
                    # Verify the installed driver version matches what we need
                    if driver_path and "141" in driver_path and chrome_major == "140":
                        print(f"[!] chromedriver_autoinstaller returned version 141 for requested {chrome_major}")
                        driver_path = None  # Force fallback to webdriver_manager
                except Exception:
                    # best-effort fallback to generic install()
                    driver_path = cda.install()
            else:
                driver_path = cda.install()

        except Exception as e:
            print("[!] chromedriver_autoinstaller detection/install failed:", e)
            driver_path = None
        if driver_path:
            print("[*] chromedriver_autoinstaller provided:", driver_path)
    except Exception as e:
        print("[!] chromedriver_autoinstaller not available or failed:", e)
    
    # Enhanced webdriver_manager fallback with manual ChromeDriver download
    if driver_path is None:
        try:
            # Get browser version info
            chrome_major = None
            chrome_full_version = None
            try:
                r = requests.get(f"http://127.0.0.1:{port}/json/version", timeout=1)
                if r.ok:
                    ver = r.json()
                    browser_str = ver.get("Browser", "") or ""
                    import re
                    # Extract full version like "140.1.7339.21965"
                    m = re.search(r"/(\d+\.\d+\.\d+\.\d+)", browser_str)
                    if m:
                        chrome_full_version = m.group(1)
                        chrome_major = chrome_full_version.split('.')[0]
            except Exception:
                pass
                
            if chrome_major and chrome_full_version:
                print(f"[*] Trying to download ChromeDriver for Chrome {chrome_full_version}")
                try:
                    # Try to manually download the right ChromeDriver version
                    import os
                    from urllib.request import urlretrieve
                    import zipfile
                    
                    # ChromeDriver version mapping - for Chrome 140, we need ChromeDriver 140.x
                    chromedriver_version = None
                    
                    # Try to find the exact ChromeDriver version for this Chrome version
                    # Chrome 140.x uses ChromeDriver 140.x
                    try:
                        # Get the ChromeDriver releases list
                        releases_url = "https://googlechromelabs.github.io/chrome-for-testing/known-good-versions-with-downloads.json"
                        releases_resp = requests.get(releases_url, timeout=5)
                        if releases_resp.ok:
                            releases_data = releases_resp.json()
                            # Look for a ChromeDriver version that matches our Chrome major version
                            for version_info in releases_data.get("versions", []):
                                version = version_info.get("version", "")
                                if version.startswith(f"{chrome_major}.") and "downloads" in version_info:
                                    downloads = version_info["downloads"]
                                    if "chromedriver" in downloads:
                                        for platform_info in downloads["chromedriver"]:
                                            if platform_info.get("platform") == "win64":
                                                chromedriver_version = version
                                                download_url = platform_info.get("url")
                                                break
                                        if chromedriver_version:
                                            break
                    except Exception as e:
                        print(f"[!] Could not fetch ChromeDriver releases: {e}")
                    
                    if chromedriver_version and download_url:
                        print(f"[*] Found ChromeDriver {chromedriver_version} for Chrome {chrome_major}")
                        
                        # Download and extract
                        import tempfile
                        with tempfile.TemporaryDirectory() as temp_dir:
                            zip_path = os.path.join(temp_dir, "chromedriver.zip")
                            print(f"[*] Downloading ChromeDriver from: {download_url}")
                            urlretrieve(download_url, zip_path)
                            
                            # Extract to project directory
                            extract_dir = os.path.join(os.getcwd(), f"chromedriver_{chromedriver_version}")
                            os.makedirs(extract_dir, exist_ok=True)
                            
                            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                                zip_ref.extractall(extract_dir)
                            
                            # Find the chromedriver.exe in the extracted files
                            for root, dirs, files in os.walk(extract_dir):
                                if "chromedriver.exe" in files:
                                    driver_path = os.path.join(root, "chromedriver.exe")
                                    break
                        
                        if driver_path:
                            print(f"[*] Downloaded and extracted ChromeDriver to: {driver_path}")
                        else:
                            print("[!] ChromeDriver.exe not found in downloaded archive")
                    
                except Exception as e:
                    print(f"[!] Manual ChromeDriver download failed: {e}")
            
            # Final fallback to webdriver_manager without version constraint
            if driver_path is None:
                try:
                    from webdriver_manager.chrome import ChromeDriverManager
                    print("[*] Falling back to webdriver_manager (latest version)")
                    manager = ChromeDriverManager()
                    driver_path = manager.install()
                    print(f"[*] webdriver_manager installed driver at: {driver_path}")
                except Exception as e:
                    print(f"[!] webdriver_manager fallback failed: {e}")
                    
        except Exception as e:
            print("[!] Enhanced ChromeDriver download failed:", e)

    if driver_path is None:
        print("[!] No chromedriver available — skipping Selenium attach")
        return None

    opts = Options()
    opts.debugger_address = f"127.0.0.1:{port}"
    opts.add_argument("--remote-allow-origins=*")

    service = Service(driver_path)
    driver = webdriver.Chrome(service=service, options=opts)
    return driver

def main():
    try:
        kill_comet_processes()
    except Exception as e:
        print("[!] Could not kill processes (psutil missing?):", e)

    # Try normal launch first
    proc = launch_comet(COMET_EXE, DEBUG_PORT, try_double_dash=False)

    # wait for devtools
    try:
        ver = wait_for_devtools(DEVTOOLS_URL, timeout=12.0)
    except RuntimeError:
        # maybe this build expects the "--" form; try relaunch with it
        try:
            print("[*] Did not see DevTools — terminating and retrying with alternate flag form...")
            try:
                proc.kill()
            except Exception:
                pass
            proc = launch_comet(COMET_EXE, DEBUG_PORT, try_double_dash=True)
            ver = wait_for_devtools(DEVTOOLS_URL, timeout=12.0)
        except RuntimeError as e:
            print("[!] DevTools endpoint still not available:", e)
            print("=> If this happens, the Comet build may strip flags (Store app) or require launching from its folder.")
            sys.exit(1)

    print("[*] DevTools available. Browser string:", ver.get("Browser"))
    print("[*] webSocketDebuggerUrl:", ver.get("webSocketDebuggerUrl"))

    # ... inside main()

    # ... after wait_for_devtools(DEVTOOLS_URL, timeout=12.0) sets 'ver'
    
    print("[*] DevTools available. Browser string:", ver.get("Browser"))
    websocket_url = ver.get("webSocketDebuggerUrl")
    print("[*] webSocketDebuggerUrl:", websocket_url)
    
    # Do NOT try to attach Selenium in this script yet.
    # The browser-use agent will handle the web interaction.
    # Just return the URL needed for external connection.
    return websocket_url # <--- Return the WebSocket URL



if __name__ == "__main__":
    url = main()
    if url:
        print(f"Comet successfully launched and listening on: {url}")
