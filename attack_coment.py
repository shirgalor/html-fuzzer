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
    args = [str(exe_path), f"--remote-debugging-port={port}", "--start-maximized"]
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
        driver_path = cda.install()
        print("[*] chromedriver_autoinstaller provided:", driver_path)
    except Exception as e:
        print("[!] chromedriver_autoinstaller not available or failed:", e)
    if driver_path is None:
        try:
            from webdriver_manager.chrome import ChromeDriverManager
            driver_path = ChromeDriverManager().install()
            print("[*] webdriver_manager installed driver at:", driver_path)
        except Exception as e:
            print("[!] webdriver_manager failed:", e)

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

    if DO_ATTACH:
        print("[*] Attempting to attach Selenium to the running Comet...")
        driver = attach_with_selenium(DEBUG_PORT)
        if driver:
            print("[*] Selenium attached successfully!")
            return driver
        else:
            print("[!] Selenium attach skipped or failed.")
            return None
    else:
        print("[*] Launch completed; DevTools listening. Run your attach script now if you want.")
        return None

if __name__ == "__main__":
    main()
