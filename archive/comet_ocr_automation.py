import pyautogui
import pytesseract
from PIL import Image, ImageEnhance, ImageFilter
import time
import subprocess
from datetime import datetime

class CometOCRAutomation:
    def __init__(self, binary_path):
        self.binary_path = binary_path
        # You'll need to download Tesseract: https://github.com/tesseract-ocr/tesseract
        # And set the path here:
        pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        
        # Your calibrated coordinates
        self.assistant_x = -138
        self.assistant_y = 61
        self.chat_input_x = -356
        self.chat_input_y = 984
        self.response_area_x = -368
        self.response_area_y = 632
    
    def launch_comet(self):
        """Launch Comet browser"""
        try:
            print(f"[info] Launching Comet browser...")
            self.process = subprocess.Popen([self.binary_path])
            time.sleep(5)
            return True
        except Exception as e:
            print(f"[error] Failed to launch: {e}")
            return False
    
    def click_assistant(self):
        """Click the Assistant button"""
        try:
            pyautogui.click(self.assistant_x, self.assistant_y)
            time.sleep(2)
            return True
        except Exception as e:
            print(f"[error] Failed to click assistant: {e}")
            return False
    
    def send_message(self, message):
        """Send message to assistant"""
        try:
            pyautogui.click(self.chat_input_x, self.chat_input_y)
            time.sleep(0.5)
            pyautogui.hotkey('ctrl', 'a')
            pyautogui.typewrite(message, interval=0.02)
            pyautogui.press('enter')
            return True
        except Exception as e:
            print(f"[error] Failed to send message: {e}")
            return False
    
    def capture_response_with_ocr(self, wait_time=10):
        """Capture response using OCR (Optical Character Recognition)"""
        try:
            print(f"[info] Waiting {wait_time} seconds for AI response...")
            time.sleep(wait_time)
            
            # Take screenshot of response area
            left = self.response_area_x - 500
            top = self.response_area_y - 200
            width = 1200
            height = 800
            
            print(f"[info] Taking screenshot for OCR...")
            screenshot = pyautogui.screenshot(region=(left, top, width, height))
            
            # Enhance image for better OCR
            # Convert to grayscale
            gray_img = screenshot.convert('L')
            
            # Enhance contrast
            enhancer = ImageEnhance.Contrast(gray_img)
            enhanced_img = enhancer.enhance(2.0)
            
            # Apply slight blur to smooth text
            smooth_img = enhanced_img.filter(ImageFilter.MedianFilter())
            
            # Use OCR to extract text
            print(f"[info] Running OCR to extract text...")
            
            # Try different OCR configurations
            configs = [
                '--psm 6',  # Uniform block of text
                '--psm 4',  # Single column of text
                '--psm 3',  # Fully automatic page segmentation
            ]
            
            best_text = ""
            for config in configs:
                try:
                    text = pytesseract.image_to_string(smooth_img, config=config)
                    if len(text) > len(best_text):
                        best_text = text
                except:
                    continue
            
            # Clean up the text
            lines = best_text.split('\n')
            cleaned_lines = []
            
            for line in lines:
                line = line.strip()
                if line and not any(skip in line.lower() for skip in [
                    'comet', 'browser', 'tab', 'window', 'chrome'
                ]):
                    cleaned_lines.append(line)
            
            result = '\n'.join(cleaned_lines)
            
            if result:
                print(f"[success] OCR extracted {len(result)} characters")
                return result
            else:
                print("[warning] No text extracted by OCR")
                return "No text could be extracted from the response area"
                
        except Exception as e:
            print(f"[error] OCR extraction failed: {e}")
            return f"OCR Error: {e}"
    
    def save_response_to_file(self, response_text, filename=None):
        """Save response to text file"""
        try:
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"comet_response_ocr_{timestamp}.txt"
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(f"Comet Assistant Response (OCR)\n")
                f.write(f"Captured: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("="*50 + "\n\n")
                f.write(response_text)
            
            print(f"[success] Response saved to: {filename}")
            return filename
        except Exception as e:
            print(f"[error] Failed to save: {e}")
            return False

# Test function
def test_ocr_automation():
    binary_path = "C:\\Users\\sheerg\\AppData\\Local\\Perplexity\\Comet\\Application\\comet.exe"
    automation = CometOCRAutomation(binary_path)
    
    print("=== COMET OCR AUTOMATION TEST ===")
    
    # Launch and setup
    if not automation.launch_comet():
        return
    
    automation.click_assistant()
    
    # Send test message
    test_message = "What are the main benefits of renewable energy?"
    automation.send_message(test_message)
    
    # Capture response with OCR
    response = automation.capture_response_with_ocr(wait_time=15)
    print(f"\nCaptured Response:\n{response}")
    
    # Save to file
    automation.save_response_to_file(response)

if __name__ == "__main__":
    test_ocr_automation()
