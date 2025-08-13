"""
Progress Dialog with Animation for Image to PDF Converter
"""

import tkinter as tk
from tkinter import ttk
import threading
import time

class ProgressDialog:
    """Progress dialog with animated waiting indicator."""
    
    def __init__(self, parent, message="Processing..."):
        """Initialize the progress dialog."""
        self.parent = parent
        self.message = message
        self.dialog = None
        self.progress_var = None
        self.is_running = False
        self.animation_after_id = None
        
    def show(self):
        """Show the progress dialog."""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("Please Wait")
        self.dialog.geometry("300x120")
        self.dialog.resizable(False, False)
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        # Center the dialog
        self.center_dialog()
        
        # Create widgets
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(expand=True, fill='both')
        
        # Message label
        message_label = ttk.Label(
            main_frame,
            text=self.message,
            font=('Arial', 10)
        )
        message_label.pack(pady=(0, 15))
        
        # Progress bar (indeterminate)
        self.progress_var = tk.StringVar()
        progress_bar = ttk.Progressbar(
            main_frame,
            mode='indeterminate',
            length=250
        )
        progress_bar.pack(pady=(0, 10))
        progress_bar.start(10)  # Start animation
        
        # Status label for animated dots
        self.status_label = ttk.Label(
            main_frame,
            text="Working...",
            font=('Arial', 8),
            foreground='gray'
        )
        self.status_label.pack()
        
        # Start dot animation
        self.is_running = True
        self.animate_dots()
        
        # Prevent dialog from being closed by user
        self.dialog.protocol("WM_DELETE_WINDOW", lambda: None)
        
    def animate_dots(self):
        """Animate the dots in the status message."""
        if not self.is_running or not self.dialog or not self.dialog.winfo_exists():
            return
            
        current_text = self.status_label.cget("text")
        if current_text.endswith("..."):
            new_text = "Working"
        elif current_text.endswith(".."):
            new_text = "Working..."
        elif current_text.endswith("."):
            new_text = "Working.."
        else:
            new_text = "Working."
            
        self.status_label.config(text=new_text)
        
        # Schedule next animation frame
        self.animation_after_id = self.dialog.after(500, self.animate_dots)
        
    def center_dialog(self):
        """Center the dialog on the parent window."""
        self.dialog.update_idletasks()
        
        # Get parent window position and size
        parent_x = self.parent.winfo_x()
        parent_y = self.parent.winfo_y()
        parent_width = self.parent.winfo_width()
        parent_height = self.parent.winfo_height()
        
        # Get dialog size
        dialog_width = self.dialog.winfo_width()
        dialog_height = self.dialog.winfo_height()
        
        # Calculate centered position
        x = parent_x + (parent_width - dialog_width) // 2
        y = parent_y + (parent_height - dialog_height) // 2
        
        self.dialog.geometry(f"+{x}+{y}")
        
    def close(self):
        """Close the progress dialog."""
        self.is_running = False
        
        # Cancel animation
        if self.animation_after_id:
            self.dialog.after_cancel(self.animation_after_id)
            
        if self.dialog and self.dialog.winfo_exists():
            self.dialog.destroy()
            
    def run_task(self, task_func, callback=None):
        """
        Run a task in a separate thread and show progress.
        
        Args:
            task_func: Function to run in background thread
            callback: Function to call when task completes (receives result)
        """
        self.show()
        
        def worker():
            """Worker thread function."""
            try:
                result = task_func()
                # Schedule callback on main thread
                if callback:
                    self.dialog.after(0, lambda: self._handle_completion(callback, True, result))
                else:
                    self.dialog.after(0, self.close)
            except Exception as e:
                # Schedule error callback on main thread
                if callback:
                    self.dialog.after(0, lambda: self._handle_completion(callback, False, str(e)))
                else:
                    self.dialog.after(0, self.close)
                    
        # Start worker thread
        thread = threading.Thread(target=worker, daemon=True)
        thread.start()
        
    def _handle_completion(self, callback, success, result):
        """Handle task completion on main thread."""
        try:
            if success:
                callback(True, result)
            else:
                callback(False, result)
        except Exception as e:
            print(f"Error in callback: {e}")
        finally:
            self.close()

class SimpleProgressDialog:
    """Simplified progress dialog for basic use cases."""
    
    def __init__(self, parent, title="Processing", message="Please wait..."):
        """Initialize simple progress dialog."""
        self.parent = parent
        self.title = title
        self.message = message
        self.dialog = None
        
    def __enter__(self):
        """Context manager entry."""
        self.show()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
        
    def show(self):
        """Show the dialog."""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title(self.title)
        self.dialog.geometry("250x100")
        self.dialog.resizable(False, False)
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        # Center dialog
        self.dialog.update_idletasks()
        x = self.parent.winfo_x() + (self.parent.winfo_width() - self.dialog.winfo_width()) // 2
        y = self.parent.winfo_y() + (self.parent.winfo_height() - self.dialog.winfo_height()) // 2
        self.dialog.geometry(f"+{x}+{y}")
        
        # Create widgets
        frame = ttk.Frame(self.dialog, padding="20")
        frame.pack(expand=True, fill='both')
        
        ttk.Label(frame, text=self.message).pack(pady=(0, 10))
        
        progress = ttk.Progressbar(frame, mode='indeterminate', length=200)
        progress.pack()
        progress.start()
        
        # Prevent closing
        self.dialog.protocol("WM_DELETE_WINDOW", lambda: None)
        
        # Update display
        self.dialog.update()
        
    def close(self):
        """Close the dialog."""
        if self.dialog and self.dialog.winfo_exists():
            self.dialog.destroy()