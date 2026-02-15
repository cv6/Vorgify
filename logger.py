import time
from proglog import ProgressBarLogger

class MyBarLogger(ProgressBarLogger):
    def __init__(self, update_callback, cancel_check_callback, estimated_duration=None):
        super().__init__(init_state=None, bars=None, ignored_bars=None, logged_bars='all', min_time_interval=0.2, ignore_bars_under=0)
        self.update_callback = update_callback
        self.cancel_check_callback = cancel_check_callback
        self.estimated_duration = estimated_duration
        self.last_update = 0

    def callback(self, **changes):
        # print(f"DEBUG CALLBACK: {changes}")
        if self.cancel_check_callback():
            raise Exception("User Cancel")
        
        if 'message' in changes:
             self.update_callback(0, changes['message'])

        if 'bars' in changes:
            bars = changes['bars']
            if 't' in bars:
                current = bars['t']['index']
                total = bars['t']['total']
                
                # Default total is sometimes None or 0 in moviepy
                if total is None or total <= 0:
                     # Fallback to estimated duration if available
                     total = self.estimated_duration if self.estimated_duration and self.estimated_duration > 0 else 100
                
                percent = current / total
                # Cap at 1.0 (100%)
                percent = min(1.0, max(0.0, percent))
                
                # Throttle updates to avoid UI freeze (e.g. max 5fps = 0.2s)
                now = time.time()
                if now - self.last_update > 0.2 or percent >= 1.0:
                     self.update_callback(percent, f"{int(percent*100)}%")
                     self.last_update = now
            elif 'chunk' in bars:
                # Also throttle chunk updates
                now = time.time()
                if now - self.last_update > 0.5:
                    self.update_callback(0, "Audio Processing...")
                    self.last_update = now
        
        else:
            # Debugging
            # print(f"Logger changes: {changes}")
            pass
