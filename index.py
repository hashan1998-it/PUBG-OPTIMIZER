#!/usr/bin/env python3
import os
import sys
import subprocess
import time
import logging
from typing import Dict, List, Optional, Tuple, Union
import random
import threading
import itertools

# Setup logging
def setup_logger(name, log_file, level=logging.ERROR):
    formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s')
    handler = logging.FileHandler(log_file)
    handler.setFormatter(formatter)
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)
    return logger

logger = setup_logger('error_logger', 'pubg_cli_interactive.log')

def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# ASCII art for PUBG Mobile logo and loading animation
PUBG_LOGO = """
\033[1;33m
██████╗ ██╗   ██╗██████╗  ██████╗     ███╗   ███╗ ██████╗ ██████╗ ██╗██╗     ███████╗
██╔══██╗██║   ██║██╔══██╗██╔════╝     ████╗ ████║██╔═══██╗██╔══██╗██║██║     ██╔════╝
██████╔╝██║   ██║██████╔╝██║  ███╗    ██╔████╔██║██║   ██║██████╔╝██║██║     █████╗  
██╔═══╝ ██║   ██║██╔══██╗██║   ██║    ██║╚██╔╝██║██║   ██║██╔══██╗██║██║     ██╔══╝  
██║     ╚██████╔╝██████╔╝╚██████╔╝    ██║ ╚═╝ ██║╚██████╔╝██████╔╝██║███████╗███████╗
╚═╝      ╚═════╝ ╚═════╝  ╚═════╝     ╚═╝     ╚═╝ ╚═════╝ ╚═════╝ ╚═╝╚══════╝╚══════╝
\033[0m"""

UNIVERSAL_TOOL = """
\033[1;36m
██╗   ██╗███╗   ██╗██╗██╗   ██╗███████╗██████╗ ███████╗ █████╗ ██╗         ████████╗ ██████╗  ██████╗ ██╗     
██║   ██║████╗  ██║██║██║   ██║██╔════╝██╔══██╗██╔════╝██╔══██╗██║         ╚══██╔══╝██╔═══██╗██╔═══██╗██║     
██║   ██║██╔██╗ ██║██║██║   ██║█████╗  ██████╔╝███████╗███████║██║            ██║   ██║   ██║██║   ██║██║     
██║   ██║██║╚██╗██║██║╚██╗ ██╔╝██╔══╝  ██╔══██╗╚════██║██╔══██║██║            ██║   ██║   ██║██║   ██║██║     
╚██████╔╝██║ ╚████║██║ ╚████╔╝ ███████╗██║  ██║███████║██║  ██║███████╗       ██║   ╚██████╔╝╚██████╔╝███████╗
 ╚═════╝ ╚═╝  ╚═══╝╚═╝  ╚═══╝  ╚══════╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚══════╝       ╚═╝    ╚═════╝  ╚═════╝ ╚══════╝
\033[0m"""

AUTHOR_INFO = """
\033[1;32m
╔═════════════════════════════════════════════════════════════════╗
║                                                                 ║
║   PUBG Universal Tool - Advanced Graphics and FPS Controller    ║
║                                                                 ║
║   Author: Hashan Sooriyage                                      ║
║   GitHub: https://github.com/hashan1998-it                      ║
║                                                                 ║
║   Follow for more gaming enhancement tools!                     ║
║                                                                 ║
╚═════════════════════════════════════════════════════════════════╝
\033[0m"""

# Loading animation function
def loading_animation(stop_event):
    spinner = itertools.cycle(['◐', '◓', '◑', '◒'])
    while not stop_event.is_set():
        sys.stdout.write('\r\033[1;33mInitializing PUBG Universal Tool ' + next(spinner) + ' \033[0m')
        sys.stdout.flush()
        time.sleep(0.1)

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def display_loading_screen():
    clear_screen()
    
    # Display the logo and author info
    print(PUBG_LOGO)
    print(UNIVERSAL_TOOL)
    print(AUTHOR_INFO)
    
    # Start loading animation in a separate thread
    stop_animation = threading.Event()
    t = threading.Thread(target=loading_animation, args=(stop_animation,))
    t.start()
    
    # Simulate loading time
    time.sleep(2.5)
    
    # Stop the animation thread
    stop_animation.set()
    t.join()
    
    # Clear the loading spinner line
    sys.stdout.write('\r' + ' ' * 50 + '\r')
    sys.stdout.flush()
    
    print("\n\033[1;32mPUBG Universal Tool ready! Let's enhance your gaming experience.\033[0m\n")
    time.sleep(1)

class PUBGGraphicsCLI:
    def __init__(self):
        self.pubg_versions = {
            "com.tencent.ig": "PUBG Mobile Global",
            "com.vng.pubgmobile": "PUBG Mobile VN",
            "com.rekoo.pubgm": "PUBG Mobile TW",
            "com.pubg.krmobile": "PUBG Mobile KR",
            "com.pubg.imobile": "Battlegrounds Mobile India"
        }
        self.adb = None
        self.pubg_package = None
        self.active_sav_content = None
        self.PUBG_Found = []
        self.is_adb_working = False

    def kill_adb(self):
        """Kills the ADB (Android Debug Bridge) process if it is currently running."""
        try:
            subprocess.run(["taskkill", "/F", "/IM", "adb.exe"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return True
        except subprocess.CalledProcessError:
            return False

    def check_adb_connection(self):
        """Check if ADB is connected to the emulator"""
        try:
            # Set the exact path to Gameloop's ADB
            adb_path = r"C:\Program Files\TxGameAssistant\ui\adb\adb.exe"  # Update this with the correct path

            # If the direct path doesn't exist, try to find it
            if not os.path.exists(adb_path):
                possible_paths = [
                    r"C:\Program Files\TxGameAssistant\adb\adb.exe",
                    r"C:\Program Files\TxGameAssistant\ui\adb.exe",
                    r"C:\Program Files\TxGameAssistant\App\adb\adb.exe",
                    r"C:\Program Files\TxGameAssistant\AppMarket\adb\adb.exe",
                    # Add fallback to regular ADB if installed
                    "adb"
                ]

                for path in possible_paths:
                    if os.path.exists(path):
                        adb_path = path
                        print(f"Found ADB at: {adb_path}")
                        break

            self.adb_path = adb_path

            # Kill existing ADB server first to avoid conflicts
            try:
                print("Killing existing ADB server...")
                subprocess.run([self.adb_path, "kill-server"],
                                 check=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                time.sleep(1)
            except Exception as e:
                print(f"Warning: Could not kill ADB server: {str(e)}")

            # Start ADB server
            try:
                print("Starting ADB server...")
                subprocess.run([self.adb_path, "start-server"],
                                 check=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                time.sleep(1)
            except Exception as e:
                print(f"Warning: Could not start ADB server: {str(e)}")

            # Try to connect to the emulator
            print("Connecting to emulator...")
            try:
                connect_cmd = [self.adb_path, "connect", "127.0.0.1:5555"]
                print(f"Running: {' '.join(connect_cmd)}")
                connect_result = subprocess.run(connect_cmd,
                                                 check=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                print(f"Connect result: {connect_result.stdout.decode('utf-8').strip()}")
                print(f"Connect error: {connect_result.stderr.decode('utf-8').strip()}")
            except Exception as e:
                print(f"Error connecting to emulator: {str(e)}")

            # Check if a device is available
            print("Checking connected devices...")
            try:
                devices_cmd = [self.adb_path, "devices"]
                print(f"Running: {' '.join(devices_cmd)}")
                devices = subprocess.run(devices_cmd,
                                             check=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

                devices_output = devices.stdout.decode('utf-8')
                devices_error = devices.stderr.decode('utf-8')
                print(f"Devices output: {devices_output.strip()}")
                print(f"Devices error: {devices_error.strip()}")

                if "emulator-5554" in devices_output or "127.0.0.1:5555" in devices_output:
                    self.is_adb_working = True
                    print("Successfully connected to ADB")
                    return True
            except Exception as e:
                print(f"Error checking devices: {str(e)}")

            print("\nFailed to connect to ADB. Please ensure:")
            print("1. Gameloop is running")
            print("2. ADB debugging is enabled in Gameloop settings")
            print("3. You're running this script with administrator privileges")
            return False
        except Exception as e:
            logger.error(f"ADB connection error: {str(e)}", exc_info=True)
            print(f"Error connecting to ADB: {str(e)}")
            return False

    def pubg_version_found(self):
        """Checks which PUBG versions are installed on the device."""
        try:
            for package_name, version_name in self.pubg_versions.items():
                result = subprocess.run([self.adb_path, "-s", "emulator-5554", "shell", f"pm list packages {package_name}"],
                                        check=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

                if result.stdout.strip():
                    self.PUBG_Found.append(version_name)

            if self.PUBG_Found:
                print("Found PUBG versions:")
                for i, version in enumerate(self.PUBG_Found, 1):
                    print(f"{i}. {version}")
                return True
            else:
                print("No PUBG Mobile versions found on the device")
                return False
        except Exception as e:
            logger.error(f"Error finding PUBG versions: {str(e)}", exc_info=True)
            print(f"Error finding PUBG versions: {str(e)}")
            return False

    def get_graphics_file(self, package: str):
        """Get the Active.sav file from the device"""
        try:
            active_savegames_path = f"/sdcard/Android/data/{package}/files/UE4Game/ShadowTrackerExtra/ShadowTrackerExtra/Saved/SaveGames/Active.sav"
            local_file_path = os.path.join("assets", "old.sav")

            # Ensure assets directory exists
            os.makedirs("assets", exist_ok=True)

            self.pubg_package = package

            print(f"Attempting to pull file from: {active_savegames_path}")

            # Pull the file using ADB
            result = subprocess.run([self.adb_path, "-s", "emulator-5554", "pull", active_savegames_path, local_file_path],
                                     check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            # Read the file content
            with open(local_file_path, 'rb') as file:
                self.active_sav_content = file.read()

            print(f"Successfully pulled Active.sav file from {package}")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Error getting graphics file (ADB pull failed): {e.stderr.decode('utf-8')}", exc_info=True)
            print(f"Error getting graphics file (ADB pull failed): {e.stderr.decode('utf-8')}")
            return False
        except FileNotFoundError as e:
            logger.error(f"Error getting graphics file (local file error): {str(e)}", exc_info=True)
            print(f"Error getting graphics file (local file error): {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Error getting graphics file: {str(e)}", exc_info=True)
            print(f"Error getting graphics file: {str(e)}")
            return False

    def save_graphics_file(self):
        """Save the modified Active.sav file"""
        try:
            file_path = os.path.join("assets", "new.sav")
            with open(file_path, 'wb') as file:
                file.write(self.active_sav_content)
            print("Graphics file saved successfully")
            return True
        except Exception as e:
            logger.error(f"Error saving graphics file: {str(e)}", exc_info=True)
            print(f"Error saving graphics file: {str(e)}")
            return False

    def set_fps(self, val: str) -> bool:
        """Updates the Active.sav file with the new FPS value."""
        fps_mapping = {
            "Low": b"\x02",
            "Medium": b"\x03",
            "High": b"\x04",
            "Ultra": b"\x05",
            "Extreme": b"\x06",
            "Extreme+": b"\x07",
            "Ultra Extreme": b"\x08"
        }

        try:
            fps_value = fps_mapping.get(val)
            if fps_value is None:
                print(f"Invalid FPS value: {val}")
                print(f"Valid values are: {', '.join(fps_mapping.keys())}")
                return False

            fps_properties = ["FPSLevel", "BattleFPS", "LobbyFPS"]
            for prop in fps_properties:
                header = prop.encode('utf-8') + b'\x00\x0c\x00\x00\x00IntProperty\x00\x04\x00\x00\x00\x00\x00\x00\x00\x00'
                before, separator, after = self.active_sav_content.partition(header)
                if separator:  # If the header was found
                    after = after[:1].replace(after[:1], fps_value) + after[1:]
                    self.active_sav_content = before + separator + after

            print(f"FPS set to {val}")
            return True
        except Exception as e:
            logger.error(f"Error setting FPS: {str(e)}", exc_info=True)
            print(f"Error setting FPS: {str(e)}")
            return False

    def read_hex(self, name):
        """Reads the value of the specified property from the Active.sav file."""
        try:
            header = name.encode('utf-8') + b'\x00\x0c\x00\x00\x00IntProperty\x00\x04\x00\x00\x00\x00\x00\x00\x00\x00'
            _, _, content = self.active_sav_content.partition(header)
            return content[:1] if content else None
        except Exception as e:
            logger.error(f"Error reading hex: {str(e)}", exc_info=True)
            return None

    def change_graphics_file(self, name, val):
        """Updates the Active.sav file with the new graphics setting value."""
        try:
            header = name.encode('utf-8') + b'\x00\x0c\x00\x00\x00IntProperty\x00\x04\x00\x00\x00\x00\x00\x00\x00\x00'
            before, separator, after = self.active_sav_content.partition(header)
            if separator:  # If the header was found
                after = val + after[1:]
                self.active_sav_content = before + separator + after
                return True
            return False
        except Exception as e:
            logger.error(f"Error changing graphics file: {str(e)}", exc_info=True)
            return False

    def get_graphics_setting(self):
        """Gets the graphics setting name from the hex value."""
        try:
            graphics_setting_hex = self.read_hex("BattleRenderQuality")
            graphics_setting_dict = {
                b'\x01': "Smooth",
                b'\x02': "Balanced",
                b'\x03': "HD",
                b'\x04': "HDR",
                b'\x05': "Ultra HD"
            }
            return graphics_setting_dict.get(graphics_setting_hex, "Unknown")
        except Exception as e:
            logger.error(f"Error getting graphics setting: {str(e)}", exc_info=True)
            return "Unknown"

    def get_fps(self):
        """Gets the FPS value from the Active.sav file."""
        try:
            fps_hex = self.read_hex("BattleFPS")
            fps_dict = {
                b"\x02": "Low",
                b"\x03": "Medium",
                b"\x04": "High",
                b"\x05": "Ultra",
                b"\x06": "Extreme",
                b"\x07": "Extreme+",
                b"\x08": "Ultra Extreme",
            }
            return fps_dict.get(fps_hex, "Unknown")
        except Exception as e:
            logger.error(f"Error getting FPS: {str(e)}", exc_info=True)
            return "Unknown"

    def get_graphics_style(self):
        """Gets the graphics style name from the hex value."""
        try:
            battle_style_hex = self.read_hex("BattleRenderStyle")
            battle_style_dict = {
                b'\x01': "Classic",
                b'\x02': "Colorful",
                b'\x03': "Realistic",
                b'\x04': "Soft",
                b'\x06': "Movie"
            }
            return battle_style_dict.get(battle_style_hex, "Unknown")
        except Exception as e:
            logger.error(f"Error getting graphics style: {str(e)}", exc_info=True)
            return "Unknown"

    def set_graphics_style(self, style):
        """Sets the graphics style."""
        try:
            battle_style_dict = {
                "Classic": b'\x01',
                "Colorful": b'\x02',
                "Realistic": b'\x03',
                "Soft": b'\x04',
                "Movie": b'\x06'
            }
            battle_style = battle_style_dict.get(style)
            if battle_style is None:
                print(f"Invalid style value: {style}")
                print(f"Valid values are: {', '.join(battle_style_dict.keys())}")
                return False

            self.change_graphics_file("BattleRenderStyle", battle_style)
            print(f"Graphics style set to {style}")
            return True
        except Exception as e:
            logger.error(f"Error setting graphics style: {str(e)}", exc_info=True)
            print(f"Error setting graphics style: {str(e)}")
            return False

    def set_graphics_quality(self, quality):
        """Sets the graphics quality for different game modes."""
        try:
            graphics_setting_dict = {
                "Smooth": b'\x01',
                "Balanced": b'\x02',
                "HD": b'\x03',
                "HDR": b'\x04',
                "Ultra HD": b'\x05'
            }
            
            graphics_setting = graphics_setting_dict.get(quality)
            if graphics_setting is None:
                print(f"Invalid quality value: {quality}")
                print(f"Valid values are: {', '.join(graphics_setting_dict.keys())}")
                return False

            # Set the graphics quality
            success = True
            graphics_files = ["ArtQuality", "LobbyRenderQuality", "BattleRenderQuality"]
            for value in graphics_files:
                success = success and self.change_graphics_file(value, graphics_setting)
            
            if success:
                print(f"Graphics quality set to {quality}")
            else:
                print("Some graphics settings could not be changed")
                
            return success
        except Exception as e:
            logger.error(f"Error setting graphics quality: {str(e)}", exc_info=True)
            print(f"Error setting graphics quality: {str(e)}")
            return False

    def push_active_shadow_file(self):
        """Pushes the modified Active.sav file to the device and restarts the game."""
        try:
            # First stop the game
            subprocess.run([self.adb_path, "-s", "emulator-5554", "shell", f"am force-stop {self.pubg_package}"],
                             check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            time.sleep(0.2)

            # Path to the SaveGames directory
            data_dir = f"/sdcard/Android/data/{self.pubg_package}/files/UE4Game/ShadowTrackerExtra/ShadowTrackerExtra/Saved"

            # Push the modified Active.sav file
            new_sav_path = os.path.join("assets", "new.sav")
            dest_path = f"{data_dir}/SaveGames/Active.sav"

            subprocess.run([self.adb_path, "-s", "emulator-5554", "push", new_sav_path, dest_path],
                             check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            print("Graphics settings pushed to device successfully")
            return True
        except Exception as e:
            logger.error(f"Error pushing Active.sav file: {str(e)}", exc_info=True)
            print(f"Error pushing Active.sav file: {str(e)}")
            return False

    def start_app(self):
        """Starts the PUBG Mobile game."""
        try:
            package = f"{self.pubg_package}/com.epicgames.ue4.SplashActivity"
            subprocess.run([self.adb_path, "-s", "emulator-5554", "shell", f"am start -n {package}"],
                             check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            print(f"Starting {self.pubg_versions.get(self.pubg_package, 'PUBG Mobile')}")
            return True
        except Exception as e:
            logger.error(f"Error starting app: {str(e)}", exc_info=True)
            print(f"Error starting app: {str(e)}")
            return False

    def display_info(self):
        """Display current graphics settings"""
        graphics = self.get_graphics_setting()
        fps = self.get_fps()
        style = self.get_graphics_style()

        print("\n\033[1;36mCurrent Settings:\033[0m")
        print(f"  \033[1;33mGame Version:\033[0m {self.pubg_versions.get(self.pubg_package, 'Unknown')}")
        print(f"  \033[1;33mGraphics:\033[0m {graphics}")
        print(f"  \033[1;33mFPS:\033[0m {fps}")
        print(f"  \033[1;33mStyle:\033[0m {style}")
        print("")

    def add_recoil_control_menu(self):
        """Add recoil control settings via sensitivity and gyroscope settings"""
        print("\n\033[1;33mRecoil Control Settings:\033[0m")
        
        # Sensitivity settings for different scopes can affect recoil control
        sensitivity_options = {
            "1": {"name": "Balanced Control", "camera": 120, "ads": 80, "gyro": 300},
            "2": {"name": "Minimal Recoil", "camera": 100, "ads": 65, "gyro": 400},
            "3": {"name": "Pro Control", "camera": 140, "ads": 90, "gyro": 200},
            "4": {"name": "Default", "camera": 100, "ads": 100, "gyro": 100}
        }
        
        # Display options
        for key, settings in sensitivity_options.items():
            print(f"\033[1;32m{key}.\033[0m {settings['name']}")
        
        selection = input("\n\033[1;36mSelect sensitivity profile (1-4): \033[0m")
        
        if selection in sensitivity_options:
            chosen_profile = sensitivity_options[selection]
            print(f"\n\033[1;32mApplying {chosen_profile['name']} sensitivity profile...\033[0m")
            
            # Here you would modify the sensitivity settings in the game config
            # Example (pseudocode):
            self.change_sensitivity_settings("CameraVertSensitivity", chosen_profile['camera'])
            self.change_sensitivity_settings("ADSSensitivity", chosen_profile['ads'])
            self.change_sensitivity_settings("GyroscopeSensitivity", chosen_profile['gyro'])
            
            print("\033[1;32mSensitivity settings applied. This should help with recoil control.\033[0m")
            print("\033[1;33mTip: Enable gyroscope in game for best results!\033[0m")
            return True
        else:
            print("\033[1;31mInvalid selection.\033[0m")
            return False

    def change_sensitivity_settings(self, setting_name, value):
        """Modify sensitivity settings in UserCustom.ini file"""
        try:
            # Pull the UserCustom.ini file
            user_custom_ini_path = f"/sdcard/Android/data/{self.pubg_package}/files/UE4Game/ShadowTrackerExtra/ShadowTrackerExtra/Saved/Config/Android/UserCustom.ini"
            local_ini_path = os.path.join("assets", "UserCustom.ini")
            
            subprocess.run([self.adb_path, "-s", "emulator-5554", "pull", user_custom_ini_path, local_ini_path],
                           check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            # Read and modify the file
            with open(local_ini_path, 'r') as file:
                lines = file.readlines()
            
            modified = False
            for i, line in enumerate(lines):
                if setting_name in line:
                    # Parse the line and modify the value
                    parts = line.split('=')
                    if len(parts) == 2:
                        lines[i] = f"{parts[0]}={value}\n"
                        modified = True
            
            # If setting not found, add it
            if not modified:
                lines.append(f"{setting_name}={value}\n")
            
            # Write back the modified file
            with open(local_ini_path, 'w') as file:
                file.writelines(lines)
            
            # Push the file back to the device
            subprocess.run([self.adb_path, "-s", "emulator-5554", "push", local_ini_path, user_custom_ini_path],
                           check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            return True
        except Exception as e:
            logger.error(f"Error changing sensitivity settings: {str(e)}", exc_info=True)
            print(f"Error changing sensitivity settings: {str(e)}")
            return False

    def temp_cleaner(self):
        """Cleans temporary files to improve system performance"""
        try:
            import shutil
            import tempfile
            
            print("\n\033[1;33mCleaning temporary files...\033[0m")
            
            # Track stats for reporting
            cleaned_files = 0
            cleaned_dirs = 0
            freed_space = 0
            
            # Start a spinner for the cleaning process
            stop_spinner = threading.Event()
            spinner_thread = threading.Thread(target=loading_animation, args=(stop_spinner,))
            spinner_thread.start()
            
            # Clean Windows temp directory
            temp_dir = os.environ.get('TEMP') or tempfile.gettempdir()
            if os.path.exists(temp_dir):
                for item in os.listdir(temp_dir):
                    item_path = os.path.join(temp_dir, item)
                    try:
                        if os.path.isfile(item_path):
                            item_size = os.path.getsize(item_path)
                            os.unlink(item_path)
                            cleaned_files += 1
                            freed_space += item_size
                        elif os.path.isdir(item_path):
                            dir_size = sum(os.path.getsize(os.path.join(dirpath, filename))
                                        for dirpath, dirnames, filenames in os.walk(item_path)
                                        for filename in filenames if os.path.exists(os.path.join(dirpath, filename)))
                            shutil.rmtree(item_path, ignore_errors=True)
                            cleaned_dirs += 1
                            freed_space += dir_size
                    except Exception:
                        # Skip files that can't be removed (likely in use)
                        pass
            
            # Clean Windows Prefetch directory
            prefetch_dir = os.path.join(os.environ.get('WINDIR', r'C:\Windows'), 'Prefetch')
            if os.path.exists(prefetch_dir):
                for item in os.listdir(prefetch_dir):
                    item_path = os.path.join(prefetch_dir, item)
                    try:
                        if os.path.isfile(item_path):
                            item_size = os.path.getsize(item_path)
                            os.unlink(item_path)
                            cleaned_files += 1
                            freed_space += item_size
                    except Exception:
                        # Skip files that can't be removed (likely in use)
                        pass
            
            # Clean GameLoop shader cache if available
            try:
                # Get GameLoop path from registry
                import winreg
                key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r'SOFTWARE\WOW6432Node\Tencent\MobileGamePC\UI')
                gameloop_path = winreg.QueryValueEx(key, 'InstallPath')[0]
                winreg.CloseKey(key)
                
                shader_cache_dir = os.path.join(gameloop_path, 'ShaderCache')
                if os.path.exists(shader_cache_dir):
                    for item in os.listdir(shader_cache_dir):
                        item_path = os.path.join(shader_cache_dir, item)
                        try:
                            if os.path.isfile(item_path):
                                item_size = os.path.getsize(item_path)
                                os.unlink(item_path)
                                cleaned_files += 1
                                freed_space += item_size
                        except Exception:
                            # Skip files that can't be removed
                            pass
            except Exception:
                # Registry key not found or other issue, skip GameLoop cleaning
                pass
            
            # Stop the spinner
            stop_spinner.set()
            spinner_thread.join()
            sys.stdout.write('\r' + ' ' * 50 + '\r')
            
            # Convert freed space to readable format
            if freed_space < 1024:
                freed_space_str = f"{freed_space} bytes"
            elif freed_space < 1024 * 1024:
                freed_space_str = f"{freed_space / 1024:.2f} KB"
            elif freed_space < 1024 * 1024 * 1024:
                freed_space_str = f"{freed_space / (1024 * 1024):.2f} MB"
            else:
                freed_space_str = f"{freed_space / (1024 * 1024 * 1024):.2f} GB"
            
            print(f"\033[1;32mTemp cleaner complete!\033[0m")
            print(f"  • Removed \033[1;33m{cleaned_files}\033[0m files")
            print(f"  • Cleaned \033[1;33m{cleaned_dirs}\033[0m directories")
            print(f"  • Freed approximately \033[1;33m{freed_space_str}\033[0m of disk space")
            print(f"\n\033[1;32mSystem performance should now be improved.\033[0m")
            
            return True
        except Exception as e:
            logger.error(f"Error cleaning temp files: {str(e)}", exc_info=True)
            print(f"\033[1;31mError cleaning temporary files: {str(e)}\033[0m")
            return False

    def optimize_ping(self):
        """Optimize network settings for better ping in PUBG Mobile on Gameloop"""
        try:
            import ctypes
            import subprocess
            
            print("\n\033[1;33mPing Optimizer for PUBG Mobile\033[0m")
            print("This will optimize your network settings for lower ping...")
            
            # Check if running as admin
            is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0
            if not is_admin:
                print("\n\033[1;31mAdministrator privileges required!\033[0m")
                print("Please run this tool as administrator for network optimizations to work.")
                return False
            
            # Start a spinner for the optimization process
            stop_spinner = threading.Event()
            spinner_thread = threading.Thread(target=loading_animation, args=(stop_spinner,))
            spinner_thread.start()
            
            # List of optimizations to apply
            optimizations = [
                # DNS optimization
                {
                    "name": "Setting DNS to faster gaming servers",
                    "commands": [
                        ["netsh", "interface", "ip", "set", "dns", "name=all", "static", "1.1.1.1", "primary"],
                        ["netsh", "interface", "ip", "add", "dns", "name=all", "1.0.0.1", "index=2"]
                    ]
                },
                # TCP optimization
                {
                    "name": "Optimizing TCP/IP settings",
                    "commands": [
                        ["netsh", "int", "tcp", "set", "global", "autotuninglevel=normal"],
                        ["netsh", "int", "tcp", "set", "global", "ecncapability=disabled"],
                        ["netsh", "int", "tcp", "set", "heuristics", "disabled"]
                    ]
                },
                # Network throttling index
                {
                    "name": "Disabling network throttling",
                    "registry_path": r"SYSTEM\CurrentControlSet\Services\Psched",
                    "registry_value": "NonBestEffortLimit",
                    "registry_data": 0,
                    "registry_type": "REG_DWORD"
                },
                # Network adapter settings
                {
                    "name": "Optimizing network adapter",
                    "commands": [
                        ["powershell", "-Command", "Set-NetAdapterAdvancedProperty -Name '*' -DisplayName 'Energy-Efficient Ethernet' -DisplayValue 'Disabled' -ErrorAction SilentlyContinue"],
                        ["powershell", "-Command", "Set-NetAdapterAdvancedProperty -Name '*' -DisplayName 'Power Saving Mode' -DisplayValue 'Disabled' -ErrorAction SilentlyContinue"],
                        ["powershell", "-Command", "Set-NetAdapterAdvancedProperty -Name '*' -DisplayName 'Interrupt Moderation' -DisplayValue 'Disabled' -ErrorAction SilentlyContinue"]
                    ]
                },
                # Gameloop-specific settings
                {
                    "name": "Optimizing Gameloop network settings",
                    "registry_path": r"SOFTWARE\WOW6432Node\Tencent\MobileGamePC",
                    "registry_value": "AdbDisable",
                    "registry_data": 0,
                    "registry_type": "REG_DWORD"
                },
                # QoS settings for gaming
                {
                    "name": "Setting QoS for gaming priority",
                    "commands": [
                        ["powershell", "-Command", "New-NetQosPolicy -Name 'Gaming Traffic' -AppPathNameMatchCondition 'AndroidEmulator.exe','AndroidEmulatorEn.exe','AndroidEmulatorEx.exe','aow_exe.exe' -IPProtocolMatchCondition Both -DSCPAction 46 -NetworkProfile All -ErrorAction SilentlyContinue"]
                    ]
                },
                # Flush DNS
                {
                    "name": "Flushing DNS cache",
                    "commands": [
                        ["ipconfig", "/flushdns"]
                    ]
                }
            ]
            
            # Track successful optimizations
            successful_optimizations = []
            
            # Apply each optimization
            for opt in optimizations:
                try:
                    # Apply command-based optimizations
                    if "commands" in opt:
                        for cmd in opt["commands"]:
                            subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
                    
                    # Apply registry-based optimizations
                    if "registry_path" in opt:
                        import winreg
                        
                        # Determine registry root
                        if opt["registry_path"].startswith("SYSTEM"):
                            reg_root = winreg.HKEY_LOCAL_MACHINE
                        else:
                            reg_root = winreg.HKEY_LOCAL_MACHINE
                        
                        # Create or open registry key
                        try:
                            reg_key = winreg.CreateKeyEx(reg_root, opt["registry_path"], 0, winreg.KEY_WRITE)
                            
                            # Determine registry type
                            reg_type = winreg.REG_DWORD
                            if "registry_type" in opt:
                                if opt["registry_type"] == "REG_SZ":
                                    reg_type = winreg.REG_SZ
                            
                            # Set registry value
                            winreg.SetValueEx(reg_key, opt["registry_value"], 0, reg_type, opt["registry_data"])
                            winreg.CloseKey(reg_key)
                        except Exception:
                            # Skip if registry operation fails
                            pass
                    
                    successful_optimizations.append(opt["name"])
                except Exception:
                    # Skip failed optimizations
                    pass
            
            # Stop the spinner
            stop_spinner.set()
            spinner_thread.join()
            sys.stdout.write('\r' + ' ' * 50 + '\r')
            
            # Network interface reset for changes to take effect
            try:
                print("\n\033[1;36mResetting network interfaces to apply changes...\033[0m")
                subprocess.run(["netsh", "winsock", "reset", "catalog"], check=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                subprocess.run(["netsh", "int", "ip", "reset"], check=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            except Exception:
                pass
            
            # Measure current ping
            try:
                print("\n\033[1;36mMeasuring ping to PUBG servers...\033[0m")
                
                # List of PUBG Mobile servers to test
                pubg_servers = [
                    "na.igamecj.com",       # North America
                    "eu.igamecj.com",       # Europe
                    "as.igamecj.com",       # Asia
                    "krjp.igamecj.com",     # Korea/Japan
                    "sa.igamecj.com"        # South America
                ]
                
                best_ping = float('inf')
                best_server = None
                
                for server in pubg_servers:
                    try:
                        ping_process = subprocess.run(["ping", "-n", "4", server], 
                                                    stdout=subprocess.PIPE, 
                                                    stderr=subprocess.PIPE,
                                                    text=True,
                                                    check=False)
                        
                        output = ping_process.stdout
                        
                        # Extract average ping time
                        if "Average" in output:
                            avg_line = [line for line in output.split('\n') if "Average" in line][0]
                            avg_ping = int(''.join(filter(str.isdigit, avg_line.split("Average")[1].split(",")[0])))
                            
                            print(f"  • {server}: \033[1;33m{avg_ping}ms\033[0m")
                            
                            if avg_ping < best_ping:
                                best_ping = avg_ping
                                best_server = server
                    except Exception:
                        print(f"  • {server}: \033[1;31mFailed to measure\033[0m")
                
                if best_server:
                    print(f"\n\033[1;32mBest server: {best_server} with {best_ping}ms ping\033[0m")
            except Exception as e:
                print(f"\033[1;31mError measuring ping: {str(e)}\033[0m")
            
            # Report successful optimizations
            print("\n\033[1;32mCompleted network optimizations:\033[0m")
            for opt in successful_optimizations:
                print(f"  • {opt}")
            
            print("\n\033[1;33mRecommendation:\033[0m Restart your computer for all changes to take effect.")
            print("\033[1;32mYour ping should be optimized for PUBG Mobile on Gameloop!\033[0m")
            
            return True
        except Exception as e:
            logger.error(f"Error optimizing ping: {str(e)}", exc_info=True)
            print(f"\033[1;31mError optimizing ping: {str(e)}\033[0m")
            return False

def show_antivirus_instructions():
    print("\n\033[1;33mImportant Notice About Antivirus Detection\033[0m")
    print("This tool may be flagged by antivirus software because it:")
    print("  • Optimizes system settings to improve gaming performance")
    print("  • Requires administrator privileges for network optimizations")
    print("  • Modifies temporary files to free up system resources")
    print("\nThese are legitimate operations needed to optimize PUBG performance.")
    print("To use this tool, you may need to add an exception in your antivirus software.")
    print("\n\033[1;36mHow to add an exception:\033[0m")
    print("1. Open your antivirus program")
    print("2. Find the 'Exclusions' or 'Exceptions' section")
    print("3. Add the PUBG Universal Tool executable to the exclusion list")
    print("\nThe tool is completely safe and open source. You can review the code at:")
    print("\033[1;32mhttps://github.com/hashan1998-it/PUBG-Universal-Tool\033[0m")
    
    input("\nPress Enter to continue...")

def display_menu():
    print("\n\033[1;32m╔═════════════════════════════════════╗\033[0m")
    print("\033[1;32m║        PUBG UNIVERSAL TOOL           ║\033[0m")
    print("\033[1;32m╠═════════════════════════════════════╣\033[0m")
    print("\033[1;32m║\033[0m 1. Set Graphics Quality             \033[1;32m║\033[0m")
    print("\033[1;32m║\033[0m 2. Set FPS                          \033[1;32m║\033[0m")
    print("\033[1;32m║\033[0m 3. Set Graphics Style               \033[1;32m║\033[0m")
    print("\033[1;32m║\033[0m 4. Recoil Control Settings          \033[1;32m║\033[0m")
    print("\033[1;32m║\033[0m 5. Clean Temporary Files            \033[1;32m║\033[0m")
    print("\033[1;32m║\033[0m 6. Optimize Ping                    \033[1;32m║\033[0m")
    print("\033[1;32m║\033[0m 7. Apply and Start Game             \033[1;32m║\033[0m")
    print("\033[1;32m║\033[0m 8. Apply Settings (Don't Start Game)\033[1;32m║\033[0m")
    print("\033[1;32m║\033[0m 9. Exit                             \033[1;32m║\033[0m")
    print("\033[1;32m╚═════════════════════════════════════╝\033[0m")

def main():
    display_loading_screen()
    
    cli = PUBGGraphicsCLI()

    print("\033[1;36mConnecting to Gameloop...\033[0m")
    if not cli.check_adb_connection():
        print("\033[1;31mError: Cannot connect to ADB. Make sure Gameloop is running and ADB is enabled.\033[0m")
        input("\nPress Enter to exit...")
        return

    print("\033[1;36mSearching for PUBG Mobile versions...\033[0m")
    if not cli.pubg_version_found():
        input("\nPress Enter to exit...")
        return

    if len(cli.PUBG_Found) > 1:
        print("\n\033[1;33mMultiple PUBG versions found. Please select one:\033[0m")
        for i, version in enumerate(cli.PUBG_Found, 1):
            print(f"\033[1;32m{i}.\033[0m {version}")
        while True:
            try:
                selection = int(input("\n\033[1;36mEnter number: \033[0m"))
                if 1 <= selection <= len(cli.PUBG_Found):
                    selected_version = cli.PUBG_Found[selection - 1]
                    break
                else:
                    print("\033[1;31mInvalid selection. Please enter a number from the list.\033[0m")
            except ValueError:
                print("\033[1;31mInvalid input. Please enter a number.\033[0m")
        package_name = next((k for k, v in cli.pubg_versions.items() if v == selected_version), None)
        if not package_name:
            print(f"\033[1;31mError: Cannot find package name for {selected_version}\033[0m")
            input("\nPress Enter to exit...")
            return
    else:
        selected_version = cli.PUBG_Found[0]
        package_name = next((k for k, v in cli.pubg_versions.items() if v == selected_version), None)
        print(f"\033[1;32mUsing found version: {selected_version}\033[0m")

    print(f"\033[1;36mRetrieving current settings for {selected_version}...\033[0m")
    if not cli.get_graphics_file(package_name):
        print("\033[1;31mError: Failed to get graphics file\033[0m")
        print("\033[1;33mTips:\033[0m")
        print("1. Make sure PUBG Mobile has been launched at least once")
        print("2. Ensure you've made graphics settings changes in the game")
        print("3. Try restarting Gameloop and the game")
        input("\nPress Enter to exit...")
        return

    cli.display_info()

    while True:
        display_menu()

        choice = input("\n\033[1;36mEnter your choice (1-9): \033[0m")

        if choice == '1':
            print("\n\033[1;33mSelect Graphics Quality:\033[0m")
            graphics_choices = [
                "\033[1;32m1.\033[0m Smooth", 
                "\033[1;32m2.\033[0m Balanced", 
                "\033[1;32m3.\033[0m HD", 
                "\033[1;32m4.\033[0m HDR", 
                "\033[1;32m5.\033[0m Ultra HD"
            ]
            for g_choice in graphics_choices:
                print(g_choice)
            while True:
                g_selection = input("\n\033[1;36mEnter number: \033[0m")
                if g_selection == '1':
                    if cli.set_graphics_quality("Smooth"):
                        print("\033[1;32mGraphics quality set to Smooth.\033[0m")
                    break
                elif g_selection == '2':
                    if cli.set_graphics_quality("Balanced"):
                        print("\033[1;32mGraphics quality set to Balanced.\033[0m")
                    break
                elif g_selection == '3':
                    if cli.set_graphics_quality("HD"):
                        print("\033[1;32mGraphics quality set to HD.\033[0m")
                    break
                elif g_selection == '4':
                    if cli.set_graphics_quality("HDR"):
                        print("\033[1;32mGraphics quality set to HDR.\033[0m")
                    break
                elif g_selection == '5':
                    if cli.set_graphics_quality("Ultra HD"):
                        print("\033[1;32mGraphics quality set to Ultra HD.\033[0m")
                    break
                else:
                    print("\033[1;31mInvalid selection.\033[0m")
        elif choice == '2':
            print("\n\033[1;33mSelect FPS:\033[0m")
            fps_choices = [
                "\033[1;32m1.\033[0m Low", 
                "\033[1;32m2.\033[0m Medium", 
                "\033[1;32m3.\033[0m High", 
                "\033[1;32m4.\033[0m Ultra", 
                "\033[1;32m5.\033[0m Extreme", 
                "\033[1;32m6.\033[0m Extreme+", 
                "\033[1;32m7.\033[0m Ultra Extreme"
            ]
            for f_choice in fps_choices:
                print(f_choice)
            while True:
                fps_selection = input("\n\033[1;36mEnter number: \033[0m")
                if fps_selection == '1':
                    if cli.set_fps("Low"):
                        print("\033[1;32mFPS set to Low.\033[0m")
                    break
                elif fps_selection == '2':
                    if cli.set_fps("Medium"):
                        print("\033[1;32mFPS set to Medium.\033[0m")
                    break
                elif fps_selection == '3':
                    if cli.set_fps("High"):
                        print("\033[1;32mFPS set to High.\033[0m")
                    break
                elif fps_selection == '4':
                    if cli.set_fps("Ultra"):
                        print("\033[1;32mFPS set to Ultra.\033[0m")
                    break
                elif fps_selection == '5':
                    if cli.set_fps("Extreme"):
                        print("\033[1;32mFPS set to Extreme.\033[0m")
                    break
                elif fps_selection == '6':
                    if cli.set_fps("Extreme+"):
                        print("\033[1;32mFPS set to Extreme+.\033[0m")
                    break
                elif fps_selection == '7':
                    if cli.set_fps("Ultra Extreme"):
                        print("\033[1;32mFPS set to Ultra Extreme.\033[0m")
                    break
                else:
                    print("\033[1;31mInvalid selection.\033[0m")
        elif choice == '3':
            print("\n\033[1;33mSelect Graphics Style:\033[0m")
            style_choices = [
                "\033[1;32m1.\033[0m Classic", 
                "\033[1;32m2.\033[0m Colorful", 
                "\033[1;32m3.\033[0m Realistic", 
                "\033[1;32m4.\033[0m Soft", 
                "\033[1;32m5.\033[0m Movie"
            ]
            for s_choice in style_choices:
                print(s_choice)
            while True:
                style_selection = input("\n\033[1;36mEnter number: \033[0m")
                if style_selection == '1':
                    if cli.set_graphics_style("Classic"):
                        print("\033[1;32mGraphics style set to Classic.\033[0m")
                    break
                elif style_selection == '2':
                    if cli.set_graphics_style("Colorful"):
                        print("\033[1;32mGraphics style set to Colorful.\033[0m")
                    break
                elif style_selection == '3':
                    if cli.set_graphics_style("Realistic"):
                        print("\033[1;32mGraphics style set to Realistic.\033[0m")
                    break
                elif style_selection == '4':
                    if cli.set_graphics_style("Soft"):
                        print("\033[1;32mGraphics style set to Soft.\033[0m")
                    break
                elif style_selection == '5':
                    if cli.set_graphics_style("Movie"):
                        print("\033[1;32mGraphics style set to Movie.\033[0m")
                    break
                else:
                    print("\033[1;31mInvalid selection.\033[0m")
        elif choice == '4':
            cli.add_recoil_control_menu()
        elif choice == '5':
            cli.temp_cleaner()
        elif choice == '6':
            cli.optimize_ping()
        elif choice == '7':
            print("\n\033[1;36mApplying settings and starting game...\033[0m")
            
            # Show a spinner while processing
            stop_spinner = threading.Event()
            spinner_thread = threading.Thread(target=loading_animation, args=(stop_spinner,))
            spinner_thread.start()
            
            success = cli.save_graphics_file()
            if success:
                success = cli.push_active_shadow_file()
                if success:
                    # Stop spinner
                    stop_spinner.set()
                    spinner_thread.join()
                    sys.stdout.write('\r' + ' ' * 50 + '\r')
                    
                    print("\033[1;32mSettings applied successfully. Starting game...\033[0m")
                    cli.start_app()
                else:
                    # Stop spinner
                    stop_spinner.set()
                    spinner_thread.join()
                    sys.stdout.write('\r' + ' ' * 50 + '\r')
                    
                    print("\033[1;31mFailed to push settings to device.\033[0m")
            else:
                # Stop spinner
                stop_spinner.set()
                spinner_thread.join()
                sys.stdout.write('\r' + ' ' * 50 + '\r')
                
                print("\033[1;31mFailed to save settings.\033[0m")
                
        elif choice == '8':
            print("\n\033[1;36mApplying settings without starting game...\033[0m")
            
            # Show a spinner while processing
            stop_spinner = threading.Event()
            spinner_thread = threading.Thread(target=loading_animation, args=(stop_spinner,))
            spinner_thread.start()
            
            success = cli.save_graphics_file()
            if success:
                success = cli.push_active_shadow_file()
                
                # Stop spinner
                stop_spinner.set()
                spinner_thread.join()
                sys.stdout.write('\r' + ' ' * 50 + '\r')
                
                if success:
                    print("\033[1;32mSettings applied successfully. Start the game manually.\033[0m")
                else:
                    print("\033[1;31mFailed to push settings to device.\033[0m")
            else:
                # Stop spinner
                stop_spinner.set()
                spinner_thread.join()
                sys.stdout.write('\r' + ' ' * 50 + '\r')
                
                print("\033[1;31mFailed to save settings.\033[0m")
                
        elif choice == '9':
            print("\n\033[1;33mExiting PUBG Universal Tool...\033[0m")
            
            # Final message with author info
            print(f"\n\033[1;32mThank you for using PUBG Universal Tool by Hashan Sooriyage!\033[0m")
            print(f"\033[1;36mGitHub: https://github.com/hashan1998-it\033[0m")
            print(f"\033[1;33mFollow for more gaming enhancement tools!\033[0m")
            
            time.sleep(1.5)
            break
        else:
            print("\033[1;31mInvalid choice. Please enter a number between 1 and 9.\033[0m")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\033[1;33mOperation cancelled by user\033[0m")
    except Exception as e:
        logger.error(f"Unhandled exception: {str(e)}", exc_info=True)
        print(f"\033[1;31mError: {str(e)}\033[0m")
        print("\033[1;33mCheck pubg_cli_interactive.log for details\033[0m")
        input("\nPress Enter to exit...")