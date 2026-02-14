from proglog import ProgressBarLogger

class MyBarLogger(ProgressBarLogger):
    def __init__(self, update_callback, cancel_check_callback, estimated_duration=None):
        super().__init__(init_state=None, bars=None, ignored_bars=None, logged_bars='all', min_time_interval=0, ignore_bars_under=0)
        self.update_callback = update_callback
        self.cancel_check_callback = cancel_check_callback
        self.estimated_duration = estimated_duration

    def callback(self, **changes):
        if self.cancel_check_callback():
            raise Exception("User Cancel")
        
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
                
                self.update_callback(percent, f"{int(percent*100)}%")
            elif 'chunk' in bars:
                self.update_callback(0, "Audio Processing...")
