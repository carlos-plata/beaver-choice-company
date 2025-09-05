"""
Terminal Animation System for request processing visualization
"""

import time
import logging

logger = logging.getLogger(__name__)


class TerminalAnimator:
    """Real-time terminal animation for customer request processing"""
    
    def __init__(self):
        self.active = False
        self.current_step = ""
        self.steps_completed = []
        
    def start_animation(self, customer_name: str):
        """Start processing animation for customer"""
        self.active = True
        self.current_step = f"Processing request for {customer_name}..."
        self.steps_completed = []
        print(f"\n{self.current_step}")
        
    def update_step(self, step: str, agent: str):
        """Update current processing step"""
        if self.active:
            self.steps_completed.append(f"[DONE] {step}")
            self.current_step = f"[{agent}]: {step}"
            print(f"  {self.current_step}")
            time.sleep(0.5)  # Animation delay for user experience
    
    def complete_animation(self, result_summary: str):
        """Complete the animation sequence"""
        if self.active:
            print(f"  Result: {result_summary}")
            print(f"  Steps completed: {len(self.steps_completed)}")
            self.active = False
            
    def show_progress_bar(self, current: int, total: int, description: str = ""):
        """Show progress bar for batch operations"""
        if total == 0:
            return
            
        percent = int((current / total) * 100)
        bar_length = 30
        filled = int((current / total) * bar_length)
        bar = "█" * filled + "░" * (bar_length - filled)
        
        print(f"\r{description} [{bar}] {percent}% ({current}/{total})", end="", flush=True)
        
        if current == total:
            print()  # New line when complete