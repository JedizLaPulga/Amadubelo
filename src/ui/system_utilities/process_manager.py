"""
Process Manager View
View and manage running processes.
"""

import customtkinter as ctk
from tkinter import messagebox
import threading
import psutil
import os
from ui.components.tool_view_base import ToolViewBase


class ProcessManagerView(ToolViewBase):
    """View for process management."""

    def __init__(self, parent, colors: dict, on_back=None, **kwargs):
        super().__init__(
            parent,
            title="Process Manager",
            icon="⚙️",
            description="View and manage running processes",
            colors=colors,
            on_back=on_back,
            **kwargs
        )

        self.processes = []
        self.sort_column = "name"
        self.sort_reverse = False

        self._create_content()
        self._refresh_processes()

    def _create_content(self):
        """Create the main content area."""
        content = ctk.CTkScrollableFrame(self, fg_color="transparent")
        content.grid(row=2, column=0, sticky="nsew", padx=20, pady=10)
        content.grid_columnconfigure(0, weight=1)
        content.grid_rowconfigure(1, weight=1)

        # Control buttons
        controls_frame = ctk.CTkFrame(content, fg_color=self.colors["bg_card"], corner_radius=10)
        controls_frame.grid(row=0, column=0, sticky="ew", pady=(0, 20))

        refresh_btn = ctk.CTkButton(
            controls_frame,
            text="🔄 Refresh",
            fg_color=self.colors["primary"],
            hover_color=self.colors["primary_hover"],
            text_color=self.colors["text"],
            command=self._refresh_processes
        )
        refresh_btn.grid(row=0, column=0, padx=15, pady=15)

        # Process list header
        header_frame = ctk.CTkFrame(content, fg_color=self.colors["bg_card"], corner_radius=10)
        header_frame.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        header_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)

        # Column headers with sorting
        headers = [
            ("Name", "name"),
            ("PID", "pid"),
            ("CPU %", "cpu_percent"),
            ("Memory %", "memory_percent")
        ]

        for i, (text, column) in enumerate(headers):
            btn = ctk.CTkButton(
                header_frame,
                text=text,
                fg_color="transparent",
                hover_color=self.colors["bg_card_hover"],
                text_color=self.colors["primary_light"],
                font=ctk.CTkFont(size=12, weight="bold"),
                command=lambda c=column: self._sort_processes(c)
            )
            btn.grid(row=0, column=i, padx=5, pady=10, sticky="ew")

        # Process list container
        self.process_frame = ctk.CTkScrollableFrame(
            content,
            fg_color=self.colors["bg_card"],
            corner_radius=10,
            height=400
        )
        self.process_frame.grid(row=2, column=0, sticky="ew", pady=(0, 20))
        self.process_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)

        # Status label
        self.status_label = ctk.CTkLabel(
            content,
            text="Loading processes...",
            text_color=self.colors["text_secondary"]
        )
        self.status_label.grid(row=3, column=0, pady=(0, 10))

    def _refresh_processes(self):
        """Refresh the process list."""
        self.set_status("Loading processes...")

        # Clear existing processes
        for widget in self.process_frame.winfo_children():
            widget.destroy()

        # Run in thread to avoid blocking UI
        thread = threading.Thread(target=self._load_processes)
        thread.daemon = True
        thread.start()

    def _load_processes(self):
        """Load process information."""
        try:
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    info = proc.info
                    processes.append({
                        'pid': info['pid'],
                        'name': info['name'] or 'Unknown',
                        'cpu_percent': info['cpu_percent'] or 0.0,
                        'memory_percent': info['memory_percent'] or 0.0
                    })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue

            self.processes = processes
            self.after(0, self._display_processes)

        except Exception as e:
            self.after(0, lambda: self._show_error(f"Failed to load processes: {str(e)}"))

    def _display_processes(self):
        """Display the processes in the UI."""
        # Clear existing
        for widget in self.process_frame.winfo_children():
            widget.destroy()

        # Sort processes
        self._sort_processes(self.sort_column, update_display=False)

        # Display processes
        for i, proc in enumerate(self.processes[:100]):  # Limit to 100 for performance
            # Alternate row colors
            bg_color = self.colors["bg_card"] if i % 2 == 0 else self.colors["bg_card_hover"]

            # Process name
            name_label = ctk.CTkLabel(
                self.process_frame,
                text=proc['name'][:30] + "..." if len(proc['name']) > 30 else proc['name'],
                text_color=self.colors["text"],
                font=ctk.CTkFont(size=11),
                anchor="w"
            )
            name_label.grid(row=i, column=0, padx=10, pady=2, sticky="ew")

            # PID
            pid_label = ctk.CTkLabel(
                self.process_frame,
                text=str(proc['pid']),
                text_color=self.colors["text"],
                font=ctk.CTkFont(size=11)
            )
            pid_label.grid(row=i, column=1, padx=10, pady=2)

            # CPU %
            cpu_label = ctk.CTkLabel(
                self.process_frame,
                text=".1f",
                text_color=self.colors["text"],
                font=ctk.CTkFont(size=11)
            )
            cpu_label.grid(row=i, column=2, padx=10, pady=2)

            # Memory %
            mem_label = ctk.CTkLabel(
                self.process_frame,
                text=".1f",
                text_color=self.colors["text"],
                font=ctk.CTkFont(size=11)
            )
            mem_label.grid(row=i, column=3, padx=10, pady=2)

            # End process button (only for non-system processes)
            if proc['pid'] not in [0, 4] and not self._is_system_process(proc['name']):
                end_btn = ctk.CTkButton(
                    self.process_frame,
                    text="❌",
                    width=30,
                    height=25,
                    fg_color=self.colors["error"],
                    hover_color="#dc2626",
                    text_color="white",
                    font=ctk.CTkFont(size=10),
                    command=lambda p=proc: self._end_process(p)
                )
                end_btn.grid(row=i, column=4, padx=(5, 10), pady=2)

        process_count = len(self.processes)
        self.set_status(f"Showing {min(process_count, 100)} of {process_count} processes")

    def _sort_processes(self, column, update_display=True):
        """Sort processes by column."""
        if self.sort_column == column:
            self.sort_reverse = not self.sort_reverse
        else:
            self.sort_column = column
            self.sort_reverse = False

        try:
            self.processes.sort(key=lambda x: x[column], reverse=self.sort_reverse)
        except (TypeError, KeyError):
            # Fallback to name sorting
            self.processes.sort(key=lambda x: x['name'], reverse=self.sort_reverse)

        if update_display:
            self._display_processes()

    def _is_system_process(self, name):
        """Check if process is a system process."""
        system_processes = [
            'System', 'systemd', 'init', 'launchd', 'svchost.exe', 'csrss.exe',
            'wininit.exe', 'winlogon.exe', 'services.exe', 'lsass.exe',
            'smss.exe', 'explorer.exe', 'dwm.exe'
        ]
        return name.lower() in [p.lower() for p in system_processes]

    def _end_process(self, proc):
        """End a process."""
        if messagebox.askyesno(
            "Confirm",
            f"Are you sure you want to end the process '{proc['name']}' (PID: {proc['pid']})?"
        ):
            try:
                p = psutil.Process(proc['pid'])
                p.terminate()
                self.set_status(f"Terminated process {proc['name']}")
                # Refresh after a short delay
                self.after(1000, self._refresh_processes)
            except Exception as e:
                self.show_error(f"Failed to terminate process: {str(e)}")

    def _show_error(self, message):
        """Show error message."""
        self.set_status(message)