import pytesseract
import pyautogui
import keyboard
import time
import json
import logging
import requests
from datetime import datetime
from PIL import ImageGrab, Image, ImageDraw, ImageTk
import os
import tkinter as tk
from tkinter import ttk, messagebox
import pyfiglet
from tabulate import tabulate

class DiscordMonitor:
    def __init__(self):
        self.load_config()
        self.running = False
        self.last_check = datetime.now()
        self.messages_detected = 0
        self.messages_sent = 0
        self.processed_messages = set()
        self.initial_scan = True
        self.start_time = None
        self.session_data = {
            "start_time": None,
            "end_time": None,
            "messages_detected": 0,
            "messages_sent": 0
        }
        self.has_responded = False

    def save_config(self):
        """Save the current configuration to the config file"""
        try:
            with open('monitor_config.json', 'w') as f:
                json.dump(self.config, f, indent=4)
            logging.info("Configuration saved successfully")
        except Exception as e:
            logging.error(f"Error saving configuration: {str(e)}")
            raise

    def load_config(self):
        try:
            with open('monitor_config.json', 'r') as f:
                loaded_config = json.load(f)
            valid_keys = {"keywords", "response", "scan_interval", "message_area", 
                         "username_area", "case_sensitive", "discord_token", "channel_id", 
                         "ocr_resolution", "ocr_config", "target_username"}
            if not all(key in loaded_config for key in valid_keys):
                logging.info("Old config format detected, creating fresh config")
                self.create_new_config()
            else:
                self.config = loaded_config
        except FileNotFoundError:
            logging.info("Config file not found, creating new config")
            self.create_new_config()
        except json.JSONDecodeError:
            logging.error("Invalid config file, creating new config")
            self.create_new_config()

    def create_new_config(self):
        self.config = {
            "keywords": "",
            "response": "",
            "scan_interval": 0.01,
            "message_area": {
                "top": 865,
                "left": 312,
                "width": 1365,
                "height": 177
            },
            "username_area": {
                "top": 865,
                "left": 100,
                "width": 200,
                "height": 30
            },
            "case_sensitive": False,
            "discord_token": "",
            "channel_id": "",
            "ocr_resolution": 1.0,
            "ocr_config": "--psm 4",
            "target_username": "",
            "session_history": []
        }
        self.save_config()
        logging.info("Created fresh config file")

    def send_discord_message(self, message):
        if not self.config.get("discord_token") or not self.config.get("channel_id"):
            logging.error("Token or channel ID not configured")
            return False
        
        headers = {
            "Authorization": self.config['discord_token'],
            "Content-Type": "application/json"
        }
        
        data = {
            "content": message
        }
        
        try:
            response = requests.post(
                f"https://discord.com/api/v10/channels/{self.config['channel_id']}/messages",
                headers=headers,
                json=data
            )
            response.raise_for_status()
            self.messages_sent += 1
            self.session_data["messages_sent"] += 1
            logging.info("Message sent successfully")
            return True
        except Exception as e:
            logging.error(f"Failed to send message: {str(e)}")
            return False

    def calibrate_message_area(self):
        print("\nCalibrating message area...")
        print("1. Move your mouse to the top-left corner of the message area")
        print("2. Press 'C' to capture the first point")
        print("3. Move your mouse to the bottom-right corner")
        print("4. Press 'C' again to capture the second point")
        print("\nPress Enter to start calibration (ESC to cancel)")
        
        input()
        
        start_pos = None
        end_pos = None
        captured_first = False
        
        while True:
            if keyboard.is_pressed('esc'):
                print("\nCalibration cancelled")
                return
                
            if keyboard.is_pressed('c'):
                if not captured_first:
                    start_pos = pyautogui.position()
                    print(f"Start position captured: {start_pos}")
                    captured_first = True
                    time.sleep(0.3)
                elif captured_first and not end_pos:
                    end_pos = pyautogui.position()
                    print(f"End position captured: {end_pos}")
                    
                    self.config["message_area"] = {
                        "left": min(start_pos[0], end_pos[0]),
                        "top": min(start_pos[1], end_pos[1]),
                        "width": abs(end_pos[0] - start_pos[0]),
                        "height": abs(end_pos[1] - start_pos[1])
                    }
                    
                    self.save_config()
                    print("\nMessage area calibrated and saved!")
                    break
                    
            time.sleep(0.1)

    def calibrate_username_area(self):
        print("\nCalibrating username area...")
        print("1. Move your mouse to the top-left corner of the username area")
        print("2. Press 'C' to capture the first point")
        print("3. Move your mouse to the bottom-right corner")
        print("4. Press 'C' again to capture the second point")
        print("\nPress Enter to start calibration (ESC to cancel)")
        
        input()
        
        start_pos = None
        end_pos = None
        captured_first = False
        
        while True:
            if keyboard.is_pressed('esc'):
                print("\nCalibration cancelled")
                return
                
            if keyboard.is_pressed('c'):
                if not captured_first:
                    start_pos = pyautogui.position()
                    print(f"Start position captured: {start_pos}")
                    captured_first = True
                    time.sleep(0.3)
                elif captured_first and not end_pos:
                    end_pos = pyautogui.position()
                    print(f"End position captured: {end_pos}")
                    
                    self.config["username_area"] = {
                        "left": min(start_pos[0], end_pos[0]),
                        "top": min(start_pos[1], end_pos[1]),
                        "width": abs(end_pos[0] - start_pos[0]),
                        "height": abs(end_pos[1] - start_pos[1])
                    }
                    
                    self.save_config()
                    print("\nUsername area calibrated and saved!")
                    break
                    
            time.sleep(0.1)

    def check_username(self, screenshot):
        try:
            new_size = tuple(int(dim * self.config["ocr_resolution"]) for dim in screenshot.size)
            if new_size[0] > 0 and new_size[1] > 0:
                screenshot = screenshot.resize(new_size, Image.Resampling.LANCZOS)

            text = pytesseract.image_to_string(screenshot, config=self.config["ocr_config"])
            username = text.strip()
            
            if not self.config["case_sensitive"]:
                username = username.lower()
                target_username = self.config["target_username"].lower()
            else:
                target_username = self.config["target_username"]

            return username == target_username
        except Exception as e:
            logging.error(f"Error checking username: {str(e)}")
            return False

    def check_for_message(self):
        try:
            if self.initial_scan:
                self.initial_scan = False
                self.processed_messages.clear()
                self.has_responded = False
                time.sleep(2)
                return False

            if self.has_responded:
                return False

            if self.config["target_username"]:
                username_area = self.config["username_area"]
                username_screenshot = ImageGrab.grab(bbox=(
                    username_area["left"],
                    username_area["top"],
                    username_area["left"] + username_area["width"],
                    username_area["top"] + username_area["height"]
                ))
                
                if not self.check_username(username_screenshot):
                    return False

            area = self.config["message_area"]
            screenshot = ImageGrab.grab(bbox=(
                area["left"],
                area["top"],
                area["left"] + area["width"],
                area["top"] + area["height"]
            ))
            
            new_size = tuple(int(dim * self.config["ocr_resolution"]) for dim in screenshot.size)
            if new_size[0] > 0 and new_size[1] > 0:
                screenshot = screenshot.resize(new_size, Image.Resampling.LANCZOS)

            text = pytesseract.image_to_string(screenshot, config=self.config["ocr_config"])
            lines = [line.strip() for line in text.split('\n') if line.strip()]

            current_visible_content = set()
            
            for line in lines:
                check_text = line if self.config["case_sensitive"] else line.lower()
                check_keywords = [k if self.config["case_sensitive"] else k.lower() for k in self.config["keywords"]]

                for keyword in check_keywords:
                    if keyword in check_text:
                        message_hash = hash(f"{line}_{lines.index(line)}")
                        current_visible_content.add(message_hash)
                        
                        if message_hash not in self.processed_messages and not self.has_responded:
                            self.messages_detected += 1
                            self.processed_messages.add(message_hash)
                            logging.info(f"New keyword '{keyword}' found in: {line}")
                            self.send_discord_message(self.config["response"])
                            self.has_responded = True
                            return True
            
            self.processed_messages = self.processed_messages.intersection(current_visible_content)
            return False

        except Exception as e:
            logging.error(f"Error checking message: {str(e)}")
            return False

    def edit_config(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        print("\nEdit Configuration")
        config_menu = [
            ["1", "Edit keywords", "Modify trigger keywords"],
            ["2", "Edit response message", "Change automatic response"],
            ["3", "Edit scan interval", "Adjust scanning frequency"],
            ["4", "Edit Discord token", "Update Discord authentication"],
            ["5", "Edit channel ID", "Change target Discord channel"],
            ["6", "Toggle case sensitivity", "Switch case matching"],
            ["7", "Edit target username", "Set specific username to monitor"],
            ["8", "Back to main menu", "Return to previous menu"]
        ]
        print(tabulate(config_menu, headers=["Option", "Action", "Description"], 
                      tablefmt="fancy_grid", colalign=("center", "left", "left")))
        
        choice = input("\nSelect option: ")
        
        if choice == "1":
            print("\nCurrent keywords:", ", ".join(self.config["keywords"]))
            new_keywords = input("Enter new keywords (comma-separated): ").split(",")
            self.config["keywords"] = [k.strip() for k in new_keywords if k.strip()]
        elif choice == "2":
            print("\nCurrent response:", self.config["response"])
            self.config["response"] = input("Enter new response: ").strip()
        elif choice == "3":
            print("\nCurrent scan interval:", self.config["scan_interval"])
            try:
                new_interval = float(input("Enter new scan interval (in seconds): "))
                if new_interval > 0:
                    self.config["scan_interval"] = new_interval
                else:
                    print("Interval must be greater than 0")
            except ValueError:
                print("Invalid input. Please enter a number.")
        elif choice == "4":
            self.config["discord_token"] = input("Enter Discord token: ").strip()
        elif choice == "5":
            self.config["channel_id"] = input("Enter channel ID: ").strip()
        elif choice == "6":
            self.config["case_sensitive"] = not self.config["case_sensitive"]
            print(f"\nCase sensitivity is now: {'ON' if self.config['case_sensitive'] else 'OFF'}")
        elif choice == "7":
            print("\nCurrent target username:", self.config.get("target_username", "None"))
            new_username = input("Enter target username (or leave empty to disable): ").strip()
            self.config["target_username"] = new_username
        elif choice == "8":
            return
        
        self.save_config()
        print("\nConfiguration saved!")

    def optimize_ocr(self):
        print("\nOCR Optimization")
        preview_window = tk.Tk()
        preview_window.title("OCR Preview")
        
        control_frame = ttk.Frame(preview_window, padding="10")
        control_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        preview_frame = ttk.Frame(preview_window, padding="10")
        preview_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        preview_text = tk.Text(preview_frame, width=60, height=10)
        preview_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        resolution_var = tk.DoubleVar(value=self.config["ocr_resolution"])
        ttk.Label(control_frame, text="Resolution Scale:").grid(row=0, column=0, padx=5)
        resolution_scale = ttk.Scale(
            control_frame,
            from_=0.1,
            to=2.0,
            orient=tk.HORIZONTAL,
            variable=resolution_var,
            length=200
        )
        resolution_scale.grid(row=0, column=1, padx=5)
        
        psm_var = tk.StringVar(value=self.config["ocr_config"].split()[1])
        ttk.Label(control_frame, text="PSM Mode:").grid(row=1, column=0, padx=5)
        psm_combo = ttk.Combobox(
            control_frame,
            textvariable=psm_var,
            values=["0", "1", "3", "4", "6", "7", "8", "9", "10", "11", "12", "13"]
        )
        psm_combo.grid(row=1, column=1, padx=5)
        
        update_id = None
        
        def update_preview():
            nonlocal update_id
            try:
                area = self.config["message_area"]
                screenshot = ImageGrab.grab(bbox=(
                    area["left"],
                    area["top"],
                    area["left"] + area["width"],
                    area["top"] + area["height"]
                ))
                
                new_size = tuple(int(dim * resolution_var.get()) for dim in screenshot.size)
                if new_size[0] > 0 and new_size[1] > 0:
                    screenshot = screenshot.resize(new_size, Image.Resampling.LANCZOS)
                
                ocr_config = f"--psm {psm_var.get()}"
                
                text = pytesseract.image_to_string(screenshot, config=ocr_config)
                
                preview_text.delete(1.0, tk.END)
                preview_text.insert(tk.END, text)
                
                update_id = preview_window.after(1000, update_preview)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to update preview: {str(e)}")
        
        def save_settings():
            nonlocal update_id
            if update_id is not None:
                preview_window.after_cancel(update_id)
            self.config["ocr_resolution"] = resolution_var.get()
            self.config["ocr_config"] = f"--psm {psm_var.get()}"
            self.save_config()
            preview_window.destroy()
        
        ttk.Button(control_frame, text="Save & Close", command=save_settings).grid(row=2, column=0, columnspan=2, pady=10)
        
        update_preview()
        
        preview_window.protocol("WM_DELETE_WINDOW", save_settings)
        preview_window.mainloop()

    def view_ocr_area(self):
        print("\nSelect area to view:")
        print("1. Message area")
        print("2. Username area")
        choice = input("\nEnter choice (1-2): ")
        
        area = self.config["message_area"] if choice == "1" else self.config["username_area"]
        area_type = "message" if choice == "1" else "username"
        
        screenshot = ImageGrab.grab(bbox=(
            area["left"],
            area["top"],
            area["left"] + area["width"],
            area["top"] + area["height"]
        ))
        
        window = tk.Tk()
        window.title(f"OCR {area_type.title()} Area Preview")
        
        photo = ImageTk.PhotoImage(screenshot)
        
        canvas = tk.Canvas(window, width=screenshot.width, height=screenshot.height)
        canvas.pack()
        canvas.create_image(0, 0, anchor=tk.NW, image=photo)
        
        crop_start = None
        crop_rect = None
        
        def start_crop(event):
            nonlocal crop_start, crop_rect
            crop_start = (event.x, event.y)
            if crop_rect:
                canvas.delete(crop_rect)
            crop_rect = canvas.create_rectangle(
                event.x, event.y, event.x, event.y,
                outline='red'
            )
        
        def update_crop(event):
            nonlocal crop_rect
            if crop_start:
                canvas.coords(crop_rect, crop_start[0], crop_start[1], event.x, event.y)
        
        def end_crop(event):
            nonlocal crop_start
            if crop_start:
                x1, y1 = crop_start
                x2, y2 = event.x, event.y
                area_key = "message_area" if choice == "1" else "username_area"
                self.config[area_key] = {
                    "left": self.config[area_key]["left"] + min(x1, x2),
                    "top": self.config[area_key]["top"] + min(y1, y2),
                    "width": abs(x2 - x1),
                    "height": abs(y2 - y1)
                }
                self.save_config()
                window.destroy()
        
        canvas.bind("<ButtonPress-1>", start_crop)
        canvas.bind("<B1-Motion>", update_crop)
        canvas.bind("<ButtonRelease-1>", end_crop)
        
        window.photo = photo
        window.mainloop()

    def start_monitoring(self):
        self.running = True
        self.initial_scan = True
        self.processed_messages.clear()
        self.has_responded = False
        self.start_time = datetime.now()
        print("\nStarting message monitor...")
        print(f"Looking for keywords: {', '.join(self.config['keywords'])}")
        print(f"Will respond with: {self.config['response']}")
        if self.config.get("target_username"):
            print(f"Monitoring messages from username: {self.config['target_username']}")
        print("\nPress ESC to stop monitoring")

        while self.running:
            if keyboard.is_pressed('esc'):
                self.stop_monitoring()
                break

            current_time = datetime.now()
            runtime = current_time - self.start_time
            
            print(f"\rRuntime: {str(runtime).split('.')[0]} | Messages Detected: {self.messages_detected} | Messages Sent: {self.messages_sent}", end="")
            
            if (current_time - self.last_check).total_seconds() >= self.config["scan_interval"]:
                self.check_for_message()
                self.last_check = current_time

            time.sleep(0.01)

    def stop_monitoring(self):
        self.running = False
        print("\nMonitoring stopped")

def main():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    try:
        if os.name == 'nt':
            tesseract_path = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
            if os.path.exists(tesseract_path):
                pytesseract.pytesseract.tesseract_cmd = tesseract_path
            else:
                print("Tesseract not found in default location!")
                custom_path = input("Enter Tesseract path (or press Enter to try system PATH): ")
                if custom_path:
                    pytesseract.pytesseract.tesseract_cmd = custom_path

        monitor = DiscordMonitor()

        while True:
            os.system('cls' if os.name == 'nt' else 'clear')
            
            header = pyfiglet.figlet_format("Discord Trigger Message", font="standard")
            print(header)
            print("Developed by 8wp".center(80))
            print("\n" + "="*80 + "\n")

            menu_items = [
                ["1", "Start monitoring", "Begin monitoring Discord messages"],
                ["2", "Calibrate message area", "Set up the screen area to monitor"],
                ["3", "Calibrate username area", "Set up the username area to monitor"],
                ["4", "Edit configuration", "Modify monitor settings"],
                ["5", "View current settings", "Display current configuration"],
                ["6", "Send test message", "Test Discord connectivity"],
                ["7", "Optimize OCR settings", "Adjust text recognition settings"],
                ["8", "View/Crop OCR area", "Preview and adjust monitored areas"],
                ["9", "Exit", "Close the application"]
            ]
            
            print(tabulate(menu_items, headers=["Option", "Action", "Description"], 
                         tablefmt="fancy_grid", colalign=("center", "left", "left")))

            choice = input("\nSelect option: ")

            if choice == "1":
                if not monitor.config["discord_token"] or not monitor.config["channel_id"]:
                    print("\nWarning: Discord token or channel ID not configured!")
                    print("Please configure Discord settings before starting.")
                    input("\nPress Enter to continue...")
                    continue
                monitor.start_monitoring()
            elif choice == "2":
                monitor.calibrate_message_area()
            elif choice == "3":
                monitor.calibrate_username_area()
            elif choice == "4":
                monitor.edit_config()
            elif choice == "5":
                print("\nCurrent configuration:")
                config_display = monitor.config.copy()
                if config_display["discord_token"]:
                    config_display["discord_token"] = "*" * len(config_display["discord_token"])
                formatted_config = [[k, str(v)] for k, v in config_display.items()]
                print(tabulate(formatted_config, headers=["Setting", "Value"], 
                             tablefmt="fancy_grid", colalign=("left", "left")))
            elif choice == "6":
                monitor.test_message()
            elif choice == "7":
                monitor.optimize_ocr()
            elif choice == "8":
                monitor.view_ocr_area()
            elif choice == "9":
                print("\nThank you for using Discord Trigger Message!")
                print("Exiting...")
                break

            if choice != "9":
                input("\nPress Enter to continue...")

    except Exception as e:
        logging.critical(f"Critical error: {str(e)}")
        print(f"\nAn error occurred: {str(e)}")
        input("\nPress Enter to exit...")

if __name__ == "__main__":

    main()
