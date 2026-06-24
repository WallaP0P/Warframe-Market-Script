import os
import threading
import time
import re
import urllib.request
import tkinter as tk
from tkinter import messagebox, ttk
 
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.chrome.options import Options
 
 
BASE_URL = "https://api.warframe.market/v2"
SITE_URL = "https://warframe.market/"
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(SCRIPT_DIR, "config.txt")
DEFAULT_PRICE = 15
REQUEST_DELAY_SECONDS = 0.35   # 3 req/s max → ~0.34s di margine
CHROME_BINARY_CANDIDATES = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    r"C:\Users\Samuele\AppData\Local\PuppeteerSharp\Chrome\Win64-124.0.6367.201\chrome-win64\chrome.exe",
]

# Tutte le mod divise per syndicate
SYNDICATE_MODS = {
    "Cephalon Simaris": [
        "ambush",
        "astral-autopsy",
        "botanist",
        "detect-vulnerability",
        "energy-conversion",
        "energy-generator",
        "health-conversion",
        "looter",
        "negate",
        "reawaken",
    ],
    "Entrati": [
        "contagious-bond",
        "duplex-bond",
        "seismic-bond",
        "vicious-bond",
        "martyr-symbiosis",
        "volatile-parasite",
    ],
    "Solaris United": [
        "reinforced-bond",
        "momentous-bond",
        "tenacious-bond",
        "aerial-bond",
        "astral-bond",
        "loyal-retriever",
        "mystic-bond",
        "precision-conditioning",
        "balanced-posture",
        "bloodthirst",
        "cull-the-weak",
    ],
    "Ostron": [
        "tandem-bond",
        "manifold-bond",
        "mystic-bond",
        "restorative-bond",
        "covert-bond",
    ],
    "New Loka": [
        "abating-link",
        "anchored-glide",
        "airburst-rounds",
        "assimilate",
        "axios-javelineers",
        "beguiling-lantern",
        "bright-purity",
        "calm-and-frenzy",
        "cataclysmic-gate",
        "celestial-stomp",
        "champions-blessing",
        "chaos-sphere",
        "conductor",
        "counter-pulse",
        "critical-surge",
        "disarming-purity",
        "duality",
        "elusive-retribution",
        "endless-lullaby",
        "energy-transfer",
        "enraged",
        "enveloping-cloud",
        "eternal-war",
        "fracturing-crush",
        "funnel-clouds",
        "fused-reservoir",
        "greedy-pull",
        "hallowed-eruption",
        "hallowed-reckoning",
        "hysterical-assault",
        "intrepid-stand",
        "ironclad-flight",
        "jet-stream",
        "kumihimo-loading",
        "lasting-purity",
        "lingering-transmutation",
        "loyal-merulina",
        "magnetized-discharge",
        "mending-splinters",
        "merulina-guardian",
        "mind-freak",
        "omikujis-fortune",
        "pacifying-bolts",
        "partitioned-mallet",
        "peaceful-provocation",
        "phoenix-renewal",
        "pilfering-swarm",
        "pool-of-life",
        "primal-rage",
        "prolonged-paralysis",
        "razorwing-blitz",
        "reactive-storm",
        "rhythm-guard",
        "rousing-plunder",
        "shattered-storm",
        "smite-infusion",
        "spectrosiphon",
        "spellbound-harvest",
        "surging-blades",
        "swift-bite",
        "swing-line",
        "target-fixation",
        "tharros-lethality",
        "tidal-impunity",
        "valence-formation",
        "vampire-leech",
        "viral-tempest",
        "volatile-recompense",
        "winds-of-purity",
        "wrath-of-ukko",
    ],
    "The Perrin Sequence": [
        "abating-link",
        "abundant-mutation",
        "aegis-gale",
        "afterburn",
        "balefire-surge",
        "blazing-pillage",
        "blinding-reave",
        "cathode-current",
        "champions-blessing",
        "coil-recharge",
        "conductive-sphere",
        "concentrated-arrow",
        "counter-pulse",
        "creeping-terrify",
        "dark-propagation",
        "deadly-sequence",
        "desiccations-curse",
        "despoil",
        "elemental-sandstorm",
        "empowered-quiver",
        "enraged",
        "eternal-war",
        "everlasting-ward",
        "fracturing-crush",
        "greedy-pull",
        "guardian-armor",
        "guided-effigy",
        "hysterical-assault",
        "infiltrate",
        "insatiable",
        "iron-shrapnel",
        "ironclad-charge",
        "larva-burst",
        "mach-crash",
        "magnetized-discharge",
        "mesmer-shield",
        "negation-swarm",
        "parasitic-vitality",
        "photon-repeater",
        "piercing-navigator",
        "piercing-roar",
        "pool-of-life",
        "prolonged-paralysis",
        "razor-mortar",
        "repair-dispensary",
        "repelling-bastille",
        "reinforcing-stomp",
        "reroot-rampage",
        "resonance",
        "resonating-quake",
        "reverse-rotorswell",
        "savage-silence",
        "sequence-burn",
        "shadow-haze",
        "shield-of-shadows",
        "sonic-fracture",
        "soul-survivor",
        "spectral-spirit",
        "swing-line",
        "teeming-virulence",
        "temporal-artillery",
        "temporal-erosion",
        "tesla-bank",
        "thermal-transfer",
        "thrall-pact",
        "toxic-sequence",
        "vampire-leech",
        "vexing-retaliation",
        "voltage-sequence",
    ],
    "Red Veil": [
        "airburst-rounds",
        "anchored-glide",
        "accumulating-whipclaw",
        "ballistic-bullseye",
        "beguiling-lantern",
        "blending-talons",
        "blood-forge",
        "capacitance",
        "catapult",
        "contagion-cloud",
        "creeping-terrify",
        "damage-decoy",
        "despoil",
        "dread-ward",
        "eroding-blight",
        "exothermic",
        "fireball-frenzy",
        "funnel-clouds",
        "gastro",
        "gleaming-blight",
        "gourmand",
        "healing-flame",
        "hearty-nourishment",
        "hushed-invisibility",
        "immolated-radiance",
        "irradiating-disarm",
        "ironclad-flight",
        "jades-judgment",
        "jet-stream",
        "lasting-covenant",
        "lingering-transmutation",
        "mesas-waltz",
        "muzzle-flash",
        "ore-gaze",
        "path-of-statues",
        "pilfering-strangledome",
        "prey-of-dynar",
        "prismatic-companion",
        "razorwing-blitz",
        "recrystalize",
        "regenerative-molt",
        "reroot-rampage",
        "revealing-spores",
        "rising-storm",
        "rubble-heap",
        "safeguard-switch",
        "savior-decoy",
        "seeking-shuriken",
        "shield-of-shadows",
        "shocking-speed",
        "shock-trooper",
        "smoke-shadow",
        "soul-survivor",
        "spectral-spirit",
        "spellbound-harvest",
        "staggering-shield",
        "stockpiled-blight",
        "swift-bite",
        "target-fixation",
        "tectonic-fracture",
        "fatal-teleport",
        "toxic-blight",
        "transistor-shield",
        "tribunal",
        "ulfruns-endurance",
        "valence-formation",
        "venari-bodyguard",
        "venom-dose",
        "warding-thurible",
        "warriors-rest",
    ],
}

# Intervallo in minuti tra aggiornamenti automatici dei prezzi (0 = disabilitato)
DEFAULT_REFRESH_MINUTES = 30
 
 
class ApiError(Exception):
    def __init__(self, message, status=None, body=None):
        super().__init__(message)
        self.status = status
        self.body = body
 
 
class StopRequested(Exception):
    pass
 
 
class WarframeMarketGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Warframe Market — Syndicate Trader")
        self.root.geometry("720x860")
        self.root.configure(bg="#2c2f33")
        self.root.minsize(680, 800)
 
        self.driver = None
        self.username_ingame = ""
        self.user_slug = ""
        self.token = ""
        self.busy = False
        self._stop_requested = False
        self.item_id_by_slug = {}
        self.local_to_canonical = {}
        self.subtype_by_slug = {}   # slug -> subtype obbligatorio (es. "maxed"), None se non serve
        self.has_rank_by_slug = {}  # slug -> True se l'item accetta il campo rank
        self.item_name_to_slug = {}  # "Nome Leggibile" -> slug (popolato da sync)
        self._auto_refresh_job = None   # after() handle per il refresh automatico
 
        self.syndicate_vars = {name: tk.BooleanVar(value=True) for name in SYNDICATE_MODS}
 
        self.build_ui()
        # Chiusura window → chiude anche Chrome
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.load_and_autoconnect()
 
    # =========================================================================
    # BUILD UI
    # =========================================================================
    def build_ui(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "Horizontal.TProgressbar",
            troughcolor="#23272a", background="#43b581",
            bordercolor="#23272a", lightcolor="#43b581", darkcolor="#43b581",
        )
 
        # --- Token ---
        token_frame = tk.LabelFrame(
            self.root, text=" Autenticazione sessione (JWT cookie) ",
            fg="white", bg="#2c2f33", padx=12, pady=8,
        )
        token_frame.pack(pady=(10, 4), fill="x", padx=20)
        tk.Label(token_frame, text="Token JWT corrente:", fg="white", bg="#2c2f33").pack(anchor="w")
        self.entry_token = tk.Entry(
            token_frame, bg="#23272a", fg="white", insertbackground="white", relief="flat"
        )
        self.entry_token.pack(pady=6, ipady=5, fill="x")
        self.btn_connect = tk.Button(
            token_frame, text="Aggiorna Token e Salva",
            bg="#7289da", fg="white", activebackground="#5f73bc", activeforeground="white",
            command=self.start_connect_thread, bd=0, padx=14, pady=6,
        )
        self.btn_connect.pack(anchor="e")
 
        self.status_label = tk.Label(
            self.root, text="Non connesso", fg="#ffffff", bg="#2c2f33", anchor="w"
        )
        self.status_label.pack(fill="x", padx=22)
 
        # --- Checkbox Syndicate ---
        syn_outer = tk.LabelFrame(
            self.root, text=" Syndicate attive ",
            fg="white", bg="#2c2f33", padx=10, pady=6,
        )
        syn_outer.pack(pady=(6, 4), fill="x", padx=20)
        names = list(SYNDICATE_MODS.keys())
        cols = 3
        for i, name in enumerate(names):
            tk.Checkbutton(
                syn_outer, text=name, variable=self.syndicate_vars[name],
                fg="white", bg="#2c2f33",
                activebackground="#2c2f33", activeforeground="#43b581",
                selectcolor="#23272a", anchor="w",
            ).grid(row=i // cols, column=i % cols, sticky="w", padx=6, pady=1)
        sel_frame = tk.Frame(syn_outer, bg="#2c2f33")
        rows_used = (len(names) + cols - 1) // cols
        sel_frame.grid(row=rows_used, column=0, columnspan=cols, sticky="e", pady=(4, 0))
        tk.Button(
            sel_frame, text="Tutte", bg="#4f545c", fg="white",
            activebackground="#36393f", activeforeground="white", bd=0, padx=8, pady=3,
            command=lambda: [v.set(True) for v in self.syndicate_vars.values()],
        ).pack(side="left", padx=(0, 4))
        tk.Button(
            sel_frame, text="Nessuna", bg="#4f545c", fg="white",
            activebackground="#36393f", activeforeground="white", bd=0, padx=8, pady=3,
            command=lambda: [v.set(False) for v in self.syndicate_vars.values()],
        ).pack(side="left")
 
        # --- Impostazioni ---
        settings_frame = tk.LabelFrame(
            self.root, text=" Impostazioni ",
            fg="white", bg="#2c2f33", padx=12, pady=6,
        )
        settings_frame.pack(pady=(4, 4), fill="x", padx=20)
 
        # Riga soglia
        row1 = tk.Frame(settings_frame, bg="#2c2f33")
        row1.pack(fill="x", pady=(0, 4))
        tk.Label(row1, text="Soglia minima pubblicazione:", fg="#cccccc", bg="#2c2f33").pack(side="left")
        self.threshold_var = tk.IntVar(value=10)
        vcmd = (self.root.register(lambda s: s.isdigit() or s == ""), "%P")
        tk.Entry(
            row1, textvariable=self.threshold_var, width=5,
            bg="#23272a", fg="white", insertbackground="white", relief="flat",
            justify="center", validate="key", validatecommand=vcmd,
        ).pack(side="left", padx=6, ipady=3)
        tk.Label(row1, text="PL  (nasconde mod con 2+ venditori sotto soglia)", fg="#666a70", bg="#2c2f33",
                 font=("Helvetica", 8)).pack(side="left")
 
        # Riga refresh automatico
        row2 = tk.Frame(settings_frame, bg="#2c2f33")
        row2.pack(fill="x")
        tk.Label(row2, text="Aggiorna prezzi ogni:", fg="#cccccc", bg="#2c2f33").pack(side="left")
        self.refresh_var = tk.IntVar(value=DEFAULT_REFRESH_MINUTES)
        tk.Entry(
            row2, textvariable=self.refresh_var, width=5,
            bg="#23272a", fg="white", insertbackground="white", relief="flat",
            justify="center", validate="key", validatecommand=vcmd,
        ).pack(side="left", padx=6, ipady=3)
        tk.Label(row2, text="minuti  (0 = disabilitato)", fg="#666a70", bg="#2c2f33",
                 font=("Helvetica", 8)).pack(side="left")
        self.lbl_next_refresh = tk.Label(
            row2, text="", fg="#43b581", bg="#2c2f33", font=("Helvetica", 8)
        )
        self.lbl_next_refresh.pack(side="right")
 
        # --- Ricerca & Vendi singolo oggetto ---
        search_frame = tk.LabelFrame(
            self.root, text=" Vendi oggetto singolo ",
            fg="white", bg="#2c2f33", padx=10, pady=6,
        )
        search_frame.pack(pady=(4, 4), fill="x", padx=20)
 
        # Riga ricerca
        srow1 = tk.Frame(search_frame, bg="#2c2f33")
        srow1.pack(fill="x", pady=(0, 4))
        tk.Label(srow1, text="Cerca:", fg="#cccccc", bg="#2c2f33").pack(side="left")
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", self._on_search_change)
        self.entry_search = tk.Entry(
            srow1, textvariable=self.search_var,
            bg="#23272a", fg="white", insertbackground="white", relief="flat",
        )
        self.entry_search.pack(side="left", padx=6, ipady=4, fill="x", expand=True)
 
        # Prezzo manuale e bottone vendi
        tk.Label(srow1, text="Prezzo:", fg="#cccccc", bg="#2c2f33").pack(side="left")
        self.sell_price_var = tk.IntVar(value=15)
        vcmd2 = (self.root.register(lambda s: s.isdigit() or s == ""), "%P")
        tk.Entry(
            srow1, textvariable=self.sell_price_var, width=5,
            bg="#23272a", fg="white", insertbackground="white", relief="flat",
            justify="center", validate="key", validatecommand=vcmd2,
        ).pack(side="left", padx=4, ipady=4)
        tk.Label(srow1, text="PL", fg="#cccccc", bg="#2c2f33").pack(side="left")
 
        self.btn_sell_single = tk.Button(
            srow1, text="\U0001f4e4 Vendi",
            font=("Helvetica", 9, "bold"),
            bg="#7289da", fg="white",
            activebackground="#5f73bc", activeforeground="white",
            state="disabled", command=self.sell_single_item, bd=0, padx=10, pady=4,
        )
        self.btn_sell_single.pack(side="left", padx=(6, 0))
 
        # Listbox suggerimenti
        self.search_listbox = tk.Listbox(
            search_frame,
            bg="#23272a", fg="white", selectbackground="#7289da",
            relief="flat", height=4, font=("Consolas", 9),
            activestyle="none",
        )
        self.search_listbox.pack(fill="x")
        self.search_listbox.bind("<<ListboxSelect>>", self._on_suggestion_select)
        self._search_selected_slug = None  # slug selezionato dalla listbox
        # --- Reliquie Varzia ---
        varzia_frame = tk.Frame(self.root, bg="#2c2f33")
        varzia_frame.pack(pady=(0, 4), fill="x", padx=20)
        self.btn_varzia = tk.Button(
            varzia_frame, text="🔮 Reliquie Varzia disponibili (Aya)",
            font=("Helvetica", 9, "bold"),
            bg="#9b59b6", fg="white", activebackground="#7d3c98", activeforeground="white",
            state="disabled", command=self.start_varzia_thread, bd=0, pady=7,
        )
        self.btn_varzia.pack(fill="x")
        # --- Log ---
        self.log_box = tk.Text(
            self.root, height=9,
            bg="#23272a", fg="#ffffff", insertbackground="white",
            font=("Consolas", 9), state="disabled", bd=0, wrap="word",
        )
        self.log_box.pack(pady=(6, 2), padx=20, fill="both", expand=True)
 
        # --- Progress ---
        self.progress = ttk.Progressbar(
            self.root, orient="horizontal", mode="determinate",
            style="Horizontal.TProgressbar",
        )
        self.progress.pack(pady=(2, 4), padx=20, fill="x")
 
        # --- Riga 1: Carica / Stop / Panico ---
        btn_frame = tk.Frame(self.root, bg="#2c2f33")
        btn_frame.pack(pady=(4, 2), fill="x", padx=20)
 
        self.btn_start = tk.Button(
            btn_frame, text="\U0001f680 Carica / Aggiorna Mod",
            font=("Helvetica", 10, "bold"),
            bg="#43b581", fg="white", activebackground="#37996d", activeforeground="white",
            state="disabled", command=self.start_posting_thread, bd=0, pady=10,
        )
        self.btn_start.pack(side="left", fill="x", expand=True, padx=(0, 6))
 
        self.btn_stop = tk.Button(
            btn_frame, text="\u23f9 STOP",
            font=("Helvetica", 10, "bold"),
            bg="#4f545c", fg="white", activebackground="#36393f", activeforeground="white",
            state="disabled", command=self.request_stop, bd=0, pady=10, padx=14,
        )
        self.btn_stop.pack(side="left", padx=(0, 6))
 
        self.btn_panic = tk.Button(
            btn_frame, text="\U0001f6d1 PANICO",
            font=("Helvetica", 10, "bold"),
            bg="#f04747", fg="white", activebackground="#c83b3b", activeforeground="white",
            state="disabled", command=self.start_panic_thread, bd=0, pady=10,
        )
        self.btn_panic.pack(side="right", fill="x", expand=True)
 
        # --- Riga 2: Nascondi / Mostra / Chiudi ---
        vis_frame = tk.Frame(self.root, bg="#2c2f33")
        vis_frame.pack(pady=(2, 4), fill="x", padx=20)
 
        self.btn_hide = tk.Button(
            vis_frame, text="\U0001f648 Nascondi Ordini",
            font=("Helvetica", 9, "bold"),
            bg="#747f8d", fg="white", activebackground="#5a6475", activeforeground="white",
            state="disabled", command=self.start_hide_thread, bd=0, pady=8,
        )
        self.btn_hide.pack(side="left", fill="x", expand=True, padx=(0, 6))
 
        self.btn_show = tk.Button(
            vis_frame, text="\U0001f440 Mostra Ordini",
            font=("Helvetica", 9, "bold"),
            bg="#faa61a", fg="white", activebackground="#c8841a", activeforeground="white",
            state="disabled", command=self.start_show_thread, bd=0, pady=8,
        )
        self.btn_show.pack(side="left", fill="x", expand=True, padx=(0, 6))
 
        # Bottone Pulisci Log
        self.btn_clear = tk.Button(
            vis_frame, text="\U0001f9f9 Pulisci Log",
            font=("Helvetica", 9, "bold"),
            bg="#23272a", fg="#aaaaaa",
            activebackground="#36393f", activeforeground="white",
            command=self.clear_log, bd=0, pady=8, padx=10,
        )
        self.btn_clear.pack(side="right", padx=(6, 0))

        # Bottone Chiudi — chiude Chrome + app
        self.btn_quit = tk.Button(
            vis_frame, text="\U0001f6aa Chiudi",
            font=("Helvetica", 9, "bold"),
            bg="#23272a", fg="#cccccc",
            activebackground="#111315", activeforeground="white",
            command=self.on_close, bd=0, pady=8, padx=12,
        )
        self.btn_quit.pack(side="right")
 
    # =========================================================================
    # STOP
    # =========================================================================
    def request_stop(self):
        self._stop_requested = True
        self.log("\u23f9 Stop richiesto — in attesa del completamento dell'azione corrente...")
        self.ui_call(self.btn_stop.config, state="disabled")
 
    def check_stop(self):
        if self._stop_requested:
            raise StopRequested()
 
    def clear_log(self):
        """Svuota la casella di log."""
        self.log_box.configure(state="normal")
        self.log_box.delete("1.0", tk.END)
        self.log_box.configure(state="disabled")
 
    # =========================================================================
    # UI helpers
    # =========================================================================
    def ui_call(self, callback, *args, **kwargs):
        self.root.after(0, lambda: callback(*args, **kwargs))
 
    def log(self, text):
        def append():
            self.log_box.configure(state="normal")
            self.log_box.insert(tk.END, text + "\n")
            self.log_box.see(tk.END)
            self.log_box.configure(state="disabled")
        self.ui_call(append)
 
    def set_status(self, text):
        self.ui_call(self.status_label.config, text=text)
 
    def set_progress(self, value=None, maximum=None):
        def update():
            if maximum is not None:
                self.progress["maximum"] = maximum
            if value is not None:
                self.progress["value"] = value
        self.ui_call(update)
 
    def set_busy(self, busy):
        self.busy = busy
        if not busy:
            self._stop_requested = False
        def update():
            connected = bool(self.username_ingame)
            state_on = "normal" if connected and not busy else "disabled"
            self.btn_connect.config(state="disabled" if busy else "normal")
            self.btn_start.config(state=state_on)
            self.btn_varzia.config(state=state_on)
            self.btn_panic.config(state=state_on)
            self.btn_hide.config(state=state_on)
            self.btn_show.config(state=state_on)
            self.btn_stop.config(state="normal" if busy else "disabled")
            self.btn_sell_single.config(state=state_on)
        self.ui_call(update)
 
    def show_error(self, title, message):
        self.ui_call(messagebox.showerror, title, message)
 
    def get_min_price(self):
        try:
            return max(0, self.threshold_var.get())
        except Exception:
            return 10
 
    def get_active_mods(self):
        mods, seen = [], set()
        for syn_name, var in self.syndicate_vars.items():
            if var.get():
                for mod in SYNDICATE_MODS[syn_name]:
                    if mod not in seen:
                        seen.add(mod)
                        mods.append(mod)
        return mods
 
    # =========================================================================
    # Config
    # =========================================================================
    def load_and_autoconnect(self):
        if not os.path.exists(CONFIG_FILE):
            self.log("\u2139\ufe0f Nessun config.txt trovato. Incolla il token JWT e premi Aggiorna Token e Salva.")
            return
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                token = f.read().strip()
        except OSError as exc:
            self.log(f"\u26a0\ufe0f Impossibile leggere config.txt: {exc}")
            return
        if not token:
            self.log("\u2139\ufe0f config.txt esiste, ma è vuoto.")
            return
        self.entry_token.insert(0, token)
        self.log("\U0001f4c2 Token trovato in config.txt.")
        self.log("\U0001f916 Connessione automatica in corso...")
        self.start_connect_thread()
 
    def save_token(self, token):
        try:
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                f.write(token)
            self.log("\U0001f4be Token salvato in config.txt.")
        except OSError as exc:
            self.log(f"\u26a0\ufe0f Errore nel salvataggio locale: {exc}")
 
    # =========================================================================
    # Browser
    # =========================================================================
    def init_browser(self):
        if self.driver:
            return
        opts = Options()
        opts.add_argument("--headless=new")
        opts.add_argument("--disable-gpu")
        opts.add_argument("--disable-dev-shm-usage")
        opts.add_argument("--no-sandbox")
        opts.add_argument("--window-size=1365,768")
        opts.add_argument(
            "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
        )
        chrome_binary = next((c for c in CHROME_BINARY_CANDIDATES if os.path.exists(c)), None)
        if chrome_binary:
            opts.binary_location = chrome_binary
            self.log(f"Chrome trovato: {chrome_binary}")
        try:
            self.driver = webdriver.Chrome(options=opts)
            self.driver.set_script_timeout(45)
            self.driver.get(SITE_URL)
            self._set_cookie()
            time.sleep(3)
        except WebDriverException as exc:
            self.driver = None
            raise RuntimeError(
                "Impossibile avviare Chrome headless. Verifica che Google Chrome "
                "sia installato e che Selenium possa trovare ChromeDriver."
            ) from exc
 
    def _set_cookie(self):
        if not self.driver or not self.token:
            return
        try:
            self.driver.delete_cookie("JWT")
        except WebDriverException:
            pass
        self.driver.add_cookie({
            "name": "JWT", "value": self.token,
            "domain": ".warframe.market", "path": "/", "secure": True,
        })
 
    def quit_browser(self):
        if self.driver:
            try:
                self.driver.quit()
            except Exception:
                pass
            self.driver = None
 
    # =========================================================================
    # CORE API
    # =========================================================================
    def api_request(self, method, endpoint, payload=None):
        if not self.driver:
            raise ApiError("Browser Selenium non inizializzato.")
        script = """
            const callback = arguments[arguments.length - 1];
            const method   = arguments[0];
            const url      = arguments[1];
            const payload  = arguments[2];
            const token    = arguments[3];
            const options = {
                method,
                credentials: "include",
                headers: {
                    "Accept":        "application/json",
                    "Language":      "en",
                    "Platform":      "pc",
                    "Crossplay":     "true",
                    "Authorization": "JWT " + token
                }
            };
            if (payload !== null) {
                options.headers["Content-Type"] = "application/json";
                options.body = JSON.stringify(payload);
            }
            fetch(url, options)
                .then(async (r) => {
                    const text = await r.text();
                    let body = null;
                    try { body = text ? JSON.parse(text) : null; } catch(e) { body = { raw: text }; }
                    callback({ ok: r.ok, status: r.status, body });
                })
                .catch((e) => callback({ ok: false, status: 0, body: { error: String(e) } }));
        """
        result = self.driver.execute_async_script(script, method, BASE_URL + endpoint, payload, self.token)
        if not result:
            raise ApiError("Nessuna risposta dal browser.", status=0)
        status = result.get("status")
        body   = result.get("body")
        if not result.get("ok"):
            if status in (401, 403):
                raise ApiError("Token scaduto/non valido.", status=status, body=body)
            raise ApiError(f"Errore API HTTP {status}.", status=status, body=body)
        return body or {}
 
    def api_get(self, ep):          return self.api_request("GET",    ep)
    def api_post(self, ep, p):      return self.api_request("POST",   ep, p)
    def api_delete(self, ep):       return self.api_request("DELETE", ep)
    def api_put(self, ep, p):       return self.api_request("PUT",    ep, p)
    def api_patch(self, ep, p):     return self.api_request("PATCH",  ep, p)
 
    # =========================================================================
    # SYNC DATABASE
    # =========================================================================
    def sync_item_database(self):
        self.log("\U0001f504 Sincronizzazione database oggetti da GET /items...")
        all_items = self.api_get("/items").get("data", [])
        if not all_items:
            raise ApiError("GET /items ha restituito una lista vuota.")
        server_index = {}
        for item in all_items:
            slug = item.get("slug") or item.get("url_name") or ""
            item_id = item.get("id")
            # subtypes: lista di valori validi es. ["maxed"], obbligatoria se presente
            subtypes    = item.get("subtypes") or []
            # mod_max_rank presente e > 0 → item accetta campo rank nel payload
            max_rank    = item.get("mod_max_rank") or item.get("modMaxRank") or 0
            if slug and item_id:
                server_index[slug.replace("_", "-").lower()] = (slug, item_id, subtypes, max_rank)
        # Popola il database completo nomi→slug per la ricerca globale
        for norm_key, (slug, iid, subtypes, max_rank) in server_index.items():
            self.item_id_by_slug[slug] = iid
            self.subtype_by_slug[slug] = subtypes[0] if subtypes else None
            self.has_rank_by_slug[slug] = (max_rank is not None and max_rank > 0)
            readable = slug.replace("-", " ").title()
            self.item_name_to_slug[readable.lower()] = slug
 
        all_local_keys = {mod for mods in SYNDICATE_MODS.values() for mod in mods}
        found, missing = 0, []
        for key in all_local_keys:
            norm = key.replace("_", "-").lower()
            if norm in server_index:
                slug, iid, subtypes, max_rank = server_index[norm]
                self.local_to_canonical[key] = slug
                found += 1
            else:
                self.log(f"  \u26a0\ufe0f Slug non trovato: '{key}'")
                missing.append(key)
        self.log(
            f"\u2705 {found}/{len(all_local_keys)} mod mappate."
            + (f" ({len(missing)} mancanti)" if missing else "")
        )
 
    # =========================================================================
    # CONNECT
    # =========================================================================
    def start_connect_thread(self):
        if self.busy:
            return
        self.set_busy(True)
        threading.Thread(target=self.run_connect, daemon=True).start()
 
    def run_connect(self):
        self.token = self.entry_token.get().strip()
        self.username_ingame = ""
        self.user_slug = ""
        if not self.token:
            self.show_error("Errore", "Il campo Token JWT è vuoto.")
            self.log("\u274c Token mancante.")
            self.set_status("Non connesso")
            self.set_busy(False)
            return
        self.log("\U0001f310 Avvio Chrome headless...")
        try:
            self.init_browser()
            self._set_cookie()
            self.log("\U0001f50d Verifica profilo tramite /me...")
            user = self.api_get("/me").get("data", {})
            username = user.get("ingameName") or user.get("ingame_name")
            if not username:
                raise ApiError("Risposta /me valida ma ingameName non trovato.")
            self.username_ingame = username
            self.user_slug = user.get("slug") or username.lower()
            self.save_token(self.token)
            self.set_status(f"Connesso come {self.username_ingame}")
            self.log(f"\u2705 Autenticato come: {self.username_ingame}")
            self.sync_item_database()
        except Exception as exc:
            self.username_ingame = ""
            self.set_status("Autenticazione fallita")
            self.log(f"\u274c Connessione fallita: {exc}")
            self.show_error("Errore autenticazione",
                            "Token scaduto, non valido o bloccato da Cloudflare.")
        finally:
            self.set_busy(False)
 
    # =========================================================================
    # FETCH PRICE  (ritorna item_id, best_price | None se skip)
    # =========================================================================
    def fetch_item_price(self, local_key, min_price):
        """
        Ritorna (item_id, price, subtype).
        price=None → mercato svenduto, nascondi l'ordine.
        Logica prezzi:
          - Si pubblica SEMPRE al prezzo minimo di mercato.
          - Si nasconde solo se 2+ venditori in-game sono SOTTO la soglia.
          - Se c'è 1 solo venditore sotto soglia lo ignoriamo e prendiamo
            il minimo tra i venditori sopra soglia (o DEFAULT_PRICE se vuoto).
        """
        slug = self.local_to_canonical.get(local_key)
        if not slug:
            raise ApiError(f"Slug non trovato per '{local_key}'.")
        item_id = self.item_id_by_slug.get(slug)
        if not item_id:
            raise ApiError(f"ItemId mancante per slug '{slug}'.")
        subtype  = self.subtype_by_slug.get(slug)   # None se non richiesto
        has_rank = self.has_rank_by_slug.get(slug, False)  # False per weapon/set/ecc.
        orders = self.api_get(f"/orders/item/{slug}").get("data", [])
        ingame = [
            o for o in orders
            if o.get("type") == "sell"
            and o.get("user", {}).get("status") == "ingame"
            and isinstance(o.get("platinum"), int)
        ]
        if not ingame:
            return item_id, DEFAULT_PRICE, subtype, has_rank

        market_min = min(o["platinum"] for o in ingame)
        sellers_at_min = [o for o in ingame if o["platinum"] == market_min]

        # 2+ venditori al prezzo minimo E quel prezzo è sotto soglia → nascondi
        if market_min < min_price and len(sellers_at_min) >= 2:
            return item_id, None, subtype, has_rank

        # 1 solo venditore sotto soglia: ignoralo, prendi il minimo sopra soglia
        if market_min < min_price:
            above = sorted(o["platinum"] for o in ingame if o["platinum"] >= min_price)
            price = above[0] if above else DEFAULT_PRICE
        else:
            price = market_min  # pubblica al minimo di mercato

        return item_id, price, subtype, has_rank
 
    # =========================================================================
    # POSTING  (fase 1: raccolta prezzi → ordina desc → fase 2: pubblica)
    # =========================================================================
    def start_posting_thread(self):
        if self.busy:
            return
        self.set_busy(True)
        threading.Thread(target=self.run_posting, daemon=True).start()
 
    def run_posting(self, silent=False):
        """
        silent=True → usato dal refresh automatico, non mostra messaggi d'inizio.
        """
        active_mods = self.get_active_mods()
        if not active_mods:
            self.log("\u26a0\ufe0f Nessuna syndicate selezionata.")
            self.set_busy(False)
            return
        min_price = self.get_min_price()
        if not silent:
            active_syn = [n for n, v in self.syndicate_vars.items() if v.get()]
            self.log("")
            self.log(f"\U0001f680 {len(active_mods)} mod da {', '.join(active_syn)} | soglia {min_price} PL")
        if not self.item_id_by_slug:
            try:
                self.sync_item_database()
            except ApiError as exc:
                self.log(f"\u274c Sync fallita: {exc}")
                self.set_busy(False)
                return
 
        # --- FASE 1: raccolta prezzi ---
        self.set_progress(0, len(active_mods))
        priced, skipped_low, skipped_miss = [], [], []
        for i, key in enumerate(active_mods, 1):
            name = key.replace("-", " ").title()
            try:
                self.check_stop()
            except StopRequested:
                self.log(f"\u23f9 Stop durante raccolta prezzi.")
                self.set_busy(False)
                return
            if key not in self.local_to_canonical:
                skipped_miss.append(name)
                self.set_progress(i)
                continue
            try:
                item_id, price, subtype, has_rank = self.fetch_item_price(key, min_price)
                if price is None:
                    skipped_low.append(name)
                else:
                    priced.append((price, key, item_id, subtype, has_rank))
            except ApiError as exc:
                self.log(f"  \u26a0\ufe0f {name}: {exc}")
                skipped_miss.append(name)
            self.set_progress(i)
            time.sleep(REQUEST_DELAY_SECONDS)
 
        priced.sort(key=lambda x: x[0], reverse=True)  # più costose prima
        self.log(f"\U0001f4ca {len(priced)} da pubblicare | {len(skipped_low)} sotto soglia | {len(skipped_miss)} non trovate")
        if skipped_low:
            self.log(f"  \U0001f648 Nascosti (sotto {min_price} PL): {', '.join(skipped_low)}")
 
        if not priced:
            self.log("\u2139\ufe0f Nessuna mod da pubblicare.")
            self.set_busy(False)
            return
 
        # --- FASE 2: pubblica in ordine di prezzo decrescente ---
        self.log(f"\U0001f4e4 Pubblicazione {len(priced)} mod (dalla più cara)...")
        self.set_progress(0, len(priced))
        ok = fail = 0
        for i, (price, key, item_id, subtype, has_rank) in enumerate(priced, 1):
            name = key.replace("-", " ").title()
            try:
                self.check_stop()
            except StopRequested:
                self.log(f"\u23f9 Stop — {ok}/{len(priced)} pubblicate.")
                self.set_busy(False)
                return
            try:
                post_payload = {
                    "itemId": item_id, "type": "sell",
                    "platinum": int(price), "quantity": 1,
                    "visible": True,
                }
                # rank va inviato SOLO se l'item ha mod_max_rank > 0
                # (weapon/set/blueprint ecc. → 400 "rank notAllowed")
                if has_rank:
                    post_payload["rank"] = 0
                if subtype:
                    post_payload["subtype"] = subtype
                try:
                    self.api_post("/order", post_payload)
                except ApiError as retry_exc:
                    # Alcune mod hanno rank obbligatorio ma /items non lo restituisce →
                    # has_rank risulta False. Se la risposta dice "rank required", riprova.
                    if retry_exc.status == 400 and self._rank_required(retry_exc.body):
                        post_payload["rank"] = 0
                        slug = self.local_to_canonical.get(key)
                        if slug:
                            self.has_rank_by_slug[slug] = True  # memorizza per i prossimi giri
                        self.api_post("/order", post_payload)
                        self.log(f"  ↩ {name}: rank auto-rilevato e aggiunto.")
                    else:
                        raise
                self.log(f"[{i}/{len(priced)}] \u2705 {name} — {price} PL")
                ok += 1
            except ApiError as exc:
                self.log(f"[{i}/{len(priced)}] \u26a0\ufe0f {name}: {exc}")
                if exc.body:
                    self.log(f"           Body: {exc.body}")
                fail += 1
            self.set_progress(i)
            time.sleep(REQUEST_DELAY_SECONDS)
 
        self.log(f"\U0001f389 {ok} pubblicate" + (f", {fail} errori." if fail else "."))
        self.set_busy(False)
        self._schedule_next_refresh()
 
    # =========================================================================
    # AGGIORNAMENTO AUTOMATICO PREZZI
    # Ogni N minuti aggiorna tutti gli ordini già attivi dell'utente
    # con il prezzo di mercato corrente, senza ricreare gli ordini.
    # =========================================================================
    def _schedule_next_refresh(self):
        """Pianifica il prossimo aggiornamento automatico dei prezzi."""
        if self._auto_refresh_job:
            self.root.after_cancel(self._auto_refresh_job)
            self._auto_refresh_job = None
        try:
            minutes = self.refresh_var.get()
        except Exception:
            minutes = 0
        if minutes <= 0:
            self.ui_call(self.lbl_next_refresh.config, text="")
            return
        ms = minutes * 60 * 1000
        self._auto_refresh_job = self.root.after(ms, self._run_auto_refresh)
        self.ui_call(self.lbl_next_refresh.config, text=f"Prossimo aggiornamento in {minutes} min")
 
    def _run_auto_refresh(self):
        """Chiamata da root.after() — avvia l'aggiornamento prezzi in background."""
        self._auto_refresh_job = None
        if self.busy or not self.username_ingame:
            self._schedule_next_refresh()
            return
        self.log("")
        self.log("\U0001f504 Aggiornamento automatico prezzi in corso...")
        self.set_busy(True)
        threading.Thread(target=self._thread_auto_refresh, daemon=True).start()
 
    def _thread_auto_refresh(self):
        """
        Recupera gli ordini attivi dell'utente, calcola il nuovo prezzo
        di mercato per ciascuno e aggiorna via PUT /order/{id}.
        Se il prezzo di mercato è sotto soglia → nasconde l'ordine.
        """
        min_price = self.get_min_price()
        try:
            response = self.api_get(f"/orders/user/{self.user_slug}")
            my_orders = [o for o in response.get("data", []) if o.get("type") == "sell"]
            if not my_orders:
                self.log("\u2139\ufe0f Nessun ordine attivo trovato.")
                self.set_busy(False)
                self._schedule_next_refresh()
                return
 
            self.log(f"\U0001f4cb Aggiornamento {len(my_orders)} ordini attivi...")
            self.set_progress(0, len(my_orders))
 
            # Costruisci mappa inversa itemId → local_key
            id_to_local = {}
            for local_key, slug in self.local_to_canonical.items():
                iid = self.item_id_by_slug.get(slug)
                if iid:
                    id_to_local[iid] = local_key
 
            updated = hidden = skipped = errors = 0
            for i, order in enumerate(my_orders, 1):
                try:
                    self.check_stop()
                except StopRequested:
                    self.log(f"\u23f9 Stop refresh automatico. Aggiornati: {updated}.")
                    self.set_busy(False)
                    return
 
                order_id  = order.get("id")
                item_id   = order.get("itemId")
                local_key = id_to_local.get(item_id)
                name      = self._resolve_order_name(order)
 
                if not order_id or not local_key:
                    skipped += 1
                    self.set_progress(i)
                    time.sleep(REQUEST_DELAY_SECONDS)
                    continue
 
                try:
                    _, new_price, _sub, _hr = self.fetch_item_price(local_key, min_price)
                    if new_price is None:
                        # Mercato svenduto → nascondi ordine
                        self._put_order(order_id, order, visible=False)
                        self.log(f"[{i}/{len(my_orders)}] \U0001f648 {name} nascosta (mercato sotto {min_price} PL)")
                        hidden += 1
                    elif int(new_price) != int(order.get("platinum", 0)):
                        # Prezzo cambiato → aggiorna
                        self._put_order(order_id, order, platinum=int(new_price), visible=True)
                        self.log(f"[{i}/{len(my_orders)}] \U0001f4b0 {name}: {order.get('platinum')} → {new_price} PL")
                        updated += 1
                    else:
                        # Prezzo invariato
                        skipped += 1
                except ApiError as exc:
                    self.log(f"[{i}/{len(my_orders)}] \u26a0\ufe0f {name}: {exc}")
                    errors += 1
 
                self.set_progress(i)
                time.sleep(REQUEST_DELAY_SECONDS)
 
            self.log(
                f"\u2705 Refresh completato: {updated} aggiornati, "
                f"{hidden} nascosti, {skipped} invariati"
                + (f", {errors} errori." if errors else ".")
            )
        except Exception as exc:
            self.log(f"\u274c Errore refresh automatico: {exc}")
        finally:
            self.set_busy(False)
            self._schedule_next_refresh()
 
    # =========================================================================
    # PUT /order/{id}  —  helper centralizzato
    # Payload corretto per API v2:
    #   order_id  (stringa, campo body OBBLIGATORIO su alcuni endpoint v2)
    #   platinum, quantity, rank, visible
    # =========================================================================
    def _put_order(self, order_id, order_data, platinum=None, visible=None):
        """
        PATCH {visible} → solo cambio visibilità (payload minimo, no campi obbligatori).
        PUT completo → aggiornamento prezzo (richiede tutti i campi).
        Payload PUT conforme alla v2: order_id, platinum, quantity, rank, visible.
        """
        if platinum is None:
            # Solo visibilità → PATCH parziale (nessun campo rank/platinum richiesto)
            return self.api_patch(
                f"/order/{order_id}",
                {"visible": visible if visible is not None else order_data.get("visible", True)},
            )
        # Aggiornamento prezzo → PUT completo
        payload = {
            "order_id": order_id,
            "platinum": int(platinum),
            "quantity": order_data.get("quantity") or 1,
            "rank":     order_data.get("rank") or 0,
            "visible":  visible if visible is not None else order_data.get("visible", True),
        }
        if order_data.get("subtype"):
            payload["subtype"] = order_data["subtype"]
        return self.api_put(f"/order/{order_id}", payload)
 
    # =========================================================================
    # PANIC
    # =========================================================================
    def start_panic_thread(self):
        if self.busy:
            return
        self.set_busy(True)
        threading.Thread(target=self.run_panic, daemon=True).start()
 
    def run_panic(self):
        self.set_progress(0, 1)
        self.log("")
        self.log("\U0001f6d1 RIMOZIONE D'EMERGENZA IN CORSO...")
        try:
            if not self.item_id_by_slug:
                self.sync_item_database()
            target_ids = set(self.item_id_by_slug.values())
            targets = [
                o for o in self.api_get(f"/orders/user/{self.user_slug}").get("data", [])
                if o.get("type") == "sell" and o.get("itemId") in target_ids
            ]
            if not targets:
                self.log("\u2139\ufe0f Nessun ordine da eliminare.")
                self.set_progress(1, 1)
                return
            self.set_progress(0, len(targets))
            for i, order in enumerate(targets, 1):
                try:
                    self.check_stop()
                except StopRequested:
                    self.log(f"\u23f9 Panico interrotto. Rimossi {i-1}/{len(targets)}.")
                    return
                oid  = order.get("id")
                name = self._resolve_order_name(order)
                if not oid:
                    self.set_progress(i)
                    continue
                try:
                    self.api_delete(f"/order/{oid}")
                    self.log(f"[{i}/{len(targets)}] \U0001f5d1\ufe0f {name}")
                except ApiError as exc:
                    self.log(f"[{i}/{len(targets)}] \u26a0\ufe0f {name}: {exc}")
                self.set_progress(i)
                time.sleep(REQUEST_DELAY_SECONDS)
            self.log("\U0001f512 Pulizia completata.")
        except Exception as exc:
            self.log(f"\u274c Errore Tasto Panico: {exc}")
            self.show_error("Errore Tasto Panico", str(exc))
        finally:
            self.set_busy(False)
 
    # =========================================================================
    # NASCONDI / MOSTRA  —  usa _put_order centralizzato
    # =========================================================================
    def start_hide_thread(self):
        if self.busy:
            return
        self.set_busy(True)
        threading.Thread(target=lambda: self.run_set_visibility(False), daemon=True).start()
 
    def start_show_thread(self):
        if self.busy:
            return
        self.set_busy(True)
        threading.Thread(target=lambda: self.run_set_visibility(True), daemon=True).start()
 
    def run_set_visibility(self, visible: bool):
        label = "NASCONDO" if not visible else "MOSTRO"
        emoji = "\U0001f648" if not visible else "\U0001f440"
        stato = "nascosti" if not visible else "visibili"
        self.set_progress(0, 1)
        self.log("")
        self.log(f"{emoji} {label} TUTTI GLI ORDINI DI VENDITA...")
        try:
            sell_orders = [
                o for o in self.api_get(f"/orders/user/{self.user_slug}").get("data", [])
                if o.get("type") == "sell"
            ]
            if not sell_orders:
                self.log("\u2139\ufe0f Nessun ordine di vendita trovato.")
                self.set_progress(1, 1)
                return
            to_update = [o for o in sell_orders if o.get("visible") != visible]
            if not to_update:
                self.log(f"\u2139\ufe0f Tutti gli ordini sono già {stato}.")
                self.set_progress(1, 1)
                return
            self.log(f"\U0001f4cb {len(to_update)} da aggiornare su {len(sell_orders)} totali...")
            self.set_progress(0, len(to_update))
            ok = fail = 0
            for i, order in enumerate(to_update, 1):
                try:
                    self.check_stop()
                except StopRequested:
                    self.log(f"\u23f9 Stop: {ok} aggiornati.")
                    return
                oid  = order.get("id")
                name = self._resolve_order_name(order)
                if not oid:
                    self.log(f"[{i}/{len(to_update)}] \u26a0\ufe0f {name}: ID mancante.")
                    fail += 1
                    self.set_progress(i)
                    continue
                try:
                    self._put_order(oid, order, visible=visible)
                    ok += 1
                except ApiError as exc:
                    self.log(f"[{i}/{len(to_update)}] \u26a0\ufe0f {name}: {exc}")
                    if exc.body:
                        self.log(f"           Body: {exc.body}")
                    fail += 1
                self.set_progress(i)
                time.sleep(REQUEST_DELAY_SECONDS)
            self.log(f"\u2705 {ok} ordini ora {stato}" + (f", {fail} errori." if fail else "."))
        except Exception as exc:
            self.log(f"\u274c Errore visibilità: {exc}")
            self.show_error("Errore visibilità ordini", str(exc))
        finally:
            self.set_busy(False)
 
    # =========================================================================
    # UTILITY
    # =========================================================================
    def item_name_from_id(self, item_id):
        for slug, iid in self.item_id_by_slug.items():
            if iid == item_id:
                return slug.replace("-", " ").title()
        return "Mod sconosciuta"
 
    def _resolve_order_name(self, order):
        iid = order.get("itemId")
        if iid and iid in self.item_id_by_slug.values():
            return self.item_name_from_id(iid)
        item_obj = order.get("item") or {}
        if isinstance(item_obj, dict):
            n = item_obj.get("name") or item_obj.get("slug") or ""
            if n:
                return n.replace("-", " ").title()
        raw = order.get("itemName") or order.get("item_name") or ""
        return raw.title() if raw else "Oggetto sconosciuto"
 
    # =========================================================================
    # UTILITY API
    # =========================================================================
    def _rank_required(self, body):
        """Ritorna True se l'errore 400 indica che 'rank' è obbligatorio."""
        try:
            return (
                isinstance(body, dict)
                and body.get("error", {}).get("inputs", {}).get("rank") == "app.field.required"
            )
        except Exception:
            return False

    def _fetch_preview_price(self, slug):
        """
        Calcola il prezzo di mercato per un dato slug (usato dall'anteprima ricerca).
        Stessa logica di fetch_item_price ma senza soglia (mostra sempre un valore).
        """
        orders = self.api_get(f"/orders/item/{slug}").get("data", [])
        ingame = [
            o for o in orders
            if o.get("type") == "sell"
            and o.get("user", {}).get("status") == "ingame"
            and isinstance(o.get("platinum"), int)
        ]
        if not ingame:
            return DEFAULT_PRICE
        return min(o["platinum"] for o in ingame)

    def _thread_update_price_preview(self, slug):
        """Thread in background: aggiorna sell_price_var con il prezzo di mercato."""
        try:
            price = self._fetch_preview_price(slug)
            self.ui_call(self.sell_price_var.set, price)
        except Exception:
            pass  # silenzioso — l'utente può sempre modificare il prezzo manualmente
    # =========================================================================
    # RELIQUIE VARZIA
    # =========================================================================
    def start_varzia_thread(self):
        if self.busy:
            return
        threading.Thread(target=self._thread_varzia_check, daemon=True).start()

    def _scrape_varzia_relics(self):
        """
        Scarica la pagina Varzia dal wiki e ritorna i slug WFM delle reliquie
        con spunta verde (table-yes) nella sezione Prime Resurgence.
        """
        url = "https://wiki.warframe.com/w/Varzia"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=20) as resp:
            html_content = resp.read().decode("utf-8", errors="replace")

        row_re   = re.compile(r'<tr[^>]*>(.*?)</tr>', re.DOTALL | re.IGNORECASE)
        yes_re   = re.compile(r'class="[^"]*table-yes[^"]*"', re.IGNORECASE)
        relic_re = re.compile(
            r'(Lith|Meso|Neo|Axi|Vanguard)\s+([A-Z]\d+)\s+Relic',
            re.IGNORECASE,
        )

        found, seen = [], set()
        for m in row_re.finditer(html_content):
            row_html = m.group(1)
            if not yes_re.search(row_html):
                continue
            r = relic_re.search(row_html)
            if r:
                slug = f"{r.group(1).lower()}-{r.group(2).lower()}-relic"
                if slug not in seen:
                    seen.add(slug)
                    found.append(slug)
        return found

    def _thread_varzia_check(self):
        self.log("🔮 Recupero reliquie Varzia disponibili dal wiki...")
        try:
            slugs = self._scrape_varzia_relics()
        except Exception as exc:
            self.log(f"❌ Errore scraping wiki: {exc}")
            return

        if not slugs:
            self.log("⚠️ Nessuna reliquia trovata (struttura wiki cambiata o nessuna attiva).")
            return

        self.log(f"📋 {len(slugs)} reliquie disponibili — recupero prezzi WFM...")
        results = []
        for slug in slugs:
            try:
                price = self._fetch_preview_price(slug)
                name  = slug.replace("-", " ").title()
                results.append((price, name, slug))
            except Exception as exc:
                self.log(f"  ⚠️ {slug}: {exc}")
            time.sleep(REQUEST_DELAY_SECONDS)

        results.sort(key=lambda x: x[0], reverse=True)
        self.ui_call(self._show_varzia_results, results)

    def _show_varzia_results(self, results):
        """Finestra con reliquie disponibili da Varzia ordinate per prezzo di mercato."""
        win = tk.Toplevel(self.root)
        win.title("🔮 Reliquie Varzia — Valore di Mercato")
        win.configure(bg="#2c2f33")
        win.geometry("440x520")
        win.resizable(True, True)

        tk.Label(
            win,
            text=f"{len(results)} reliquie disponibili, ordinate per prezzo",
            fg="#cccccc", bg="#2c2f33", font=("Helvetica", 9),
        ).pack(pady=(10, 4), padx=12)

        frame_tree = tk.Frame(win, bg="#2c2f33")
        frame_tree.pack(fill="both", expand=True, padx=12)

        cols = ("Reliquia", "Prezzo min (PL)")
        tree = ttk.Treeview(frame_tree, columns=cols, show="headings", height=22)
        tree.heading("Reliquia",        text="Reliquia")
        tree.heading("Prezzo min (PL)", text="Prezzo min (PL)")
        tree.column("Reliquia",        width=270)
        tree.column("Prezzo min (PL)", width=130, anchor="center")

        tree.tag_configure("high", foreground="#43b581")   # >30 PL  → verde
        tree.tag_configure("mid",  foreground="#faa61a")   # 15–30   → arancio
        tree.tag_configure("low",  foreground="#f04747")   # <15     → rosso

        sb = ttk.Scrollbar(frame_tree, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=sb.set)
        tree.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

        for price, name, _slug in results:
            tag = "high" if price > 30 else ("mid" if price >= 15 else "low")
            tree.insert("", tk.END, values=(name, f"{price} PL"), tags=(tag,))

        tk.Button(
            win, text="Chiudi", bg="#4f545c", fg="white",
            activebackground="#36393f", bd=0, padx=12, pady=6,
            command=win.destroy,
        ).pack(pady=(6, 10))

        if results:
            best = results[0]
            self.log(
                f"🔮 Varzia: analizzate {len(results)} reliquie — "
                f"la più cara: {best[1]} a {best[0]} PL"
            )
    # =========================================================================
    # RICERCA ITEM & VENDI SINGOLO
    # =========================================================================
    def _on_search_change(self, *_):
        """Aggiorna i suggerimenti nella listbox mentre l'utente digita."""
        query = self.search_var.get().strip().lower()
        self.search_listbox.delete(0, tk.END)
        self._search_selected_slug = None
        if len(query) < 2 or not self.item_name_to_slug:
            return
        # Ricerca fuzzy: prima i match che iniziano con la query, poi contengono
        starts = [n for n in self.item_name_to_slug if n.startswith(query)]
        contains = [n for n in self.item_name_to_slug if query in n and n not in starts]
        results = (starts + contains)[:12]
        for name in results:
            self.search_listbox.insert(tk.END, name.title())
 
    def _on_suggestion_select(self, event):
        """Seleziona un suggerimento dalla listbox e aggiorna il campo ricerca."""
        sel = self.search_listbox.curselection()
        if not sel:
            return
        chosen_display = self.search_listbox.get(sel[0])
        chosen_lower   = chosen_display.lower()
        self._search_selected_slug = self.item_name_to_slug.get(chosen_lower)
        # Aggiorna entry senza ri-triggerare la trace
        self.search_var.trace_remove("write", self.search_var.trace_info()[0][1])
        self.entry_search.delete(0, tk.END)
        self.entry_search.insert(0, chosen_display)
        self.search_var.trace_add("write", self._on_search_change)
        self.search_listbox.delete(0, tk.END)

        # Avvia anteprima prezzo di mercato in background
        if self._search_selected_slug and self.username_ingame and not self.busy:
            threading.Thread(
                target=self._thread_update_price_preview,
                args=(self._search_selected_slug,),
                daemon=True,
            ).start()

    def sell_single_item(self):
        """Mette in vendita l'oggetto selezionato dalla ricerca al prezzo indicato."""
        if self.busy:
            return
        slug = self._search_selected_slug
        if not slug:
            # Prova a risolvere il testo digitato direttamente
            txt = self.search_var.get().strip().lower()
            slug = self.item_name_to_slug.get(txt)
        if not slug:
            self.log("\u274c Nessun oggetto selezionato o nome non riconosciuto.")
            return
        try:
            price = int(self.sell_price_var.get())
        except Exception:
            self.log("\u274c Prezzo non valido.")
            return
        if price <= 0:
            self.log("\u274c Il prezzo deve essere maggiore di 0.")
            return
        self.set_busy(True)
        threading.Thread(
            target=lambda: self._thread_sell_single(slug, price),
            daemon=True,
        ).start()
 
    def _thread_sell_single(self, slug, price):
        item_id  = self.item_id_by_slug.get(slug)
        subtype  = self.subtype_by_slug.get(slug)
        has_rank = self.has_rank_by_slug.get(slug, False)
        name     = slug.replace("-", " ").title()
        if not item_id:
            self.log(f"\u274c ItemId non trovato per '{name}'. Riconnetti per sincronizzare.")
            self.set_busy(False)
            return
        try:
            payload = {
                "itemId":   item_id,
                "type":     "sell",
                "platinum": price,
                "quantity": 1,
                "visible":  True,
            }
            if has_rank:
                payload["rank"] = 0
            if subtype:
                payload["subtype"] = subtype
            try:
                self.api_post("/order", payload)
            except ApiError as retry_exc:
                if retry_exc.status == 400 and self._rank_required(retry_exc.body):
                    payload["rank"] = 0
                    self.has_rank_by_slug[slug] = True
                    self.api_post("/order", payload)
                    self.log(f"  ↩ {name}: rank auto-rilevato e aggiunto.")
                else:
                    raise
            self.log(f"\u2705 {name} messa in vendita a {price} PL.")
            # Reset ricerca
            self.ui_call(self.entry_search.delete, 0, tk.END)
            self.ui_call(self.search_listbox.delete, 0, tk.END)
            self._search_selected_slug = None
        except ApiError as exc:
            self.log(f"\u26a0\ufe0f Errore pubblicazione {name}: {exc}")
            if exc.body:
                self.log(f"           Body: {exc.body}")
        except Exception as exc:
            self.log(f"\u274c Errore inatteso: {exc}")
        finally:
            self.set_busy(False)
 
    # =========================================================================
    # CHIUSURA — garantisce che Chrome venga sempre terminato
    # =========================================================================
    def on_close(self):
        """Chiude Chrome e poi la finestra. Chiamato sia dal bottone che dalla X."""
        if self._auto_refresh_job:
            self.root.after_cancel(self._auto_refresh_job)
        self.log("\U0001f6aa Chiusura in corso — arresto Chrome...")
        # Forza stop di qualsiasi operazione
        self._stop_requested = True
        self.quit_browser()
        self.root.destroy()
 
 
if __name__ == "__main__":
    root = tk.Tk()
    app = WarframeMarketGUI(root)
    root.mainloop()