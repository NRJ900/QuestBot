#FEEL FREE TO MODIFY FOR YOUR NEEDS
import os
import sys
import psutil
import subprocess
import shutil
import time
import threading
from tkinter import *
from tkinter import ttk, scrolledtext
import queue
import ctypes

class ModernButton(Canvas):
    """Custom modern button with beautiful styling and animations"""
    def __init__(self, parent, text, command, color, icon="", **kwargs):
        super().__init__(parent, height=60, highlightthickness=0, **kwargs)
        self.color = color
        self.hover_color = self.lighten_color(color)
        self.pressed_color = self.darken_color(color)
        self.command = command
        self.text = text
        self.icon = icon
        self.is_hovered = False
        self.is_pressed = False
        
        # Create shadow
        self.shadow = self.create_rounded_rect(3, 3, 277, 57, radius=12, fill="#1a1a1a", outline="")
        
        # Main button background
        self.bg_rect = self.create_rounded_rect(0, 0, 280, 54, radius=12, fill=color, outline="")
        
        # Icon and text
        if icon:
            self.icon_id = self.create_text(
                40, 27, 
                text=icon, 
                fill="white", 
                font=("Segoe UI Emoji", 18)
            )
            self.text_id = self.create_text(
                160, 27, 
                text=text, 
                fill="white", 
                font=("Segoe UI", 11, "bold")
            )
        else:
            self.text_id = self.create_text(
                140, 27, 
                text=text, 
                fill="white", 
                font=("Segoe UI", 12, "bold")
            )
        
        # Create glow outline (hidden by default)
        self.glow = self.create_rounded_rect(
            -1, -1, 281, 55, 
            radius=13, 
            fill="", 
            outline=self.hover_color, 
            width=2
        )
        self.itemconfig(self.glow, state='hidden')
        
        # Bind events to the canvas itself
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
        self.bind("<Button-1>", self.on_press)
        self.bind("<ButtonRelease-1>", self.on_release)
    
    def create_rounded_rect(self, x1, y1, x2, y2, radius=25, **kwargs):
        """Create a rounded rectangle"""
        points = [
            x1+radius, y1,
            x1+radius, y1,
            x2-radius, y1,
            x2-radius, y1,
            x2, y1,
            x2, y1+radius,
            x2, y1+radius,
            x2, y2-radius,
            x2, y2-radius,
            x2, y2,
            x2-radius, y2,
            x2-radius, y2,
            x1+radius, y2,
            x1+radius, y2,
            x1, y2,
            x1, y2-radius,
            x1, y2-radius,
            x1, y1+radius,
            x1, y1+radius,
            x1, y1
        ]
        return self.create_polygon(points, smooth=True, **kwargs)
    
    def on_enter(self, event):
        self.is_hovered = True
        self.itemconfig(self.bg_rect, fill=self.hover_color)
        self.config(cursor="hand2")
        self.itemconfig(self.glow, state='normal', outline=self.hover_color)
        
    def on_leave(self, event):
        self.is_hovered = False
        if not self.is_pressed:
            self.itemconfig(self.bg_rect, fill=self.color)
        self.config(cursor="")
        self.itemconfig(self.glow, state='hidden')
        
    def on_press(self, event):
        self.is_pressed = True
        self.itemconfig(self.bg_rect, fill=self.pressed_color)
        
        # Move elements down for press effect
        self.move(self.bg_rect, 0, 2)
        self.move(self.text_id, 0, 2)
        if hasattr(self, 'icon_id'):
            self.move(self.icon_id, 0, 2)
        
    def on_release(self, event):
        self.is_pressed = False
        
        # Move elements back up
        self.move(self.bg_rect, 0, -2)
        self.move(self.text_id, 0, -2)
        if hasattr(self, 'icon_id'):
            self.move(self.icon_id, 0, -2)
        
        if self.is_hovered:
            self.itemconfig(self.bg_rect, fill=self.hover_color)
            # Execute command
            self.command()
        else:
            self.itemconfig(self.bg_rect, fill=self.color)
        
    def lighten_color(self, color):
        """Lighten a hex color"""
        color = color.lstrip('#')
        rgb = tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
        lighter = tuple(min(255, int(c * 1.25)) for c in rgb)
        return '#%02x%02x%02x' % lighter
    
    def darken_color(self, color):
        """Darken a hex color"""
        color = color.lstrip('#')
        rgb = tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
        darker = tuple(max(0, int(c * 0.75)) for c in rgb)
        return '#%02x%02x%02x' % darker



class DiscordQuestBotGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Discord Quest Bot Manager")
        self.root.geometry("1200x900")
        self.root.resizable(True, True)
        self.root.iconbitmap("questbot.ico")

        # Modern color scheme
        self.bg_color = "#1a1d23"
        self.card_bg = "#252932"
        self.accent_color = "#5865f2"
        self.success_color = "#1F2649"
        self.danger_color = "#ed4245"
        self.run_color = "#57f287"
        self.warning_color = "#fee75c"
        self.text_color = "#ffffff"
        self.muted_text = "#b9bbbe"
        
        self.root.configure(bg=self.bg_color)
        
        # Title bar color
        self.root.update_idletasks()
        try:
            hwnd = ctypes.windll.user32.GetParent(self.root.winfo_id())
            DWMWA_USE_IMMERSIVE_DARK_MODE = 20
            value = ctypes.c_int(2)
            ctypes.windll.dwmapi.DwmSetWindowAttribute(
                hwnd, DWMWA_USE_IMMERSIVE_DARK_MODE,
                ctypes.byref(value), ctypes.sizeof(value)
            )
            self.root.update()
        except:
            pass
        # Queues for thread-safe console updates
        self.app_console_queue = queue.Queue()
        self.discord_console_queue = queue.Queue()
        
        # State variables
        self.discord_running = False
        self.modified_discord = False
        self.monitor_thread = None
        
        self.setup_ui()
        self.update_consoles_from_queue()
        
    def setup_ui(self):
        # Header
        header = Frame(self.root, bg=self.card_bg, height=100)
        header.pack(fill=X, pady=(0, 20))
        header.pack_propagate(False)
        
        title_container = Frame(header, bg=self.card_bg)
        title_container.place(relx=0.5, rely=0.5, anchor=CENTER)
        
        logo = Label(
            title_container,
            text="🎮",
            font=("Segoe UI Emoji", 40),
            bg=self.card_bg
        )
        logo.pack(side=LEFT, padx=(0, 15))
        
        title_frame = Frame(title_container, bg=self.card_bg)
        title_frame.pack(side=LEFT)
        
        title = Label(
            title_frame,
            text="Discord Quest Bot",
            font=("Segoe UI", 28, "bold"),
            bg=self.card_bg,
            fg=self.text_color
        )
        title.pack(anchor=W)
        
        subtitle = Label(
            title_frame,
            text="Automatic Quest Completion for Discord",
            font=("Segoe UI", 11),
            bg=self.card_bg,
            fg=self.muted_text
        )
        subtitle.pack(anchor=W)
        
        # Main content
        content = Frame(self.root, bg=self.bg_color)
        content.pack(fill=BOTH, expand=True, padx=30, pady=(0, 30))
        
        # Left Panel - Controls
        left_panel = Frame(content, bg=self.card_bg, width=300)
        left_panel.pack(side=LEFT, fill=Y, padx=(0, 15))
        left_panel.pack_propagate(False)
        
        controls_title = Label(
            left_panel,
            text="⚡ Quick Actions",
            font=("Segoe UI", 16, "bold"),
            bg=self.card_bg,
            fg=self.text_color
        )
        controls_title.pack(pady=(25, 20))
        
        btn_container = Frame(left_panel, bg=self.card_bg)
        btn_container.pack(pady=10)

        self.start_btn = ModernButton(
            btn_container,
            "Start Modified Discord",
            self.start_modified_discord,
            self.success_color,
            icon="🚀",
            bg=self.card_bg,
            width=280
        )
        self.start_btn.pack(pady=15)

        self.original_btn = ModernButton(
            btn_container,
            "Open Unmodified Discord",
            self.start_original_discord,
            self.accent_color,
            icon="🔓",
            bg=self.card_bg,
            width=280
        )
        self.original_btn.pack(pady=15)

        self.stop_btn = ModernButton(
            btn_container,
            "Stop Discord",
            self.stop_discord,
            self.danger_color,
            icon="🛑",
            bg=self.card_bg,
            width=280
        )
        self.stop_btn.pack(pady=15)
        
        # Status card
        status_card = Frame(left_panel, bg="#2b2f3a", relief=FLAT)
        status_card.pack(pady=20, padx=20, fill=X)
        
        status_title = Label(
            status_card,
            text="Status",
            font=("Segoe UI", 13, "bold"),
            bg="#2b2f3a",
            fg=self.text_color
        )
        status_title.pack(pady=(15, 10), anchor=W, padx=15)
        
        status_row1 = Frame(status_card, bg="#2b2f3a")
        status_row1.pack(fill=X, padx=15, pady=5)
        
        Label(
            status_row1,
            text="Operation:",
            font=("Segoe UI", 10),
            bg="#2b2f3a",
            fg=self.muted_text
        ).pack(side=LEFT)
        
        self.status_label = Label(
            status_row1,
            text="Idle",
            font=("Segoe UI", 10, "bold"),
            bg="#2b2f3a",
            fg=self.muted_text
        )
        self.status_label.pack(side=RIGHT)
        
        status_row2 = Frame(status_card, bg="#2b2f3a")
        status_row2.pack(fill=X, padx=15, pady=(5, 15))
        
        Label(
            status_row2,
            text="Discord:",
            font=("Segoe UI", 10),
            bg="#2b2f3a",
            fg=self.muted_text
        ).pack(side=LEFT)
        
        self.discord_status_label = Label(
            status_row2,
            text="Not Running",
            font=("Segoe UI", 10, "bold"),
            bg="#2b2f3a",
            fg=self.muted_text
        )
        self.discord_status_label.pack(side=RIGHT)
        
        # Info card
        info_card = Frame(left_panel, bg="#2b2f3a", relief=FLAT)
        info_card.pack(pady=(0, 20), padx=20, fill=BOTH, expand=True)
        
        info_title = Label(
            info_card,
            text="ℹ️ How It Works",
            font=("Segoe UI", 13, "bold"),
            bg="#2b2f3a",
            fg=self.text_color
        )
        info_title.pack(pady=(15, 10), anchor=W, padx=15)
        
        info_points = [
            "• Injects quest completion bot",
            "• Completes quests automatically",
            "• Real-time quest monitoring",
            "• Checks for new quests",
            "• Auto-restores on close"
        ]
        
        for point in info_points:
            Label(
                info_card,
                text=point,
                font=("Segoe UI", 9),
                bg="#2b2f3a",
                fg=self.muted_text,
                justify=LEFT
            ).pack(anchor=W, padx=15, pady=2)
        
        Label(info_card, bg="#2b2f3a", height=1).pack()
        
        # Right Panel - TWO CONSOLES
        right_panel = Frame(content, bg=self.bg_color)
        right_panel.pack(side=RIGHT, fill=BOTH, expand=True)
        
        # App Console (Top)
        app_console_frame = Frame(right_panel, bg=self.card_bg)
        app_console_frame.pack(fill=BOTH, expand=True, pady=(0, 10))
        
        app_console_header = Frame(app_console_frame, bg=self.success_color, height=40)
        app_console_header.pack(fill=X)
        app_console_header.pack_propagate(False)
        
        app_console_title = Frame(app_console_header, bg=self.success_color)
        app_console_title.place(relx=0.5, rely=0.5, anchor=CENTER)
        
        Label(
            app_console_title,
            text="App Console",
            font=("Segoe UI", 12, "bold"),
            bg=self.success_color,
            fg="white"
        ).pack()
        
        app_console_container = Frame(app_console_frame, bg=self.card_bg)
        app_console_container.pack(fill=BOTH, expand=True, padx=10, pady=10)
        
        self.app_console = scrolledtext.ScrolledText(
            app_console_container,
            bg="#0d1117",
            fg="#c9d1d9",
            font=("Cascadia Code", 9),
            insertbackground="white",
            relief=FLAT,
            state=DISABLED,
            padx=10,
            pady=10,
            height=12
        )
        self.app_console.pack(fill=BOTH, expand=True)
        
        self.app_console.tag_config("success", foreground="#3fb950")
        self.app_console.tag_config("error", foreground="#f85149")
        self.app_console.tag_config("warning", foreground="#d29922")
        self.app_console.tag_config("info", foreground="#58a6ff")
        self.app_console.tag_config("quest", foreground="#7ee787", font=("Cascadia Code", 9, "bold"))
        self.app_console.tag_config("timestamp", foreground="#8b949e")
        
        # Discord Quest Console (Bottom)
        discord_console_frame = Frame(right_panel, bg=self.card_bg)
        discord_console_frame.pack(fill=BOTH, expand=True)
        
        discord_console_header = Frame(discord_console_frame, bg=self.success_color, height=40)
        discord_console_header.pack(fill=X)
        discord_console_header.pack_propagate(False)
        
        discord_console_title = Frame(discord_console_header, bg=self.success_color)
        discord_console_title.place(relx=0.5, rely=0.5, anchor=CENTER)
        
        Label(
            discord_console_title,
            text="Output Console",
            font=("Segoe UI", 12, "bold"),
            bg=self.success_color,
            fg="white"
        ).pack()
        
        discord_console_container = Frame(discord_console_frame, bg=self.card_bg)
        discord_console_container.pack(fill=BOTH, expand=True, padx=10, pady=10)
        
        self.discord_console = scrolledtext.ScrolledText(
            discord_console_container,
            bg="#0d1117",
            fg="#7ee787",
            font=("Cascadia Code", 9),
            insertbackground="white",
            relief=FLAT,
            state=DISABLED,
            padx=10,
            pady=10,
            height=12
        )
        self.discord_console.pack(fill=BOTH, expand=True)
        
        self.discord_console.tag_config("quest_success", foreground="#3fb950", font=("Cascadia Code", 9, "bold"))
        self.discord_console.tag_config("quest_progress", foreground="#7ee787", font=("Cascadia Code", 9, "bold"))
        self.discord_console.tag_config("quest_info", foreground="#58a6ff")
        self.discord_console.tag_config("quest_warning", foreground="#d29922")
        self.discord_console.tag_config("quest_error", foreground="#f85149")
        self.discord_console.tag_config("timestamp", foreground="#8b949e")
        
        # Console controls
        console_controls = Frame(right_panel, bg=self.bg_color)
        console_controls.pack(fill=X, pady=(10, 0))
        
        Button(
            console_controls,
            text="Clear App Console",
            command=self.clear_app_console,
            bg="#2b2f3a",
            fg=self.text_color,
            font=("Segoe UI", 9),
            relief=FLAT,
            cursor="hand2",
            padx=15,
            pady=6
        ).pack(side=LEFT, padx=(0, 10))
        
        Button(
            console_controls,
            text="🗑️ Clear Quest Console",
            command=self.clear_discord_console,
            bg="#2b2f3a",
            fg=self.text_color,
            font=("Segoe UI", 9),
            relief=FLAT,
            cursor="hand2",
            padx=15,
            pady=6
        ).pack(side=LEFT)
        
        # Initial messages
        self.log_app("🎮 Discord Quest Bot Manager initialized", "success")
        self.log_app("Ready! Click 'Start Modified Discord' to begin", "info")
        self.log_discord("⏳ Checking for errors...", "quest_info")
        
    def log_app(self, message, tag="info"):
        """Log to app console"""
        self.app_console_queue.put((message, tag))
    
    def log_discord(self, message, tag="quest_info"):
        """Log to Discord quest console"""
        self.discord_console_queue.put((message, tag))
    
    def update_consoles_from_queue(self):
        """Update both consoles from their queues"""
        # Update app console
        try:
            while True:
                message, tag = self.app_console_queue.get_nowait()
                self.app_console.config(state=NORMAL)
                timestamp = time.strftime("[%H:%M:%S] ")
                self.app_console.insert(END, timestamp, "timestamp")
                self.app_console.insert(END, message + "\n", tag)
                self.app_console.see(END)
                self.app_console.config(state=DISABLED)
        except queue.Empty:
            pass
        
        # Update Discord console
        try:
            while True:
                message, tag = self.discord_console_queue.get_nowait()
                self.discord_console.config(state=NORMAL)
                timestamp = time.strftime("[%H:%M:%S] ")
                self.discord_console.insert(END, timestamp, "timestamp")
                self.discord_console.insert(END, message + "\n", tag)
                self.discord_console.see(END)
                self.discord_console.config(state=DISABLED)
        except queue.Empty:
            pass
        
        self.root.after(100, self.update_consoles_from_queue)
    
    def clear_app_console(self):
        self.app_console.config(state=NORMAL)
        self.app_console.delete(1.0, END)
        self.app_console.config(state=DISABLED)
        self.log_app("Console cleared", "info")
    
    def clear_discord_console(self):
        self.discord_console.config(state=NORMAL)
        self.discord_console.delete(1.0, END)
        self.discord_console.config(state=DISABLED)
        self.log_discord("Console cleared", "quest_info")
    
    def update_status(self, text, color):
        self.status_label.config(text=text, fg=color)
    
    def update_discord_status(self, running, modified=False):
        self.discord_running = running
        self.modified_discord = modified
        
        if running:
            status = "Running (Modified)" if modified else "Running (Original)"
            self.discord_status_label.config(text=status, fg=self.run_color)
        else:
            self.discord_status_label.config(text="Not Running", fg=self.muted_text)
    
    def find_discord(self):
        """Find Discord"""
        username = os.getenv('USERNAME')
        base = f"C:\\Users\\{username}\\AppData\\Local\\Discord"
        
        for root, dirs, files in os.walk(base):
            if 'Discord.exe' in files:
                return os.path.join(root, 'Discord.exe'), os.path.join(root, 'resources')
        return None, None
    
    def kill_discord(self):
        """Kill Discord"""
        killed = 0
        for p in psutil.process_iter(['name']):
            try:
                if 'Discord' in p.info['name']:
                    p.kill()
                    killed += 1
            except:
                pass
        
        if killed > 0:
            time.sleep(3)
        return killed
    
    def extract_asar(self, asar_file, extract_dir):
        return os.system(f'npx asar extract "{asar_file}" "{extract_dir}" >nul 2>&1') == 0
    
    def pack_asar(self, source_dir, asar_file):
        return os.system(f'npx asar pack "{source_dir}" "{asar_file}" >nul 2>&1') == 0    
    
    def start_modified_discord(self):
        """Start Discord with quest bot injection"""
        def inject_thread():
            try:
                self.update_status("Injecting...", self.warning_color)
                self.log_app("🚀 Starting modified Discord injection...", "info")
                
                exe, resources = self.find_discord()
                if not exe:
                    self.log_app("❌ Discord not found!", "error")
                    self.update_status("Error", self.danger_color)
                    return
                
                self.log_app(f"✅ Found Discord", "success")
                
                asar_file = os.path.join(resources, 'app.asar')
                asar_backup = os.path.join(resources, 'app.asar.backup')
                extract_dir = os.path.join(resources, 'app_extracted')
                
                if os.path.exists(asar_backup):
                    self.log_app("⚠️  Previous backup found, restoring first...", "warning")
                    killed = self.kill_discord()
                    if killed > 0:
                        self.log_app(f"🛑 Closed {killed} Discord process(es)", "info")
                    
                    if os.path.exists(asar_file):
                        os.remove(asar_file)
                    shutil.copy2(asar_backup, asar_file)
                    os.remove(asar_backup)
                    self.log_app("✅ Previous state restored", "success")
                
                killed = self.kill_discord()
                if killed > 0:
                    self.log_app(f"🛑 Closed {killed} Discord process(es)", "info")
                
                self.log_app("📦 Creating backup...", "info")
                shutil.copy2(asar_file, asar_backup)
                self.log_app("✅ Backup created", "success")
                
                if os.path.exists(extract_dir):
                    shutil.rmtree(extract_dir)
                
                self.log_app("📂 Extracting app.asar...", "info")
                if not self.extract_asar(asar_file, extract_dir):
                    self.log_app("❌ Extraction failed!", "error")
                    self.update_status("Error", self.danger_color)
                    return
                
                self.log_app("✅ Extraction complete", "success")
                
                # Find index.js
                index_file = None
                for root, dirs, files in os.walk(extract_dir):
                    if 'index.js' in files:
                        potential = os.path.join(root, 'index.js')
                        with open(potential, 'r', encoding='utf-8') as f:
                            content = f.read()
                            if 'require' in content and len(content) > 100:
                                index_file = potential
                                break
                
                if not index_file:
                    self.log_app("❌ index.js not found!", "error")
                    self.update_status("Error", self.danger_color)
                    return
                
                self.log_app("✅ Found index.js", "success")
                
                injection_code = r"""

// Quest Bot - Continuous Auto-Completion
const {BrowserWindow} = require('electron');
const {app} = require('electron');

function injectQuestBot(window) {
    if (!window || !window.webContents || window.isDestroyed() || window.webContents.isDestroyed()) {
        return;
    }
    
    try {
        const questScript = `
(function() {
    console.log('[QUEST BOT] Starting continuous quest automation...');
    
    let initAttempts = 0;
    const maxAttempts = 120;
    let activeQuestId = null;
    
    function tryInit() {
        initAttempts++;
        
        if (initAttempts % 10 === 0) {
            console.log('[QUEST BOT] Waiting for Discord... attempt', initAttempts);
        }
        
        if (!window.webpackChunkdiscord_app) {
            if (initAttempts < maxAttempts) {
                setTimeout(tryInit, 1000);
            }
            return;
        }
        
        console.log('[QUEST BOT] Webpack found!');
        
        try {
            var w = webpackChunkdiscord_app.push([[Symbol()], {}, r => r]);
            webpackChunkdiscord_app.pop();
            
            var R = Object.values(w.c).find(x => x?.exports?.ZP?.getRunningGames)?.exports?.ZP;
            var Q = Object.values(w.c).find(x => x?.exports?.Z?.__proto__?.getQuest)?.exports?.Z;
            var F = Object.values(w.c).find(x => x?.exports?.Z?.__proto__?.flushWaitQueue)?.exports?.Z;
            var A = Object.values(w.c).find(x => x?.exports?.tn?.get)?.exports?.tn;
            
            if (!R || !Q || !F || !A) {
                if (initAttempts < maxAttempts) {
                    setTimeout(tryInit, 2000);
                }
                return;
            }
            
            console.log('[QUEST BOT] All stores loaded!');
            startContinuousQuestBot(R, Q, F, A);
            
        } catch (e) {
            console.error('[QUEST BOT] Error:', e);
            if (initAttempts < maxAttempts) {
                setTimeout(tryInit, 2000);
            }
        }
    }
    
    function startContinuousQuestBot(R, Q, F, A) {
        console.log('[QUEST BOT] 🔄 Continuous quest mode enabled');
        
        function checkForQuests() {
            try {
                var q = [...Q.quests.values()].find(x => 
                    x.userStatus?.enrolledAt && 
                    !x.userStatus?.completedAt &&
                    new Date(x.config.expiresAt).getTime() > Date.now()
                );
                
                if (!q) {
                    console.log('[QUEST BOT] ⏳ No active quest. Checking in 1 minute...');
                    setTimeout(checkForQuests, 60000);
                    return;
                }
                
                if (activeQuestId !== q.id) {
                    activeQuestId = q.id;
                    console.log('[QUEST BOT] ✅ NEW QUEST:', q.config.messages.questName);
                    startQuest(q, R, Q, F, A);
                } else {
                    setTimeout(checkForQuests, 30000);
                }
                
            } catch (e) {
                setTimeout(checkForQuests, 120000);
            }
        }
        
        function startQuest(q, R, Q, F, A) {
            var p = Math.floor(Math.random() * 30000) + 1000;
            var id = q.config.application.id;
            var taskConfig = q.config.taskConfig ?? q.config.taskConfigV2;
            var taskName = Object.keys(taskConfig.tasks)[0];
            var need = taskConfig.tasks[taskName].target;
            
            if (taskName !== 'PLAY_ON_DESKTOP') {
                activeQuestId = null;
                setTimeout(checkForQuests, 120000);
                return;
            }
            
            A.get({url: '/applications/public?application_ids=' + id}).then(r => {
                var a = r.body[0];
                var e = a.executables.find(x => x.os === 'win32').name.replace('>', '');
                
                var g = {
                    cmdLine: 'C:\\\\\\\\Program Files\\\\\\\\' + a.name + '\\\\\\\\' + e,
                    exeName: e,
                    exePath: 'c:/program files/' + a.name.toLowerCase() + '/' + e,
                    hidden: false,
                    isLauncher: false,
                    id: id,
                    name: a.name,
                    pid: p,
                    pidPath: [p],
                    processName: a.name,
                    start: Date.now()
                };
                
                var o1 = R.getRunningGames;
                var o2 = R.getGameForPID;
                
                R.getRunningGames = () => [g];
                R.getGameForPID = x => x === p ? g : null;
                F.dispatch({type: 'RUNNING_GAMES_CHANGE', removed: [], added: [g], games: [g]});
                
                console.log('[QUEST BOT] ✅✅✅ GAME SPOOFED:', a.name, '✅✅✅');
                
                var progressHandler = function(d) {
                    try {
                        var pr = Math.floor(d.userStatus.progress.PLAY_ON_DESKTOP.value);
                        var percent = Math.round(pr / need * 100);
                        var timeLeft = Math.ceil((need - pr) / 60);
                        
                        console.log('[QUEST BOT] 📊 PROGRESS:', pr + '/' + need, '(' + percent + '%) ~' + timeLeft + ' min');
                        
                        if (pr >= need) {
                            console.log('[QUEST BOT] 🎉🎉🎉 QUEST COMPLETE! 🎉🎉🎉');
                            
                            R.getRunningGames = o1;
                            R.getGameForPID = o2;
                            F.dispatch({type: 'RUNNING_GAMES_CHANGE', removed: [g], added: [], games: []});
                            F.unsubscribe('QUESTS_SEND_HEARTBEAT_SUCCESS', progressHandler);
                            
                            activeQuestId = null;
                            console.log('[QUEST BOT] 🔄 Checking in 1 minute...');
                            setTimeout(checkForQuests, 60000);
                        }
                    } catch (err) {}
                };
                
                F.subscribe('QUESTS_SEND_HEARTBEAT_SUCCESS', progressHandler);
                console.log('[QUEST BOT] ✅ Bot active!');
                
            }).catch(err => {
                activeQuestId = null;
                setTimeout(checkForQuests, 120000);
            });
        }
        
        checkForQuests();
    }
    
    tryInit();
})();
        `;
        
        window.webContents.executeJavaScript(questScript).catch(() => {});
        
    } catch (err) {}
}

app.on('browser-window-created', (event, window) => {
    window.webContents.on('dom-ready', () => {
        setTimeout(() => {
            if (!window.isDestroyed()) {
                injectQuestBot(window);
            }
        }, 3000);
    });
    
    window.webContents.on('did-navigate', () => {
        setTimeout(() => {
            if (!window.isDestroyed()) {
                injectQuestBot(window);
            }
        }, 2000);
    });
    
    window.webContents.on('did-navigate-in-page', () => {
        setTimeout(() => {
            if (!window.isDestroyed()) {
                injectQuestBot(window);
            }
        }, 2000);
    });
});
"""
                
                with open(index_file, 'a', encoding='utf-8') as f:
                    f.write(injection_code)
            
                if os.path.exists(asar_file):
                    os.remove(asar_file)
                
                self.log_app("📦 Repacking...", "info")
                if not self.pack_asar(extract_dir, asar_file):
                    self.log_app("❌ Packing failed!", "error")
                    shutil.copy2(asar_backup, asar_file)
                    self.update_status("Error", self.danger_color)
                    return
                
                self.log_app("✅ Repacked successfully", "success")
                shutil.rmtree(extract_dir)
                
                self.log_app("🚀 Starting Discord...", "info")
                subprocess.Popen([exe])
                
                time.sleep(1)
                
                self.log_app("═" * 50, "quest")
                self.log_app("✅ MODIFIED DISCORD STARTED!", "quest")
                self.log_app("═" * 50, "quest")
                
                self.update_status("Running", self.run_color)
                self.update_discord_status(True, modified=True)
                
                # Start file monitoring
                self.start_monitoring(exe, asar_file, asar_backup)
                
            except Exception as e:
                self.log_app(f"❌ Error: {str(e)}", "error")
                self.update_status("Error", self.danger_color)
        
        thread = threading.Thread(target=inject_thread, daemon=True)
        thread.start()
    
    def start_original_discord(self):
        """Start original Discord"""
        def start_thread():
            try:
                self.update_status("Starting...", self.warning_color)
                self.log_app("🔓 Starting Unmodified Discord...", "info")
                
                exe, resources = self.find_discord()
                if not exe:
                    self.log_app("❌ Discord not found!", "error")
                    self.update_status("Error", self.danger_color)
                    return
                
                asar_file = os.path.join(resources, 'app.asar')
                asar_backup = os.path.join(resources, 'app.asar.backup')
                
                if os.path.exists(asar_backup):
                    self.log_app("⚠️  Modified version detected, restoring...", "warning")
                    killed = self.kill_discord()
                    if killed > 0:
                        self.log_app(f"🛑 Closed {killed} Discord process(es)", "info")
                    
                    if os.path.exists(asar_file):
                        os.remove(asar_file)
                    shutil.copy2(asar_backup, asar_file)
                    os.remove(asar_backup)
                    self.log_app("✅ Original restored", "success")
                else:
                    killed = self.kill_discord()
                    if killed > 0:
                        self.log_app(f"🛑 Closed {killed} Discord process(es)", "info")
                
                subprocess.Popen([exe])
                self.log_app("✅ Unmodified Discord started", "success")
                
                self.update_status("Running", self.accent_color)
                self.update_discord_status(True, modified=False)
                
                self.log_discord("ℹ️  Unmodified Discord - No quest bot active", "quest_info")
                
            except Exception as e:
                self.log_app(f"❌ Error: {str(e)}", "error")
                self.update_status("Error", self.danger_color)
        
        thread = threading.Thread(target=start_thread, daemon=True)
        thread.start()
    
    def stop_discord(self):
        """Stop Discord completely and restore original"""
        def stop_thread():
            try:
                self.log_app("🛑 Stopping Discord ...", "warning")
                
                exe, resources = self.find_discord()
                if not exe:
                    self.log_app("❌ Discord not found!", "error")
                    self.update_status("Error", self.danger_color)
                    return
                
                asar_file = os.path.join(resources, 'app.asar')
                asar_backup = os.path.join(resources, 'app.asar.backup')
                
                # Kill Discord first
                killed = self.kill_discord()
                if killed > 0:
                    self.log_app(f"🛑 Closed {killed} Discord process(es)", "info")
                else:
                    self.log_app("ℹ️  Discord was not running", "info")
                
                # Check if backup exists
                if not os.path.exists(asar_backup):
                    self.log_app("ℹ️  No backup found - Discord already in original state", "info")
                    self.update_status("Idle", self.muted_text)
                    self.update_discord_status(False)
                    return
                
                self.log_app("🔄 Found backup, starting restore process...", "info")
                
                # Verify backup file is valid before proceeding
                backup_size = os.path.getsize(asar_backup)
                self.log_app(f"ℹ️  Backup file size: {backup_size} bytes", "info")
                
                if backup_size < 1000000:  # Less than 1MB is suspicious
                    self.log_app("⚠️  WARNING: Backup file seems too small!", "warning")
                    self.log_app("❌ Aborting to preserve backup", "error")
                    self.update_status("Error", self.danger_color)
                    return
                
                # Step 1: Remove modified asar
                if os.path.exists(asar_file):
                    try:
                        os.remove(asar_file)
                        self.log_app("✅ Step 1: Removed modified app.asar", "success")
                    except Exception as e:
                        self.log_app(f"❌ Failed to remove modified asar: {e}", "error")
                        self.update_status("Error", self.danger_color)
                        return
                else:
                    self.log_app("ℹ️  Step 1: No modified asar to remove", "info")
                
                # Step 2: Copy backup to original location
                try:
                    shutil.copy2(asar_backup, asar_file)
                    self.log_app("✅ Step 2: Copied backup to app.asar location", "success")
                except Exception as e:
                    self.log_app(f"❌ CRITICAL: Failed to restore backup: {e}", "error")
                    self.log_app("⚠️  BACKUP FILE PRESERVED - DO NOT DELETE", "warning")
                    self.update_status("Error", self.danger_color)
                    return
                
                # Step 3: Verify the restored file exists and has correct size
                if not os.path.exists(asar_file):
                    self.log_app("❌ CRITICAL: Restored asar file not found!", "error")
                    self.log_app("⚠️  BACKUP PRESERVED", "warning")
                    self.update_status("Error", self.danger_color)
                    return
                
                restored_size = os.path.getsize(asar_file)
                
                if restored_size != backup_size:
                    self.log_app("❌ CRITICAL: Restored file size mismatch!", "error")
                    self.log_app("⚠️  BACKUP PRESERVED", "warning")
                    self.update_status("Error", self.danger_color)
                    return
                
                self.log_app("✅ Step 3: Verified restored file integrity", "success")
                
                # Step 4: ONLY NOW delete the backup after ALL verifications pass
                try:
                    os.remove(asar_backup)
                    self.log_app("✅ Step 4: Deleted backup file", "success")
                except Exception as e:
                    self.log_app(f"⚠️  Could not delete backup: {e}", "warning")
                    self.log_app("ℹ️  Backup remains but restoration was successful", "info")
                
                self.log_app(f"ℹ️  Backup file size: {backup_size} bytes", "info")
                self.log_app(f"ℹ️  Restored file size: {restored_size} bytes", "info")
                
                self.log_app("═" * 50, "success")
                self.log_app("✅ Discord fully restored to original state!", "success")
                self.log_app("═" * 50, "success")
                
                self.update_status("Idle", self.muted_text)
                self.update_discord_status(False)

            except Exception as e:
                self.log_app(f"❌ Unexpected error: {str(e)}", "error")
                self.log_app("⚠️  If backup exists, it has been preserved", "warning")
                self.update_status("Error", self.danger_color)
        
        thread = threading.Thread(target=stop_thread, daemon=True)
        thread.start()

    
    def start_monitoring(self, exe_path, asar_file, asar_backup):
        """Monitor Discord and auto-restore"""
        def monitor():
            self.log_app("👁️ Monitoring Discord process...", "info")
            time.sleep(5)
            
            discord_running = True
            while discord_running:
                discord_running = False
                for proc in psutil.process_iter(['name', 'exe']):
                    try:
                        if proc.info['exe'] and exe_path in proc.info['exe']:
                            discord_running = True
                            break
                    except:
                        pass
                
                time.sleep(2)
            
            # Discord closed - restore original
            self.log_app("🛑 Discord has been closed, You can safely quit this app now.", "warning")
            time.sleep(1)
            
            try:
                if not os.path.exists(asar_backup):
                    self.log_app("ℹ️  No backup to restore", "info")
                    self.update_status("Idle", self.muted_text)
                    self.update_discord_status(False)
                    return
                
                self.log_app("🔄 Auto-restoring original Discord...", "info")
                
                # Verify backup
                backup_size = os.path.getsize(asar_backup)
                if backup_size < 1000000:
                    self.log_app("⚠️  Backup seems corrupted, preserving it", "warning")
                    self.update_status("Error", self.danger_color)
                    return
                
                # Remove modified
                if os.path.exists(asar_file):
                    os.remove(asar_file)
                
                # Restore from backup
                shutil.copy2(asar_backup, asar_file)
                
                # Verify restore
                if not os.path.exists(asar_file) or os.path.getsize(asar_file) != backup_size:
                    self.log_app("❌ Restore verification failed, keeping backup", "error")
                    return
                
                self.log_app("✅ Restored original app.asar", "success")
                
                # Delete backup only after successful verification
                os.remove(asar_backup)
                self.log_app("✅ Backup cleaned up", "success")
                    
            except Exception as e:
                self.log_app(f"❌ Error during auto-restore: {str(e)}", "error")
                self.log_app("⚠️  Backup preserved if it exists", "warning")
            
            self.update_status("Idle", self.muted_text)
            self.update_discord_status(False)
        
        self.monitor_thread = threading.Thread(target=monitor, daemon=True)
        self.monitor_thread.start()


if __name__ == "__main__":
    root = Tk()
    app = DiscordQuestBotGUI(root)
    root.mainloop()
