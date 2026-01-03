#!/usr/bin/env python3
"""
AI-Powered PDF Organizer - GUI Version
Easy-to-use interface for organizing PDFs
"""

import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext, messagebox
import threading
import os
from pathlib import Path
from pdf_organizer import PDFOrganizer

class PDFOrganizerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("AI PDF Organizer")
        self.root.geometry("800x700")
        
        # Variables
        self.downloads_path = tk.StringVar()
        self.ebooks_path = tk.StringVar()
        self.api_key = tk.StringVar()
        self.dry_run = tk.BooleanVar(value=True)
        
        # Auto-detect Downloads folder for current user
        self.auto_downloads_path = str(Path.home() / "Downloads")
        
        # Load saved settings
        self.load_settings()
        
        # Set Downloads to auto-detected path if not already set
        if not self.downloads_path.get():
            self.downloads_path.set(self.auto_downloads_path)
        
        self.create_widgets()
        
    def create_widgets(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Title
        title = ttk.Label(main_frame, text="AI-Powered PDF Organizer", 
                         font=('Arial', 16, 'bold'))
        title.grid(row=0, column=0, columnspan=3, pady=10)
        
        # Downloads folder
        ttk.Label(main_frame, text="Downloads Folder:").grid(row=1, column=0, sticky=tk.W, pady=5)
        downloads_entry = ttk.Entry(main_frame, textvariable=self.downloads_path, width=50)
        downloads_entry.grid(row=1, column=1, pady=5)
        ttk.Button(main_frame, text="Browse", 
                  command=self.browse_downloads).grid(row=1, column=2, padx=5, pady=5)
        
        # Auto-detected info
        auto_label = ttk.Label(main_frame, text=f"Auto-detected: {self.auto_downloads_path}", 
                              font=('Arial', 8), foreground='gray')
        auto_label.grid(row=2, column=1, sticky=tk.W)
        
        # Ebooks folder
        ttk.Label(main_frame, text="Ebooks Folder:").grid(row=3, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.ebooks_path, width=50).grid(row=3, column=1, pady=5)
        ttk.Button(main_frame, text="Browse", 
                  command=self.browse_ebooks).grid(row=3, column=2, padx=5, pady=5)
        
        # API Key
        ttk.Label(main_frame, text="Anthropic API Key:").grid(row=4, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.api_key, width=50, 
                 show="*").grid(row=4, column=1, pady=5)
        ttk.Button(main_frame, text="Show/Hide", 
                  command=self.toggle_api_key).grid(row=4, column=2, padx=5, pady=5)
        
        # Options
        options_frame = ttk.LabelFrame(main_frame, text="Options", padding="10")
        options_frame.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        
        ttk.Checkbutton(options_frame, text="Dry Run (preview only, don't move files)", 
                       variable=self.dry_run).grid(row=0, column=0, sticky=tk.W)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=6, column=0, columnspan=3, pady=10)
        
        ttk.Button(button_frame, text="Organize PDFs", 
                  command=self.run_organizer, style='Accent.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Save Settings", 
                  command=self.save_settings).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="View Log", 
                  command=self.view_log).pack(side=tk.LEFT, padx=5)
        
        # Progress
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.grid(row=7, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        # Log output
        log_frame = ttk.LabelFrame(main_frame, text="Activity Log", padding="5")
        log_frame.grid(row=8, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=20, width=90)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(8, weight=1)
        
    def browse_downloads(self):
        folder = filedialog.askdirectory(title="Select Downloads Folder")
        if folder:
            self.downloads_path.set(folder)
            
    def browse_ebooks(self):
        folder = filedialog.askdirectory(title="Select Ebooks Folder")
        if folder:
            self.ebooks_path.set(folder)
            
    def toggle_api_key(self):
        # Toggle between show and hide
        current_show = self.log_text.winfo_children()[0].cget('show') if hasattr(self, 'api_entry') else '*'
        # Find the entry widget and toggle
        for widget in self.root.winfo_children()[0].winfo_children():
            if isinstance(widget, ttk.Entry) and widget.cget('show') == '*':
                widget.configure(show='')
                return
            elif isinstance(widget, ttk.Entry) and widget.cget('show') == '':
                widget.configure(show='*')
                return
    
    def log(self, message):
        """Add message to log"""
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.root.update()
        
    def run_organizer(self):
        """Run the PDF organizer"""
        # Validate inputs
        if not self.downloads_path.get() or self.downloads_path.get().strip() == '':
            messagebox.showerror("Error", "Please select Downloads folder.\n\nThe Downloads folder is where your PDFs are currently located.")
            return
        if not self.ebooks_path.get() or self.ebooks_path.get().strip() == '':
            messagebox.showerror("Error", "Please select Ebooks folder.\n\nThe Ebooks folder is where PDFs will be organized (e.g., F:\\ebooks)")
            return
        if not self.api_key.get() or self.api_key.get().strip() == '':
            messagebox.showerror("Error", "Please enter your Anthropic API key.\n\nGet one at: https://console.anthropic.com/")
            return
            
        # Clear log
        self.log_text.delete(1.0, tk.END)
        
        # Start progress
        self.progress.start()
        
        # Run in separate thread
        thread = threading.Thread(target=self._organize_thread)
        thread.daemon = True
        thread.start()
        
    def _organize_thread(self):
        """Thread to run organizer"""
        try:
            self.log("Starting PDF organization...\n")
            
            # Create organizer
            organizer = PDFOrganizer(
                downloads_folder=self.downloads_path.get(),
                ebooks_folder=self.ebooks_path.get(),
                api_key=self.api_key.get(),
                dry_run=self.dry_run.get()
            )
            
            # Redirect output to log
            import sys
            from io import StringIO
            
            old_stdout = sys.stdout
            sys.stdout = StringIO()
            
            try:
                # Run organizer
                results = organizer.organize_pdfs(confirm=False)
                
                # Get captured output
                output = sys.stdout.getvalue()
                sys.stdout = old_stdout
                
                self.log(output)
                
                if results:
                    if self.dry_run.get():
                        self.log("\n✅ Dry run complete! No files were moved.")
                        self.log("Uncheck 'Dry Run' to actually move files.")
                    else:
                        self.log(f"\n✅ Successfully organized {len(results)} PDFs!")
                else:
                    self.log("\nNo PDFs to organize.")
                    
            finally:
                sys.stdout = old_stdout
                
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            self.log(f"\n❌ Error: {str(e)}")
            self.log(f"\nFull error details:\n{error_details}")
            messagebox.showerror("Error", f"Organization failed:\n\n{str(e)}\n\nCheck the activity log for full details.")
        finally:
            self.progress.stop()
            
    def save_settings(self):
        """Save settings to file"""
        settings = {
            'downloads_path': self.downloads_path.get(),
            'ebooks_path': self.ebooks_path.get(),
            'api_key': self.api_key.get()
        }
        
        import json
        settings_file = Path.home() / '.pdf_organizer_settings.json'
        with open(settings_file, 'w') as f:
            json.dump(settings, f)
            
        messagebox.showinfo("Success", "Settings saved!")
        
    def load_settings(self):
        """Load settings from file"""
        import json
        settings_file = Path.home() / '.pdf_organizer_settings.json'
        
        if settings_file.exists():
            try:
                with open(settings_file, 'r') as f:
                    settings = json.load(f)
                    self.downloads_path.set(settings.get('downloads_path', ''))
                    self.ebooks_path.set(settings.get('ebooks_path', ''))
                    self.api_key.set(settings.get('api_key', ''))
            except:
                pass
                
    def view_log(self):
        """Open the organization log file"""
        log_file = Path(self.ebooks_path.get()) / 'organization_log.json'
        if log_file.exists():
            import json
            with open(log_file, 'r') as f:
                log_data = json.load(f)
            
            # Show in new window
            log_window = tk.Toplevel(self.root)
            log_window.title("Organization Log")
            log_window.geometry("600x400")
            
            text = scrolledtext.ScrolledText(log_window, width=70, height=20)
            text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            text.insert(1.0, json.dumps(log_data, indent=2))
            text.configure(state='disabled')
        else:
            messagebox.showinfo("No Log", "No organization log found yet.")


def main():
    root = tk.Tk()
    app = PDFOrganizerGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
