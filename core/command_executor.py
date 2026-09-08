"""
Command Executor Module
Handles system commands and actions
"""

import logging
import subprocess
import os
import sys
import webbrowser
import pyautogui
import psutil
from pathlib import Path
import json

logger = logging.getLogger(__name__)


class CommandExecutor:
    """Execute system commands and actions"""
    
    def __init__(self, config):
        """
        Initialize command executor
        
        Args:
            config (ConfigManager): Configuration object
        """
        self.config = config
        self.custom_commands = self._load_custom_commands()
        
        logger.info("⚙️ Command executor initialized")
    
    def _load_custom_commands(self):
        """Load custom commands from file"""
        try:
            custom_file = self.config.get('commands.custom_commands_file', 'custom_commands.json')
            if Path(custom_file).exists():
                with open(custom_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logger.warning(f"⚠️ Could not load custom commands: {e}")
        
        return {}
    
    def execute(self, command_text):
        """
        Try to execute a command
        
        Args:
            command_text (str): User command text
        
        Returns:
            dict: {'success': bool, 'action': str, 'response': str}
        """
        command_lower = command_text.lower().strip()
        
        # Check custom commands first
        for custom_cmd, action in self.custom_commands.items():
            if custom_cmd.lower() in command_lower:
                return self._execute_action(action)
        
        # System commands
        # Time/Date
        if 'time' in command_lower or 'what time' in command_lower:
            return self._get_time()
        
        if 'date' in command_lower or 'what\'s the date' in command_lower:
            return self._get_date()
        
        # Application control
        if 'open' in command_lower:
            return self._open_application(command_text)
        
        if 'close' in command_lower or 'quit' in command_lower:
            return self._close_application(command_text)
        
        # Web search
        if 'search' in command_lower or 'google' in command_lower:
            return self._web_search(command_text)
        
        if 'open browser' in command_lower or 'open chrome' in command_lower:
            return self._open_browser()
        
        # Volume control
        if 'volume' in command_lower:
            return self._control_volume(command_text)
        
        # Screenshot
        if 'screenshot' in command_lower or 'take a picture' in command_lower:
            return self._take_screenshot()
        
        # Shutdown/Restart
        if 'shutdown' in command_lower:
            return self._shutdown()
        
        if 'restart' in command_lower:
            return self._restart()
        
        # Sleep
        if 'sleep' in command_lower:
            return self._sleep()
        
        # System info
        if 'system info' in command_lower or 'hardware' in command_lower:
            return self._get_system_info()
        
        # File explorer
        if 'file explorer' in command_lower or 'open files' in command_lower:
            return self._open_file_explorer()
        
        # Notepad
        if 'notepad' in command_lower or 'open notepad' in command_lower:
            return self._open_notepad()
        
        # Default: not a recognized command
        return {'success': False, 'action': None, 'response': None}
    
    def _get_time(self):
        """Get current time"""
        from datetime import datetime
        current_time = datetime.now().strftime("%I:%M %p")
        return {
            'success': True,
            'action': 'get_time',
            'response': f"The current time is {current_time}"
        }
    
    def _get_date(self):
        """Get current date"""
        from datetime import datetime
        current_date = datetime.now().strftime("%A, %B %d, %Y")
        return {
            'success': True,
            'action': 'get_date',
            'response': f"Today is {current_date}"
        }
    
    def _open_application(self, command_text):
        """Open an application"""
        try:
            # Extract app name
            app_name = command_text.replace('open', '').strip().lower()
            
            apps = {
                'notepad': 'notepad.exe',
                'paint': 'mspaint.exe',
                'calculator': 'calc.exe',
                'calc': 'calc.exe',
                'chrome': 'chrome.exe',
                'firefox': 'firefox.exe',
                'edge': 'msedge.exe',
                'excel': 'excel.exe',
                'word': 'winword.exe',
                'powershell': 'powershell.exe',
                'command prompt': 'cmd.exe',
                'cmd': 'cmd.exe',
            }
            
            if app_name in apps:
                subprocess.Popen(apps[app_name])
                return {
                    'success': True,
                    'action': 'open_app',
                    'response': f"Opening {app_name}"
                }
        except Exception as e:
            logger.error(f"❌ Error opening application: {e}")
        
        return {'success': False, 'action': None, 'response': None}
    
    def _close_application(self, command_text):
        """Close an application"""
        try:
            app_name = command_text.replace('close', '').replace('quit', '').strip().lower()
            
            # Kill process by name
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    if app_name in proc.info['name'].lower():
                        proc.kill()
                        return {
                            'success': True,
                            'action': 'close_app',
                            'response': f"Closed {proc.info['name']}"
                        }
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
        except Exception as e:
            logger.error(f"❌ Error closing application: {e}")
        
        return {'success': False, 'action': None, 'response': None}
    
    def _web_search(self, command_text):
        """Perform web search"""
        try:
            query = command_text.replace('search', '').replace('google', '').strip()
            url = f"https://www.google.com/search?q={query}"
            webbrowser.open(url)
            
            return {
                'success': True,
                'action': 'web_search',
                'response': f"Searching Google for {query}"
            }
        except Exception as e:
            logger.error(f"❌ Error searching: {e}")
        
        return {'success': False, 'action': None, 'response': None}
    
    def _open_browser(self):
        """Open default browser"""
        try:
            webbrowser.open('https://www.google.com')
            return {
                'success': True,
                'action': 'open_browser',
                'response': "Opening browser"
            }
        except Exception as e:
            logger.error(f"❌ Error opening browser: {e}")
        
        return {'success': False, 'action': None, 'response': None}
    
    def _control_volume(self, command_text):
        """Control system volume (Windows only)"""
        try:
            # This requires additional setup
            return {
                'success': True,
                'action': 'volume_control',
                'response': "Volume control not yet implemented"
            }
        except Exception as e:
            logger.error(f"❌ Error controlling volume: {e}")
        
        return {'success': False, 'action': None, 'response': None}
    
    def _take_screenshot(self):
        """Take a screenshot"""
        try:
            screenshot = pyautogui.screenshot()
            filename = f"screenshot_{int(__import__('time').time())}.png"
            screenshot.save(filename)
            
            return {
                'success': True,
                'action': 'screenshot',
                'response': f"Screenshot saved as {filename}"
            }
        except Exception as e:
            logger.error(f"❌ Error taking screenshot: {e}")
        
        return {'success': False, 'action': None, 'response': None}
    
    def _shutdown(self):
        """Shutdown system"""
        return {
            'success': True,
            'action': 'shutdown',
            'response': "System will shutdown in 30 seconds. Say cancel to stop."
        }
    
    def _restart(self):
        """Restart system"""
        return {
            'success': True,
            'action': 'restart',
            'response': "System will restart in 30 seconds. Say cancel to stop."
        }
    
    def _sleep(self):
        """Put system to sleep"""
        try:
            os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
            return {
                'success': True,
                'action': 'sleep',
                'response': "System going to sleep"
            }
        except Exception as e:
            logger.error(f"❌ Error sleeping: {e}")
        
        return {'success': False, 'action': None, 'response': None}
    
    def _get_system_info(self):
        """Get system information"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            
            info = f"CPU usage is {cpu_percent} percent. Memory usage is {memory.percent} percent."
            
            return {
                'success': True,
                'action': 'system_info',
                'response': info
            }
        except Exception as e:
            logger.error(f"❌ Error getting system info: {e}")
        
        return {'success': False, 'action': None, 'response': None}
    
    def _open_file_explorer(self):
        """Open file explorer"""
        try:
            os.startfile(os.path.expanduser("~"))
            return {
                'success': True,
                'action': 'open_explorer',
                'response': "Opening file explorer"
            }
        except Exception as e:
            logger.error(f"❌ Error opening file explorer: {e}")
        
        return {'success': False, 'action': None, 'response': None}
    
    def _open_notepad(self):
        """Open Notepad"""
        try:
            subprocess.Popen('notepad.exe')
            return {
                'success': True,
                'action': 'open_notepad',
                'response': "Opening Notepad"
            }
        except Exception as e:
            logger.error(f"❌ Error opening Notepad: {e}")
        
        return {'success': False, 'action': None, 'response': None}
    
    def _execute_action(self, action):
        """Execute a custom action"""
        try:
            if isinstance(action, str):
                subprocess.Popen(action)
            
            return {
                'success': True,
                'action': 'custom',
                'response': f"Executing action"
            }
        except Exception as e:
            logger.error(f"❌ Error executing action: {e}")
        
        return {'success': False, 'action': None, 'response': None}
