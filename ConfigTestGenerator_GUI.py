#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ConfigTestGenerator_GUI.py
--------------------------
Modern GUI application for generating .hwtp configs and tests from Excel.

Features:
- Import Excel file
- Generate configs (single + multi-variant)
- Generate tests automatically
- Modern dark theme interface

Author: VRG Team
Date: 2025-01-03
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
import subprocess
import sys
import traceback
import os
from typing import Optional


def get_resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller."""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path, relative_path)


class ModernButton(tk.Canvas):
    """Custom modern button with gradient effect."""
    
    def __init__(self, parent, text, command, bg_color="#2196F3", fg_color="#FFFFFF", 
                 hover_color="#1976D2", width=200, height=45):
        super().__init__(parent, width=width, height=height, highlightthickness=0, bg=parent['bg'])
        
        self.text = text
        self.command = command
        self.bg_color = bg_color
        self.fg_color = fg_color
        self.hover_color = hover_color
        self.width = width
        self.height = height
        
        self.rect = self.create_rectangle(2, 2, width-2, height-2, fill=bg_color, outline="", width=0)
        self.text_id = self.create_text(width//2, height//2, text=text, fill=fg_color, 
                                       font=("Segoe UI", 11, "bold"))
        
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
        self.bind("<Button-1>", self.on_click)
        
    def on_enter(self, e):
        self.itemconfig(self.rect, fill=self.hover_color)
        
    def on_leave(self, e):
        self.itemconfig(self.rect, fill=self.bg_color)
        
    def on_click(self, e):
        if self.command:
            self.command()
            
    def set_enabled(self, enabled: bool):
        if enabled:
            self.itemconfig(self.rect, fill=self.bg_color)
            self.itemconfig(self.text_id, fill=self.fg_color)
            self.bind("<Button-1>", self.on_click)
        else:
            self.itemconfig(self.rect, fill="#424242")
            self.itemconfig(self.text_id, fill="#757575")
            self.unbind("<Button-1>")


class ConfigTestGeneratorGUI:
    """Main GUI application."""
    
    def __init__(self, root):
        self.root = root
        self.root.title("VRG Config & Test Generator")
        self.root.geometry("800x650")
        
        # Set minimum size for usability
        self.root.minsize(700, 550)
        
        # Enable resizing
        self.root.resizable(True, True)
        
        # Set icon
        try:
            icon_path = get_resource_path("VRG_Logo.ico")
            if os.path.exists(icon_path):
                self.root.iconbitmap(icon_path)
        except:
            pass
        
        # Modern dark theme colors
        self.bg_dark = "#1E1E1E"
        self.bg_medium = "#2D2D2D"
        self.bg_light = "#3E3E3E"
        self.accent_blue = "#2196F3"
        self.accent_green = "#4CAF50"
        self.accent_purple = "#9C27B0"
        self.text_color = "#FFFFFF"
        self.text_gray = "#B0B0B0"
        
        # State variables
        self.excel_path: Optional[Path] = None
        self.config_dir: Optional[Path] = None
        
        # Configure root background
        self.root.configure(bg=self.bg_dark)
        
        # Configure grid weights for responsive layout
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
        # Bind resize event for dynamic scaling
        self.root.bind("<Configure>", self.on_resize)
        
        self.create_widgets()
        
    def create_widgets(self):
        """Create all GUI widgets."""
        
        # Header Frame (more compact)
        self.header_frame = tk.Frame(self.root, bg=self.bg_medium, height=80)
        self.header_frame.grid(row=0, column=0, sticky="ew", padx=0, pady=0)
        self.header_frame.grid_propagate(False)
        self.header_frame.grid_columnconfigure(0, weight=1)
        
        # Title
        self.title_label = tk.Label(self.header_frame, text="⚙️ VRG Config & Test Generator",
                              font=("Segoe UI", 18, "bold"), bg=self.bg_medium, fg=self.text_color)
        self.title_label.pack(pady=(15, 3))
        
        # Subtitle
        self.subtitle_label = tk.Label(self.header_frame, text="Universal Hardware Test Generator v4.0",
                                 font=("Segoe UI", 9), bg=self.bg_medium, fg=self.text_gray)
        self.subtitle_label.pack()
        
        # Main content frame with scrollable canvas
        self.content_frame = tk.Frame(self.root, bg=self.bg_dark)
        self.content_frame.grid(row=1, column=0, sticky="nsew", padx=25, pady=15)
        
        # Configure grid weights for responsive sections
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.grid_rowconfigure(0, weight=0)  # Step 1
        self.content_frame.grid_rowconfigure(1, weight=0)  # Excel label
        self.content_frame.grid_rowconfigure(2, weight=0)  # Import button
        self.content_frame.grid_rowconfigure(3, weight=0)  # Step 2
        self.content_frame.grid_rowconfigure(4, weight=0)  # Config label
        self.content_frame.grid_rowconfigure(5, weight=0)  # Config button
        self.content_frame.grid_rowconfigure(6, weight=0)  # Step 3
        self.content_frame.grid_rowconfigure(7, weight=0)  # Test label
        self.content_frame.grid_rowconfigure(8, weight=1)  # Test button (expandable)
        
        # Step 1: Import Excel
        self.create_step_section(self.content_frame, "STEP 1: Import Excel File", 0)
        
        # Excel path display
        self.excel_label = tk.Label(self.content_frame, text="No file selected",
                                   font=("Segoe UI", 9), bg=self.bg_dark, fg=self.text_gray,
                                   anchor="w", wraplength=600, justify="left")
        self.excel_label.grid(row=1, column=0, sticky="ew", pady=(3, 8), padx=30)
        
        # Import button (smaller)
        self.import_btn = ModernButton(self.content_frame, "📁 Select Excel File", self.import_excel,
                                      bg_color=self.accent_blue, width=200, height=38)
        self.import_btn.grid(row=2, column=0, pady=(0, 15), padx=30, sticky="w")
        
        # Step 2: Generate Configs
        self.create_step_section(self.content_frame, "STEP 2: Generate Configurations", 3)
        
        # Config output display
        self.config_label = tk.Label(self.content_frame, text="Configs will be saved to selected directory",
                                    font=("Segoe UI", 9), bg=self.bg_dark, fg=self.text_gray,
                                    anchor="w", wraplength=600, justify="left")
        self.config_label.grid(row=4, column=0, sticky="ew", pady=(3, 8), padx=30)
        
        # Generate config button (smaller)
        self.config_btn = ModernButton(self.content_frame, "⚙️ Generate Configs", self.generate_configs,
                                      bg_color=self.accent_green, width=200, height=38)
        self.config_btn.grid(row=5, column=0, pady=(0, 15), padx=30, sticky="w")
        self.config_btn.set_enabled(False)
        
        # Step 3: Generate Tests
        self.create_step_section(self.content_frame, "STEP 3: Generate Test Menus", 6)
        
        # Test output display
        self.test_label = tk.Label(self.content_frame, text="Tests will be saved next to config files",
                                  font=("Segoe UI", 9), bg=self.bg_dark, fg=self.text_gray,
                                  anchor="w", wraplength=600, justify="left")
        self.test_label.grid(row=7, column=0, sticky="ew", pady=(3, 8), padx=30)
        
        # Generate test button (smaller)
        self.test_btn = ModernButton(self.content_frame, "🧪 Generate Tests", self.generate_tests,
                                     bg_color=self.accent_purple, width=200, height=38)
        self.test_btn.grid(row=8, column=0, pady=(0, 15), padx=30, sticky="nw")
        self.test_btn.set_enabled(False)
        
        # Status bar at bottom (compact)
        self.status_frame = tk.Frame(self.root, bg=self.bg_medium, height=35)
        self.status_frame.grid(row=2, column=0, sticky="ew")
        self.status_frame.grid_propagate(False)
        self.status_frame.grid_columnconfigure(0, weight=1)
        
        self.status_label = tk.Label(self.status_frame, text="Ready", font=("Segoe UI", 9),
                                     bg=self.bg_medium, fg=self.text_gray, anchor="w")
        self.status_label.pack(side=tk.LEFT, padx=20, pady=8)
        
    def create_step_section(self, parent, title, row):
        """Create a step section header."""
        section_frame = tk.Frame(parent, bg=self.bg_light, height=38)
        section_frame.grid(row=row, column=0, sticky="ew", pady=(0, 8))
        section_frame.grid_propagate(False)
        section_frame.grid_columnconfigure(0, weight=1)
        
        label = tk.Label(section_frame, text=title, font=("Segoe UI", 11, "bold"),
                        bg=self.bg_light, fg=self.text_color, anchor="w")
        label.pack(side=tk.LEFT, padx=20, pady=10)
    
    def on_resize(self, event):
        """Handle window resize event for dynamic font scaling."""
        if event.widget == self.root:
            width = event.width
            height = event.height
            
            # Calculate scale factors (base: 800x650)
            scale_x = max(0.8, min(1.5, width / 800))
            scale_y = max(0.8, min(1.5, height / 650))
            scale = (scale_x + scale_y) / 2
            
            # Update title font
            title_size = int(18 * scale)
            self.title_label.config(font=("Segoe UI", title_size, "bold"))
            
            # Update subtitle font
            subtitle_size = int(9 * scale)
            self.subtitle_label.config(font=("Segoe UI", subtitle_size))
            
            # Update wraplength for labels (responsive text wrapping)
            wrap_width = max(500, width - 250)
            self.excel_label.config(wraplength=wrap_width, font=("Segoe UI", int(9 * scale)))
            self.config_label.config(wraplength=wrap_width, font=("Segoe UI", int(9 * scale)))
            self.test_label.config(wraplength=wrap_width, font=("Segoe UI", int(9 * scale)))
            
            # Update status label font
            self.status_label.config(font=("Segoe UI", int(9 * scale)))
        
    def set_status(self, message: str, color: str = None):
        """Update status bar message."""
        self.status_label.config(text=message)
        if color:
            self.status_label.config(fg=color)
        self.root.update()
        
    def import_excel(self):
        """Import Excel file."""
        file_path = filedialog.askopenfilename(
            title="Select Excel File",
            filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
            initialdir=str(Path.cwd())
        )
        
        if not file_path:
            return
            
        self.excel_path = Path(file_path)
        self.excel_label.config(text=f"📄 {self.excel_path.name}", fg=self.accent_blue)
        self.config_btn.set_enabled(True)
        self.set_status(f"Loaded: {self.excel_path.name}", self.accent_green)
        
    def generate_configs(self):
        """Generate configuration files."""
        if not self.excel_path:
            messagebox.showerror("Error", "Please select an Excel file first!")
            return
            
        # Ask for output directory
        output_dir = filedialog.askdirectory(
            title="Select Output Directory for Configs",
            initialdir=str(self.excel_path.parent)
        )
        
        if not output_dir:
            return
            
        self.config_dir = Path(output_dir)
        
        # Update status
        self.set_status("Generating configs...", self.accent_blue)
        self.root.update()
        
        try:
            # Prefer direct import to work inside bundled .exe
            try:
                import GenSymb_ConfigVRG as genconf
            except Exception as imp_err:
                # Fallback: show detailed traceback to help diagnose
                tb = traceback.format_exc()
                raise RuntimeError(f"Failed to import GenSymb_ConfigVRG module.\n\n{tb}") from imp_err

            # Run multi-config generation directly via API
            genconf.generate_multi_configs(str(self.excel_path), str(self.config_dir), base_name="config")

            # Count generated files
            config_files = list(self.config_dir.glob("config*.hwtp"))
            num_configs = len(config_files)

            self.config_label.config(
                text=f"✅ Generated {num_configs} config file(s) in:\n{self.config_dir}",
                fg=self.accent_green
            )
            self.test_btn.set_enabled(True)
            self.set_status(f"Success! Generated {num_configs} configs", self.accent_green)

            messagebox.showinfo(
                "Success",
                f"Successfully generated {num_configs} configuration file(s)!\n\n" +
                f"Location: {self.config_dir}"
            )

        except Exception as e:
            self.set_status("Config generation failed!", "#F44336")
            messagebox.showerror("Error", f"Error generating configs:\n\n{str(e)}")
            
    def generate_tests(self):
        """Generate test menu files."""
        if not self.config_dir:
            messagebox.showerror("Error", "Please generate configs first!")
            return
            
        # Find all config files
        config_files = list(self.config_dir.glob("config_*.hwtp"))
        
        if not config_files:
            messagebox.showerror("Error", "No config files found!\nPlease generate configs first.")
            return
            
        # Update status
        self.set_status("Generating tests...", self.accent_blue)
        self.root.update()
        
        try:
            # Import test generator as a module and call its API
            try:
                import generate_test_menu_v4 as gentest
            except Exception as imp_err:
                tb = traceback.format_exc()
                raise RuntimeError(f"Failed to import generate_test_menu_v4 module.\n\n{tb}") from imp_err

            tests_generated = 0

            for config_file in config_files:
                # Extract variant name (e.g., config_DZC.hwtp -> DZC)
                variant = config_file.stem.replace("config_", "")
                test_file = self.config_dir / f"test_{variant}_v4.hwtp"

                # Parse config and generate menu lines
                groups = gentest.parse_config(config_file)
                lines = gentest.generate_test_menu(groups)

                # Write output file
                with open(test_file, "w", encoding="utf-8") as f:
                    f.write("\n".join(lines))

                tests_generated += 1

            if tests_generated > 0:
                self.test_label.config(
                    text=f"✅ Generated {tests_generated} test file(s) in:\n{self.config_dir}",
                    fg=self.accent_green
                )
                self.set_status(f"Success! Generated {tests_generated} tests", self.accent_green)

                messagebox.showinfo(
                    "Success",
                    f"Successfully generated {tests_generated} test menu file(s)!\n\n" +
                    f"Location: {self.config_dir}"
                )
            else:
                self.set_status("No tests generated!", "#F44336")
                messagebox.showwarning("Warning", "No tests were generated. Check config files.")

        except Exception as e:
            self.set_status("Test generation failed!", "#F44336")
            messagebox.showerror("Error", f"Error generating tests:\n\n{str(e)}")


def main():
    """Main entry point."""
    root = tk.Tk()
    app = ConfigTestGeneratorGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
