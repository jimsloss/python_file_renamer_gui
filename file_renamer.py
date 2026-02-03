import os
import re
import json
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from pathlib import Path
from typing import List, Tuple, Dict
from datetime import datetime

class RegexFileRenamerGUI:
    """A GUI-based regex file renamer with validation and safety features."""
    
    ILLEGAL_CHARS_WIN = r'[<>:"/\\|?*]'
    
    # Color scheme - Professional palette
    HEADER_BG = "#1a3a52"  # Deep navy blue
    HEADER_FG = "#ffffff"  # Pure white
    PRIMARY_COLOR = "#1a3a52"  # Deep navy blue (matches header background)
    SECONDARY_COLOR = "#f0f4f8"  # Light blue-gray
    BG_COLOR = "#eceff5"  # Soft blue-gray background
    ACCENT_COLOR = "#00a86b"  # Professional green
    TEXT_COLOR = "#1a3a52"  # Deep navy for text
    BORDER_COLOR = "#d4dce6"  # Soft gray
    SUCCESS_COLOR = "#00a86b"  # Professional green
    ERROR_COLOR = "#cc0000"  # Professional red
    WARNING_COLOR = "#ff9900"  # Professional orange
    
    def __init__(self, root):
        self.root = root
        self.root.title("File Renamer")
        self.root.geometry("1000x900")
        self.root.resizable(True, True)
        
        # Set window background
        self.root.configure(bg=self.HEADER_BG)
        
        # Configure style
        self.setup_styles()
        
        self.rename_log = []
        self.current_changes = []
        self.current_collisions = {}
        
        # Predefined patterns for non-programmers
        self.patterns = {
            "Replace Spaces with Underscores": {
                "pattern": r" ",
                "description": "Convert spaces to underscores",
                "label": "Replace spaces with underscores"
            },
            "Replace Spaces with Hyphens": {
                "pattern": r" ",
                "description": "Convert spaces to hyphens",
                "label": "Replace spaces with hyphens"
            },
            "Remove Numbers": {
                "pattern": r"\d+",
                "description": "Delete all numbers from filenames",
                "label": "Remove numbers"
            },
            "Remove Special Characters": {
                "pattern": r"[^a-zA-Z0-9._\-\s]",
                "description": "Keep only letters, numbers, spaces, dots, hyphens",
                "label": "Remove special characters"
            },
            "Extract Numbers Only": {
                "pattern": r"[^\d]",
                "description": "Keep only numbers",
                "label": "Keep numbers only"
            },
            "Add Prefix": {
                "pattern": "^",
                "description": "Add text at the start",
                "label": "Add prefix"
            },
            "Add Suffix Before Extension": {
                "pattern": r"(.*)(\.[\w]+)$",
                "description": "Insert text before extension",
                "label": "Add suffix"
            },
            "Remove Extra Spaces": {
                "pattern": r"\s+",
                "description": "Replace multiple spaces",
                "label": "Remove extra spaces"
            },
            "Convert to Lowercase": {
                "pattern": r"(.*)",
                "description": "Make lowercase",
                "label": "Convert to lowercase"
            },
            "Convert to Uppercase": {
                "pattern": r"(.*)",
                "description": "Make uppercase",
                "label": "Convert to uppercase"
            },
            "Camel Case": {
                "pattern": r"(.*)",
                "description": "Convert to camelCase",
                "label": "Convert to camelCase"
            },
            "Remove Text": {
                "type": "remove_text",
                "description": "Remove specific text",
                "label": "Remove text"
            },
            "Replace Text": {
                "type": "replace_text",
                "description": "Find and replace text",
                "label": "Replace text"
            }
        }

        self.setup_ui()
    
    def setup_styles(self):
        """Configure custom ttk styles for modern look."""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure label styles
        style.configure('TLabel', font=('Segoe UI', 11), background=self.BG_COLOR, foreground=self.TEXT_COLOR)
        style.configure('Header.TLabel', font=('Segoe UI', 12, 'bold'), background=self.BG_COLOR, foreground=self.PRIMARY_COLOR)
        style.configure('Title.TLabel', font=('Segoe UI', 28, 'bold'), background=self.HEADER_BG, foreground=self.HEADER_FG)
        
        # Configure button styles
        style.configure('TButton', font=('Segoe UI', 11, 'bold'), relief='raised', borderwidth=4, background=self.PRIMARY_COLOR, foreground='white', padding=8)
        style.map(
            'TButton',
            background=[
                ('disabled', '#bfc7d1'),   # light grey-blue
                ('active', '#4a7ba7'),
                ('pressed', '#0a1520')
            ],
            foreground=[
                ('disabled', '#6d7885'),   # muted grey text
                ('active', 'white'),
                ('pressed', 'white')
            ],
            relief=[
                ('disabled', 'flat'),
                ('pressed', 'sunken'),
                ('active', 'raised')
            ]
        )
        
        # Configure frame styles
        style.configure('TFrame', background=self.BG_COLOR)
        style.configure('Content.TFrame', background=self.BG_COLOR, relief='solid', borderwidth=2)
        style.configure('Header.TFrame', background=self.HEADER_BG)
        
        style.configure(
            'Pattern.TLabelframe',
            background=self.BG_COLOR,
            borderwidth=3,
            relief='ridge'
        )

        style.configure(
            'Pattern.TLabelframe.Label',
            background=self.BG_COLOR,
            foreground=self.PRIMARY_COLOR,
            font=('Segoe UI', 12, 'bold')
        )

        # Configure entry styles
        style.configure('TEntry', font=('Segoe UI', 11), padding=5, fieldbackground='white', foreground=self.TEXT_COLOR)
        
        # Configure radiobutton styles
        style.configure('TRadiobutton', font=('Segoe UI', 13), background=self.BG_COLOR, foreground=self.TEXT_COLOR)
        
        # Configure labelframe
        style.configure('TLabelframe', font=('Segoe UI', 12, 'bold'), background=self.BG_COLOR, foreground=self.PRIMARY_COLOR)
        style.configure('TLabelframe.Label', background=self.BG_COLOR, foreground=self.PRIMARY_COLOR)
        
        # Configure scrollbar styles
        style.configure('Vertical.TScrollbar', background=self.SECONDARY_COLOR, troughcolor=self.BG_COLOR, borderwidth=2)
        style.map('Vertical.TScrollbar', 
                  background=[('active', self.PRIMARY_COLOR)])
    
    def setup_ui(self):
        """Create the GUI layout with modern styling."""
        # Create header frame
        header_frame = ttk.Frame(self.root, style='Header.TFrame')
        header_frame.pack(fill=tk.X, side=tk.TOP)
        header_frame.configure(height=100, relief='flat')
        
        # Title with padding
        title_label = ttk.Label(header_frame, text="File Renamer", style='Title.TLabel')
        title_label.pack(pady=20, padx=20)
        
        # Main content frame with scrollable canvas
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Create canvas and scrollbar
        canvas = tk.Canvas(main_frame, bg=self.BG_COLOR, highlightthickness=0)
        scrollbar = ttk.Scrollbar(main_frame, orient='vertical', command=canvas.yview)
        
        # Create scrollable frame inside canvas
        scrollable_frame = ttk.Frame(canvas)
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="n")
        canvas.configure(yscrollcommand=scrollbar.set)

        def _on_canvas_resize(event):
            canvas.itemconfig(window_id, width=event.width)

        window_id = canvas.create_window((0, 0), window=scrollable_frame, anchor="n")
        canvas.bind("<Configure>", _on_canvas_resize)

        # Pack canvas and scrollbar
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind mousewheel to canvas
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        # Add internal padding to the scrollable frame
        inner_frame = ttk.Frame(scrollable_frame)
        inner_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Configure grid weights for resizing
        inner_frame.columnconfigure(0, weight=1)
        
        # --- APP DESCRIPTION ---
        description_text = "Easily rename multiple files at once.\nChoose a renaming option below, preview your changes, and apply them safely."
        ttk.Label(inner_frame, text=description_text, font=('Segoe UI', 11), foreground=self.TEXT_COLOR, wraplength=900, justify='center', anchor='center').grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 20))
        
        # --- DIRECTORY SECTION ---
        ttk.Label(inner_frame, text="📁 Directory to Scan", style='Header.TLabel').grid(row=1, column=0, sticky=tk.W, pady=(0, 10))
        
        dir_frame = ttk.Frame(inner_frame)
        dir_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 20))
        dir_frame.columnconfigure(0, weight=1)
        
        self.dir_var = tk.StringVar()
        self.dir_var.trace_add("write", self.invalidate_preview)
        self.dir_entry = ttk.Entry(dir_frame, textvariable=self.dir_var)
        self.dir_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 10), ipady=8)
        
        ttk.Button(dir_frame, text="Browse...", command=self.browse_directory, width=15).grid(row=0, column=1)
        
        # --- PATTERN SELECTION SECTION ---
        ttk.Label(inner_frame, text="🔍 Renaming Option", style='Header.TLabel').grid(row=3, column=0, sticky=tk.W, pady=(10, 10))
        
        pattern_frame = ttk.LabelFrame(inner_frame,  style='Pattern.TLabelframe', padding="15", text ="")
        pattern_frame.grid(row=4, column=0, sticky=(tk.W, tk.E), pady=(0, 20))
        pattern_frame.columnconfigure(0, weight=1)
        pattern_frame.columnconfigure(1, weight=1)
        
        
        self.pattern_var = tk.StringVar(value="Replace Spaces with Underscores")
        
        # Create two-column layout for radio buttons
        row = 0
        col = 0

        for pattern_name, pattern_info in self.patterns.items():
            text = pattern_info.get("label", pattern_name)

            rb = ttk.Radiobutton(
                pattern_frame,
                text=text,
                variable=self.pattern_var,
                value=pattern_name,
                command=self.on_pattern_selected
            )
            rb.grid(row=row, column=col, sticky=tk.W, pady=5, padx=(0, 10))

            col += 1
            if col > 1:
                col = 0
                row += 1
     
        # --- REPLACEMENT SECTION (side-by-side layout) ---
        self.replacement_row = row + 1  # remember where this section lives

        self.replacement_frame = ttk.Frame(inner_frame)
        self.replacement_frame.grid(row=self.replacement_row, column=0, sticky=(tk.W, tk.E), pady=(10, 10))
        self.replacement_frame.columnconfigure(0, weight=1)
        self.replacement_frame.columnconfigure(1, weight=1)

        # First label + entry
        self.replacement_label = ttk.Label(self.replacement_frame, text="✏️  Replacement Text", style='Header.TLabel')
        self.replacement_label.grid(row=0, column=0, sticky=tk.W, padx=(0, 10))

        self.replacement_var = tk.StringVar()
        self.replacement_entry = ttk.Entry(self.replacement_frame, textvariable=self.replacement_var)
        self.replacement_entry.grid(row=1, column=0, sticky=(tk.W, tk.E), ipady=8, padx=(0, 10))

        # Second label + entry
        self.replace_with_label = ttk.Label(self.replacement_frame, text="✏️  Replace With", style='Header.TLabel')
        self.replace_with_label.grid(row=0, column=1, sticky=tk.W)

        self.replace_with_var = tk.StringVar()
        self.replace_with_entry = ttk.Entry(self.replacement_frame, textvariable=self.replace_with_var)
        self.replace_with_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), ipady=8)

        self.replacement_var.trace_add("write", self.invalidate_preview)
        self.replace_with_var.trace_add("write", self.invalidate_preview)

        # start hidden
        self.replacement_frame.grid_remove()
       
        # Initialize example display
        self.on_pattern_selected()
        
        
        # --- BUTTONS SECTION ---
        button_frame = ttk.Frame(inner_frame)
        button_frame.grid(row=10, column=0, sticky=(tk.W, tk.E), pady=(0, 20))
        button_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(1, weight=1)
        button_frame.columnconfigure(2, weight=1)
        
        ttk.Button(
            button_frame,
            text="🔍 Preview Changes",
            command=self.preview_changes,
            width=20
        ).grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 10), ipady=10)

        self.rename_button = ttk.Button(
            button_frame,
            text="✅ Rename Files",
            command=self.rename_files,
            width=20,
            state="disabled"  # start disabled
        )
        self.rename_button.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10), ipady=10)

        ttk.Button(
            button_frame,
            text="🗑️  Clear Output",
            command=self.clear_output,
            width=20
        ).grid(row=0, column=2, sticky=(tk.W, tk.E), ipady=10)

        # --- OUTPUT SECTION ---
        ttk.Label(inner_frame, text="📋 Output", style='Header.TLabel').grid(row=11, column=0, sticky=tk.W, pady=(10, 10))
        
        # Create output frame with visible scrollbar
        output_frame = ttk.Frame(inner_frame)
        output_frame.grid(row=12, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        output_frame.columnconfigure(0, weight=1)
        output_frame.rowconfigure(0, weight=1)
        
        self.output_text = scrolledtext.ScrolledText(output_frame, height=14, width=100, wrap=tk.WORD, font=('Courier New', 11))
        self.output_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure text tags for colors
        self.output_text.tag_config("success", foreground=self.SUCCESS_COLOR, font=('Courier New', 11, 'bold'))
        self.output_text.tag_config("error", foreground=self.ERROR_COLOR, font=('Courier New', 11, 'bold'))
        self.output_text.tag_config("warning", foreground=self.WARNING_COLOR, font=('Courier New', 11))
        self.output_text.tag_config("info", foreground=self.PRIMARY_COLOR, font=('Courier New', 11))
        self.output_text.tag_config("header", foreground=self.HEADER_BG, font=('Courier New', 12, 'bold'))
   
    def on_pattern_selected(self):
        self.invalidate_preview()

        selected = self.pattern_var.get()

        # Hide everything by default
        self.replacement_frame.grid_remove()
        self.replacement_label.grid_forget()
        self.replacement_entry.grid_forget()
        self.replace_with_label.grid_forget()
        self.replace_with_entry.grid_forget()

        if selected == "Remove Text":
            self.replacement_label.config(text="✏️  Text to Remove")
            self.replacement_var.set("")
            self.replacement_frame.grid(row=self.replacement_row, column=0, sticky=(tk.W, tk.E), pady=(10, 10))
            self.replacement_label.grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
            self.replacement_entry.grid(row=1, column=0, sticky=(tk.W, tk.E), ipady=8, padx=(0, 10))

        elif selected == "Replace Text":
            self.replacement_label.config(text="✏️  Text to Find")
            self.replacement_var.set("")
            self.replace_with_var.set("")
            self.replacement_frame.grid(row=self.replacement_row, column=0, sticky=(tk.W, tk.E), pady=(10, 10))

            self.replacement_label.grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
            self.replacement_entry.grid(row=1, column=0, sticky=(tk.W, tk.E), ipady=8, padx=(0, 10))

            self.replace_with_label.grid(row=0, column=1, sticky=tk.W)
            self.replace_with_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), ipady=8)
            
        elif selected == "Add Prefix":
            self.replacement_label.config(text="✏️  Prefix to Add")
            self.replacement_var.set("")
            self.replacement_frame.grid(row=self.replacement_row, column=0, sticky=(tk.W, tk.E), pady=(10, 10))
            self.replacement_label.grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
            self.replacement_entry.grid(row=1, column=0, sticky=(tk.W, tk.E), ipady=8, padx=(0, 10))

        elif selected == "Add Suffix Before Extension":
            self.replacement_label.config(text="✏️  Suffix to Add")
            self.replacement_var.set("")
            self.replacement_frame.grid(row=self.replacement_row, column=0, sticky=(tk.W, tk.E), pady=(10, 10))
            self.replacement_label.grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
            self.replacement_entry.grid(row=1, column=0, sticky=(tk.W, tk.E), ipady=8, padx=(0, 10))

    def log_output(self, text, tag="info"):
        """Add text to the output area."""
        self.output_text.insert(tk.END, text + "\n", tag)
        self.output_text.see(tk.END)
        self.root.update()
    
    def clear_output(self):
        """Clear the output text area."""
        self.output_text.delete(1.0, tk.END)
    
    def browse_directory(self):
        """Open directory browser dialog."""
        dir_path = filedialog.askdirectory(title="Select Directory to Scan")
        if dir_path:
            self.dir_var.set(dir_path)
            self.invalidate_preview()

    
    def show_examples(self):
        """Display pattern examples in the output area."""
        self.clear_output()
        self.log_output("=" * 60, "header")
        self.log_output("COMMON PATTERN EXAMPLES", "header")
        self.log_output("=" * 60 + "\n", "header")
        
        examples = [
            ("Replace 'old' with 'new'", "old", "new", "file_old.txt → file_new.txt"),
            ("Remove 'backup_' prefix", "^backup_", "", "backup_photo.jpg → photo.jpg"),
            ("Add '_final' before extension", r"(.*)(\..\w+)$", r"\1_final\2", "document.pdf → document_final.pdf"),
            ("Rearrange date (2024-01-15 → 15-01-2024)", r"(\d{4})-(\d{2})-(\d{2})", r"\3-\2-\1", "2024-01-15.txt → 15-01-2024.txt"),
            ("Capture numbers in brackets", r"(\d+)", r"[\1]", "photo123.jpg → photo[123].jpg"),
        ]
        
        for name, pattern, replacement, example in examples:
            self.log_output(f"📋 {name}:", "info")
            self.log_output(f"   Pattern:     {pattern}")
            self.log_output(f"   Replacement: {replacement if replacement else '(leave blank - deletes match)'}")
            self.log_output(f"   Example:     {example}\n")
    
    def is_valid_filename(self, filename: str) -> bool:
        """Check if filename contains illegal Windows characters."""
        return not re.search(self.ILLEGAL_CHARS_WIN, filename)
    
    def collect_files(self, dir_path: str, recursive: bool) -> List[str]:
        files = []
        for filename in os.listdir(dir_path):
            full_path = os.path.join(dir_path, filename)
            if os.path.isfile(full_path):
                files.append(full_path)
        return sorted(files)
 
    def apply_regex(self, files: List[str], pattern: str, replacement: str, flags: int) -> List[Tuple[str, str, str]]:
        """Apply regex pattern and generate new filenames (regex-based patterns only)."""
        changes = []

        for full_path in files:
            old_name = os.path.basename(full_path)

            # Only apply regex if pattern matches
            if re.search(pattern, old_name, flags):
                new_name = re.sub(pattern, replacement, old_name, flags=flags)

                # Validate new filename
                if not self.is_valid_filename(new_name):
                    self.log_output(f"⚠️  Skipping {old_name}: new name contains illegal characters", "warning")
                    continue

                # Skip if no change
                if new_name == old_name:
                    continue

                changes.append((full_path, old_name, new_name))

        return changes

    def detect_collisions(self, changes: List[Tuple[str, str, str]]) -> Dict[str, List[str]]:
        """Detect files that would map to the same new name."""
        collisions = {}
        new_names = {}
        
        for full_path, old_name, new_name in changes:
            dir_path = os.path.dirname(full_path)
            key = os.path.join(dir_path, new_name)
            
            if key not in new_names:
                new_names[key] = []
            new_names[key].append(old_name)
        
        for key, old_names in new_names.items():
            if len(old_names) > 1:
                collisions[key] = old_names
        
        return collisions
    
    def preview_changes(self):
        """Preview the changes without making them."""
        self.clear_output()

        # Validate directory
        dir_path = self.dir_var.get().strip()
        if not dir_path or not os.path.isdir(dir_path):
            messagebox.showerror("Error", "Please select a valid directory")
            return

        selected_pattern = self.pattern_var.get()
        pattern_info = self.patterns[selected_pattern]

        transform_mode = None
        pattern = None
        replacement = None

        # -------------------------------
        # BUILD PATTERN + REPLACEMENT
        # -------------------------------
        if selected_pattern == "Remove Text":
            pattern = re.escape(self.replacement_var.get().strip())
            replacement = ""

        elif selected_pattern == "Replace Text":
            pattern = re.escape(self.replacement_var.get().strip())
            replacement = self.replace_with_var.get().strip()

        elif selected_pattern == "Add Prefix":
            pattern = r"^(.*)$"
            replacement = self.replacement_var.get().strip() + r"\1"

        elif selected_pattern == "Add Suffix Before Extension":
            pattern = r"^(.*?)(\.[\w]+)$"
            replacement = r"\1" + self.replacement_var.get().strip() + r"\2"

        elif selected_pattern == "Replace Spaces with Underscores":
            pattern = r"\s+"
            replacement = "_"

        elif selected_pattern == "Replace Spaces with Hyphens":
            pattern = r"\s+"
            replacement = "-"

        elif selected_pattern == "Remove Numbers":
            pattern = r"\d+"
            replacement = ""

        # -------------------------------
        # CASE CONVERSION OPTIONS
        # -------------------------------
        elif selected_pattern == "Convert to Uppercase":
            transform_mode = "upper"

        elif selected_pattern == "Convert to Lowercase":
            transform_mode = "lower"

        elif selected_pattern == "Camel Case":
            transform_mode = "camel"

        else:
            pattern = pattern_info.get("pattern", "")
            replacement = ""

        # -------------------------------
        # COLLECT FILES
        # -------------------------------
        files = self.collect_files(dir_path, recursive=False)
        if not files:
            self.log_output("ℹ️ This folder doesn’t contain any files that can be renamed.\n", "warning")
            self.log_output("Choose a different folder and try Preview again.\n", "info")
            self.rename_button.config(state="disabled")
            return

        self.log_output(f"✓ Found {len(files)} file(s)\n", "success")

        # -------------------------------
        # APPLY CASE CONVERSION
        # -------------------------------
        if transform_mode:
            self.current_changes = []

            for full_path in files:
                old_name = os.path.basename(full_path)
                name, ext = os.path.splitext(old_name)

                if transform_mode == "upper":
                    new_stem = name.upper()
                elif transform_mode == "lower":
                    new_stem = name.lower()
                elif transform_mode == "camel":
                    new_stem = " ".join(part.capitalize() for part in name.split())

                new_name = new_stem + ext

                if new_name != old_name:
                    self.current_changes.append((full_path, old_name, new_name))

        # -------------------------------
        # APPLY REGEX PATTERNS
        # -------------------------------
        else:
            try:
                flags = 0
                re.compile(pattern)
            except re.error as e:
                messagebox.showerror("Regex Error", f"Invalid pattern: {e}")
                return

            self.current_changes = self.apply_regex(files, pattern, replacement, flags)

            # Special case: Replace Spaces options
            if selected_pattern in ["Replace Spaces with Underscores", "Replace Spaces with Hyphens"]:
                if not any(" " in os.path.basename(f) for f in files):
                    self.log_output("ℹ️ None of the filenames contain any spaces.\n", "warning")
                    self.log_output("There’s nothing to replace. Try choosing a different option or selecting another folder.\n", "info")
                    self.rename_button.config(state="disabled")
                    return

        # -------------------------------
        # NO CHANGES
        # -------------------------------
        if not self.current_changes:
            self.log_output("ℹ️ None of the files in this folder match your chosen option.\n", "warning")
            self.log_output("Try adjusting your renaming option or the text you entered, then preview again.\n", "info")
            self.rename_button.config(state="disabled")
            return

        # -------------------------------
        # COLLISION DETECTION
        # -------------------------------
        self.current_collisions = self.detect_collisions(self.current_changes)

        if self.current_collisions:
            self.log_output("\n⚠️ Some files would end up with the same name.\n", "error")
            self.log_output("To keep your files safe, the renaming has been stopped.\n", "error")

            for new_path, old_names in self.current_collisions.items():
                target = os.path.basename(new_path)
                self.log_output(f"These files would all become: {target}", "error")
                for old_name in old_names:
                    self.log_output(f"  - {old_name}", "error")
                self.log_output("", "error")

            self.log_output("Please adjust your renaming option or text and try Preview again.\n", "error")
            self.rename_button.config(state="disabled")
            return

        # -------------------------------
        # DISPLAY PREVIEW
        # -------------------------------
        self.log_output("=" * 60, "header")
        self.log_output(f"PREVIEW: {len(self.current_changes)} file(s) will be renamed", "header")
        self.log_output("=" * 60 + "\n", "header")

        for full_path, old_name, new_name in self.current_changes:
            self.log_output(f"  {old_name:40} → {new_name}")

        self.rename_button.config(state="normal")
       
       
            
    def rename_files(self):
        """Execute the rename operation."""
        if not self.current_changes:
            messagebox.showwarning("No Changes", "Please click 'Preview Changes' first")
            return
        
        if self.current_collisions:
            messagebox.showerror("Collisions Detected", "Cannot rename: collisions detected in preview")
            return
        
        
        # Confirm before proceeding
        if messagebox.askyesno("Confirm Rename", f"Rename {len(self.current_changes)} file(s)?"):
            self.clear_output()
            self.log_output("=" * 60, "header")
            self.log_output("RENAMING FILES...", "header")
            self.log_output("=" * 60 + "\n", "header")
            
            success_count = 0
            fail_count = 0
            
            for full_path, old_name, new_name in self.current_changes:
                dir_path = os.path.dirname(full_path)
                new_path = os.path.join(dir_path, new_name)
                
                try:
                    os.rename(full_path, new_path)
                    self.log_output(f"✓ {old_name} → {new_name}", "success")
                    self.rename_log.append({
                        'old_name': old_name,
                        'new_name': new_name,
                        'timestamp': datetime.now().isoformat()
                    })
                    success_count += 1
                except Exception as e:
                    self.log_output(f"❌ {old_name}: {str(e)}", "error")
                    fail_count += 1
            
           # Friendly summary
            if fail_count == 0:
                self.log_output("\n🎉 All files were renamed successfully.\n", "success")
            else:
                self.log_output("\n⚠️ Some files could not be renamed.\n", "warning")
                self.log_output(f"{success_count} file(s) updated successfully.", "info")
                self.log_output(f"{fail_count} file(s) could not be changed.\n", "error")
                
            if success_count > 0:
                self.save_rollback_log(dir_path)

            # Show confirmation
            if fail_count == 0:
                messagebox.showinfo("Renaming Complete", "All files were renamed successfully.")
            else:
                messagebox.showinfo("Renaming Finished", "Some files could not be renamed. Check the output for details.")
            
            # Clear output and reset state
            self.clear_output()
            self.current_changes = []
            self.current_collisions = {}
            self.rename_button.config(state="disabled")

    
    def save_rollback_log(self, dir_path: str) -> None:
        """Save a JSON log for potential rollback."""
        log_file = os.path.join(dir_path, f".rename_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        try:
            with open(log_file, 'w') as f:
                json.dump(self.rename_log, f, indent=2)
            self.log_output(f"📝 Rollback log saved: {log_file}", "info")
        except Exception as e:
            self.log_output(f"⚠️  Could not save rollback log: {e}", "warning")

    def invalidate_preview(self, *args):
        """Disable rename button and clear preview when it becomes invalid."""
        if hasattr(self, "rename_button"):
            self.rename_button.config(state="disabled")

        # Clear preview output if it exists
        if hasattr(self, "output_text"):
            self.clear_output()

        self.current_changes = []
        self.current_collisions = {}
        
        
def main():
    root = tk.Tk()
    app = RegexFileRenamerGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()