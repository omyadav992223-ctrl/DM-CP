"""
gui.py
=======
CustomTkinter graphical interface for the RSA Educational Prototype.

Responsibilities:
  - Build and layout all widgets
  - Connect button actions to the rsa.py / crypto_utils.py functions
  - Display keys, ciphertext, decrypted text, and status messages
  - Show/Hide key details
  - Open the "Show Mathematics" window
  - Handle all user errors gracefully (no raw tracebacks)

Design choices:
  - Dark modern theme (customtkinter "dark-blue" appearance)
  - Scrollable frame for the main content so it works on any screen size
  - Left column: message input + key information
  - Right column: encryption output + decryption output
  - Bottom: status bar + footer
"""

import threading
import customtkinter as ctk
from tkinter import messagebox, scrolledtext
import tkinter as tk

# Import our RSA implementation and utility functions.
from rsa import (
    RSAKeyPair,
    generate_keys,
    encrypt_message,
    decrypt_message,
    ciphertext_to_str,
    str_to_ciphertext,
)

# ─────────────────────────────────────────────────────────────────
# Global Appearance Settings
# ─────────────────────────────────────────────────────────────────

# Set the overall visual theme.  "dark-blue" gives a professional dark look.
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

# ─────────────────────────────────────────────────────────────────
# Colour Palette (kept in one place for easy tweaking)
# ─────────────────────────────────────────────────────────────────

CLR_BG          = "#1a1a2e"   # Main window background
CLR_CARD        = "#16213e"   # Card / panel background
CLR_CARD2       = "#0f3460"   # Slightly lighter card
CLR_ACCENT      = "#e94560"   # Highlight / accent (red-pink)
CLR_SUCCESS     = "#4ade80"   # Green — success messages
CLR_WARNING     = "#facc15"   # Yellow — warnings
CLR_ERROR       = "#f87171"   # Red — errors
CLR_TEXT        = "#e2e8f0"   # Primary text
CLR_SUBTEXT     = "#94a3b8"   # Secondary / muted text
CLR_BTN_PRI     = "#e94560"   # Primary button
CLR_BTN_PRI_HV  = "#c73652"   # Primary button hover
CLR_BTN_SEC     = "#0f3460"   # Secondary button
CLR_BTN_SEC_HV  = "#1a4a80"   # Secondary button hover
CLR_INPUT_BG    = "#0d1117"   # Text-box background
CLR_BORDER      = "#334155"   # Widget border / separator


# ─────────────────────────────────────────────────────────────────
# Helper: make a styled card frame
# ─────────────────────────────────────────────────────────────────

def make_card(parent, **kwargs) -> ctk.CTkFrame:
    """Return a styled rounded card frame."""
    defaults = dict(
        fg_color=CLR_CARD,
        corner_radius=12,
        border_width=1,
        border_color=CLR_BORDER,
    )
    defaults.update(kwargs)
    return ctk.CTkFrame(parent, **defaults)


def make_label(parent, text: str, font_size: int = 13,
               bold: bool = False, color: str = CLR_TEXT, **kwargs) -> ctk.CTkLabel:
    """Return a styled label."""
    weight = "bold" if bold else "normal"
    return ctk.CTkLabel(
        parent, text=text,
        font=ctk.CTkFont(family="Segoe UI", size=font_size, weight=weight),
        text_color=color, **kwargs
    )


def make_button(parent, text: str, command, primary: bool = True,
                width: int = 160, **kwargs) -> ctk.CTkButton:
    """Return a styled button (primary = accent colour, secondary = dark)."""
    fg   = CLR_BTN_PRI     if primary else CLR_BTN_SEC
    hv   = CLR_BTN_PRI_HV  if primary else CLR_BTN_SEC_HV
    return ctk.CTkButton(
        parent, text=text, command=command,
        fg_color=fg, hover_color=hv,
        font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
        corner_radius=8, height=38, width=width,
        text_color=CLR_TEXT, **kwargs
    )


def make_textbox(parent, height: int = 80, **kwargs) -> ctk.CTkTextbox:
    """Return a styled multi-line text box."""
    return ctk.CTkTextbox(
        parent,
        height=height,
        fg_color=CLR_INPUT_BG,
        border_color=CLR_BORDER,
        border_width=1,
        corner_radius=8,
        font=ctk.CTkFont(family="Consolas", size=12),
        text_color=CLR_TEXT,
        wrap="word",
        **kwargs
    )


# ─────────────────────────────────────────────────────────────────
# "Show Mathematics" popup window
# ─────────────────────────────────────────────────────────────────

class MathWindow(ctk.CTkToplevel):
    """
    A popup that displays the full RSA calculation trace for the current key pair.

    The teacher can read through the step-by-step computation live during the demo.
    """

    def __init__(self, parent, key: RSAKeyPair):
        super().__init__(parent)
        self.title("RSA Mathematics — Step-by-Step")
        self.geometry("680x700")
        self.resizable(True, True)
        self.configure(fg_color=CLR_BG)
        self.grab_set()   # Make it modal so the user focuses here.

        # Build the math text.
        math_text = self._build_math_text(key)

        # Title label.
        make_label(self, "RSA Key Generation — Mathematics",
                   font_size=16, bold=True, color=CLR_ACCENT).pack(
            padx=20, pady=(20, 4))
        make_label(self, "All values computed from your current key pair",
                   font_size=12, color=CLR_SUBTEXT).pack(padx=20, pady=(0, 12))

        # Scrollable text area for the maths.
        text_box = ctk.CTkTextbox(
            self,
            fg_color=CLR_INPUT_BG,
            border_color=CLR_BORDER,
            border_width=1,
            corner_radius=8,
            font=ctk.CTkFont(family="Consolas", size=12),
            text_color=CLR_TEXT,
            wrap="none",
        )
        text_box.pack(padx=20, pady=(0, 12), fill="both", expand=True)
        text_box.insert("1.0", math_text)
        text_box.configure(state="disabled")  # Read-only.

        make_button(self, "Close", command=self.destroy, primary=False, width=120).pack(
            pady=(0, 16))

    def _build_math_text(self, k: RSAKeyPair) -> str:
        """Format the RSA calculation trace as a readable string."""
        lines = [
            "═" * 58,
            "  RSA KEY GENERATION — STEP-BY-STEP CALCULATIONS",
            "═" * 58,
            "",
            "STEP 1 — Choose Two Prime Numbers",
            "──────────────────────────────────",
            f"  p = {k.p}",
            f"  q = {k.q}",
            "",
            "STEP 2 — Calculate the Modulus n",
            "──────────────────────────────────",
            "  n = p × q",
            f"    = {k.p}",
            f"    × {k.q}",
            f"    = {k.n}",
            "",
            "STEP 3 — Calculate Euler's Totient φ(n)",
            "──────────────────────────────────────────",
            "  φ(n) = (p - 1) × (q - 1)",
            f"       = ({k.p} - 1) × ({k.q} - 1)",
            f"       = {k.p - 1} × {k.q - 1}",
            f"       = {k.phi}",
            "",
            "STEP 4 — Choose Public Exponent e",
            "───────────────────────────────────",
            f"  e = {k.e}",
            f"  Verify: gcd(e, φ(n)) = gcd({k.e}, {k.phi})",
            f"        = 1  ✓  (e and φ(n) are coprime)",
            "",
            "STEP 5 — Calculate Private Exponent d",
            "───────────────────────────────────────",
            "  d = modular_inverse(e, φ(n))",
            f"    = modular_inverse({k.e}, {k.phi})",
            f"    = {k.d}",
            "",
            "  Verify: (e × d) mod φ(n) = 1",
            f"        = ({k.e} × {k.d}) mod {k.phi}",
            f"        = {(k.e * k.d) % k.phi}  ✓",
            "",
            "═" * 58,
            "  KEY SUMMARY",
            "═" * 58,
            "",
            f"  Public Key  (e, n) = ({k.e}, {k.n})",
            f"  Private Key (d, n) = ({k.d}, {k.n})",
            "",
            "═" * 58,
            "  ENCRYPTION / DECRYPTION FORMULAS",
            "═" * 58,
            "",
            "  Encryption:   c = m^e  mod n",
            "                  = m^" + str(k.e) + "  mod n",
            "",
            "  Decryption:   m = c^d  mod n",
            "                  = c^" + str(k.d) + "  mod n",
            "",
            "  Python code:  pow(m, e, n)   ← fast modular exponentiation",
            "                pow(c, d, n)",
            "",
            "═" * 58,
            "  WHY DECRYPTION WORKS — Euler's Theorem",
            "═" * 58,
            "",
            "  By Euler's theorem:",
            "    m^φ(n) ≡ 1  (mod n)   for any m coprime with n",
            "",
            "  Since e × d ≡ 1 (mod φ(n)), we can write:",
            "    e × d = 1 + k × φ(n)  for some integer k",
            "",
            "  Therefore:",
            "    (m^e)^d = m^(e×d) = m^(1 + k·φ(n))",
            "            = m × (m^φ(n))^k",
            "            ≡ m × 1^k",
            "            ≡ m  (mod n)  ✓",
            "",
            "═" * 58,
        ]
        return "\n".join(lines)


# ─────────────────────────────────────────────────────────────────
# "How It Works" educational popup
# ─────────────────────────────────────────────────────────────────

class HowItWorksWindow(ctk.CTkToplevel):
    """Simple educational popup explaining RSA in student-friendly language."""

    CONTENT = """\
╔══════════════════════════════════════════════════════════╗
║         HOW RSA ENCRYPTION WORKS — SIMPLE GUIDE         ║
╚══════════════════════════════════════════════════════════╝

RSA is a Public-Key Cryptosystem invented in 1977 by
Rivest, Shamir, and Adleman (R-S-A).

It uses TWO related keys:
  • Public Key  → shared openly, used to ENCRYPT
  • Private Key → kept secret, used to DECRYPT

Anyone can encrypt a message using your public key,
but ONLY you (with the private key) can decrypt it.

────────────────────────────────────────────────────────────
STEP 1 — Choose Two Prime Numbers  (p and q)
────────────────────────────────────────────────────────────
  Pick two large prime numbers p and q.
  Keep them secret — they are the "seed" of the key pair.

  Example: p = 61,  q = 53

────────────────────────────────────────────────────────────
STEP 2 — Compute the Modulus  n = p × q
────────────────────────────────────────────────────────────
  n = 61 × 53 = 3233

  n is part of BOTH keys.  Its security comes from the fact
  that factoring a large n back into p and q is extremely hard.

────────────────────────────────────────────────────────────
STEP 3 — Euler's Totient  φ(n) = (p-1)(q-1)
────────────────────────────────────────────────────────────
  φ(n) = 60 × 52 = 3120

  φ(n) counts how many numbers from 1 to n are coprime with n.
  This number is kept SECRET — it is what makes the key work.

────────────────────────────────────────────────────────────
STEP 4 — Choose Public Exponent  e
────────────────────────────────────────────────────────────
  Choose e such that:
    • 1 < e < φ(n)
    • gcd(e, φ(n)) = 1   (e and φ(n) share no common factor)

  Standard choice: e = 65537   (used in real TLS/SSL)

────────────────────────────────────────────────────────────
STEP 5 — Compute Private Exponent  d
────────────────────────────────────────────────────────────
  d = modular inverse of e  modulo φ(n)

  This means:   (e × d) mod φ(n) = 1

  Example: e=17, φ(n)=3120 → d = 2753
  Check:   (17 × 2753) mod 3120 = 46801 mod 3120 = 1  ✓

────────────────────────────────────────────────────────────
STEP 6 — Keys
────────────────────────────────────────────────────────────
  Public Key  = (e, n)  → share freely
  Private Key = (d, n)  → keep absolutely secret

────────────────────────────────────────────────────────────
STEP 7 — Encryption
────────────────────────────────────────────────────────────
  Convert message to a number m, then:

      c = m^e  mod n       ← "m to the power e, mod n"

  In Python:   c = pow(m, e, n)

────────────────────────────────────────────────────────────
STEP 8 — Decryption
────────────────────────────────────────────────────────────
  Receiver uses the private key:

      m = c^d  mod n       ← "c to the power d, mod n"

  In Python:   m = pow(c, d, n)

  Euler's theorem guarantees this recovers the original m.

────────────────────────────────────────────────────────────
WHY IS IT SECURE?
────────────────────────────────────────────────────────────
  Breaking RSA requires factoring n back into p and q.
  For a 2048-bit n, this would take longer than the age
  of the universe with current computers.

⚠  This application uses small keys for EDUCATIONAL speed.
   Real-world RSA uses 2048 or 4096-bit keys.
"""

    def __init__(self, parent):
        super().__init__(parent)
        self.title("How RSA Works")
        self.geometry("640x700")
        self.resizable(True, True)
        self.configure(fg_color=CLR_BG)
        self.grab_set()

        make_label(self, "How RSA Encryption Works",
                   font_size=16, bold=True, color=CLR_ACCENT).pack(padx=20, pady=(20, 4))
        make_label(self, "Educational Guide — Student Friendly",
                   font_size=12, color=CLR_SUBTEXT).pack(padx=20, pady=(0, 12))

        box = ctk.CTkTextbox(
            self,
            fg_color=CLR_INPUT_BG,
            border_color=CLR_BORDER,
            border_width=1,
            corner_radius=8,
            font=ctk.CTkFont(family="Consolas", size=12),
            text_color=CLR_TEXT,
            wrap="none",
        )
        box.pack(padx=20, pady=(0, 12), fill="both", expand=True)
        box.insert("1.0", self.CONTENT)
        box.configure(state="disabled")

        make_button(self, "Close", command=self.destroy, primary=False, width=120).pack(
            pady=(0, 16))


# ─────────────────────────────────────────────────────────────────
# Main Application Window
# ─────────────────────────────────────────────────────────────────

class CryptoApp(ctk.CTk):
    """
    Main application window.

    Layout (two-column grid inside a scrollable outer frame):
      Left  column → Message input, Key Information card
      Right column → Encryption card, Decryption card
      Bottom       → Status bar, footer
    """

    VERSION = "1.0  |  Phase 1 Prototype"

    def __init__(self):
        super().__init__()

        # ── Window setup ──────────────────────────────────────────
        self.title("Cryptography Using Modular Arithmetic")
        self.geometry("1100x820")
        self.minsize(900, 700)
        self.configure(fg_color=CLR_BG)

        # Application state.
        self._key: RSAKeyPair | None = None        # Current RSA key pair.
        self._cipher_blocks: list[int] | None = None  # Current ciphertext blocks.
        self._keys_visible: bool = True            # Whether sensitive key fields show.

        # Build the interface.
        self._build_header()
        self._build_body()
        self._build_status_bar()
        self._build_footer()

    # ── Header ───────────────────────────────────────────────────

    def _build_header(self):
        """Top banner with title, subtitle, and phase label."""
        header = ctk.CTkFrame(self, fg_color=CLR_CARD2, corner_radius=0, height=90)
        header.pack(fill="x", padx=0, pady=0)
        header.pack_propagate(False)

        inner = ctk.CTkFrame(header, fg_color="transparent")
        inner.pack(expand=True)

        make_label(inner,
                   "🔐  Cryptography Using Modular Arithmetic",
                   font_size=22, bold=True, color=CLR_TEXT).pack(pady=(14, 2))
        make_label(inner,
                   "RSA Encryption & Decryption  —  Educational Desktop Application",
                   font_size=13, color=CLR_SUBTEXT).pack()

        # Phase badge.
        phase_frame = ctk.CTkFrame(header, fg_color=CLR_ACCENT, corner_radius=6)
        phase_frame.place(relx=1.0, rely=0.0, anchor="ne", x=-12, y=10)
        make_label(phase_frame, f"  Phase 1 — Core RSA Prototype  v{self.VERSION}  ",
                   font_size=10, color="#ffffff").pack(padx=4, pady=3)

    # ── Body ─────────────────────────────────────────────────────

    def _build_body(self):
        """Two-column scrollable main body."""
        # Outer frame holds two columns side by side.
        body = ctk.CTkFrame(self, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=12, pady=8)
        body.columnconfigure(0, weight=1)
        body.columnconfigure(1, weight=1)
        body.rowconfigure(0, weight=1)

        # ── Left column ──────────────────────────────────────────
        left_scroll = ctk.CTkScrollableFrame(
            body, fg_color="transparent", scrollbar_button_color=CLR_BORDER)
        left_scroll.grid(row=0, column=0, sticky="nsew", padx=(0, 6))

        self._build_message_card(left_scroll)
        self._build_key_info_card(left_scroll)
        self._build_implemented_card(left_scroll)

        # ── Right column ─────────────────────────────────────────
        right_scroll = ctk.CTkScrollableFrame(
            body, fg_color="transparent", scrollbar_button_color=CLR_BORDER)
        right_scroll.grid(row=0, column=1, sticky="nsew", padx=(6, 0))

        self._build_encryption_card(right_scroll)
        self._build_decryption_card(right_scroll)
        self._build_action_buttons_card(right_scroll)

    # ── Message Card ─────────────────────────────────────────────

    def _build_message_card(self, parent):
        """Card containing the plaintext message input and key-size selector."""
        card = make_card(parent)
        card.pack(fill="x", pady=(0, 10))

        # Card title.
        title_row = ctk.CTkFrame(card, fg_color="transparent")
        title_row.pack(fill="x", padx=14, pady=(12, 6))
        make_label(title_row, "✉  Message", font_size=15, bold=True,
                   color=CLR_ACCENT).pack(side="left")

        # Key size selector — educational option to pick prime bit-length.
        make_label(title_row, "Key Bits:", font_size=11,
                   color=CLR_SUBTEXT).pack(side="right", padx=(0, 4))
        self._key_size_var = ctk.StringVar(value="128")
        seg = ctk.CTkSegmentedButton(
            title_row,
            values=["64", "128", "256"],
            variable=self._key_size_var,
            font=ctk.CTkFont(size=11),
            fg_color=CLR_CARD,
            selected_color=CLR_ACCENT,
            unselected_color=CLR_CARD,
        )
        seg.pack(side="right", padx=(0, 8))

        # Message input text box.
        make_label(card, "Enter your plaintext message below:",
                   font_size=11, color=CLR_SUBTEXT).pack(
            anchor="w", padx=14, pady=(0, 4))
        self._msg_box = make_textbox(card, height=100)
        self._msg_box.pack(fill="x", padx=14, pady=(0, 10))
        self._msg_box.insert("1.0", "Hello World")   # Handy default for demos.

        # Generate Keys button.
        btn_row = ctk.CTkFrame(card, fg_color="transparent")
        btn_row.pack(fill="x", padx=14, pady=(0, 14))
        make_button(btn_row, "⚙  Generate RSA Keys",
                    command=self._on_generate_keys, primary=True, width=200).pack(
            side="left")
        make_label(btn_row,
                   "Generates fresh p, q, n, φ(n), e, d",
                   font_size=10, color=CLR_SUBTEXT).pack(side="left", padx=10)

    # ── Key Information Card ──────────────────────────────────────

    def _build_key_info_card(self, parent):
        """Card that shows RSA parameters after key generation."""
        card = make_card(parent)
        card.pack(fill="x", pady=(0, 10))

        # Title row with Show/Hide toggle.
        title_row = ctk.CTkFrame(card, fg_color="transparent")
        title_row.pack(fill="x", padx=14, pady=(12, 8))
        make_label(title_row, "🔑  RSA Key Information",
                   font_size=15, bold=True, color=CLR_ACCENT).pack(side="left")
        make_button(title_row, "Hide Keys", command=self._toggle_key_visibility,
                    primary=False, width=100).pack(side="right")
        self._toggle_btn_ref = title_row.winfo_children()[-1]  # Reference for text update.

        # Define which fields to display and in what order.
        # Each tuple: (label text, attribute name on self, sensitive?)
        self._key_fields = [
            ("Prime  p",         "_lbl_p",   True),
            ("Prime  q",         "_lbl_q",   True),
            ("n  =  p × q",      "_lbl_n",   False),
            ("φ(n)  =  (p-1)(q-1)", "_lbl_phi", True),
            ("Public Exponent  e",  "_lbl_e",   False),
            ("Private Exponent  d", "_lbl_d",   True),
            ("Public Key  (e, n)",  "_lbl_pub",  False),
            ("Private Key  (d, n)", "_lbl_priv", True),
        ]

        grid = ctk.CTkFrame(card, fg_color="transparent")
        grid.pack(fill="x", padx=14, pady=(0, 14))
        grid.columnconfigure(0, weight=0, minsize=180)
        grid.columnconfigure(1, weight=1)

        for row_idx, (label_text, attr, _sensitive) in enumerate(self._key_fields):
            # Row separator line.
            sep = ctk.CTkFrame(grid, fg_color=CLR_BORDER, height=1)
            sep.grid(row=row_idx * 2, column=0, columnspan=2,
                     sticky="ew", pady=(3, 0))

            # Label.
            make_label(grid, label_text, font_size=11,
                       color=CLR_SUBTEXT).grid(
                row=row_idx * 2 + 1, column=0, sticky="w", pady=4)

            # Value label — starts with placeholder.
            val_lbl = make_label(grid, "—", font_size=11,
                                 color=CLR_TEXT)
            val_lbl.grid(row=row_idx * 2 + 1, column=1, sticky="w", padx=(8, 0))

            # Store reference so we can update the value later.
            setattr(self, attr, val_lbl)

    # ── "Currently Implemented" status card ──────────────────────

    def _build_implemented_card(self, parent):
        """Shows implemented and future features — useful for teacher review."""
        card = make_card(parent, fg_color="#0d1117")
        card.pack(fill="x", pady=(0, 10))

        make_label(card, "Project Status",
                   font_size=13, bold=True, color=CLR_ACCENT).pack(
            anchor="w", padx=14, pady=(12, 6))

        items_done = [
            "CustomTkinter GUI",
            "RSA key generation",
            "Modular arithmetic (GCD, Extended GCD, Mod Inverse)",
            "Miller-Rabin primality test",
            "Block-based encryption",
            "Block-based decryption",
            "Mathematical explanation popup",
        ]
        items_next = [
            "Improved Unicode / large-block handling",
            "Visual RSA process diagram",
            "Digital signatures demonstration",
            "Export keys to file",
        ]

        done_f = ctk.CTkFrame(card, fg_color="transparent")
        done_f.pack(fill="x", padx=14, pady=(0, 4))
        make_label(done_f, "✅  Currently Implemented",
                   font_size=11, bold=True, color=CLR_SUCCESS).pack(anchor="w")
        for item in items_done:
            make_label(done_f, f"  ✓  {item}",
                       font_size=10, color=CLR_SUCCESS).pack(anchor="w")

        next_f = ctk.CTkFrame(card, fg_color="transparent")
        next_f.pack(fill="x", padx=14, pady=(6, 14))
        make_label(next_f, "🔲  Next Phase",
                   font_size=11, bold=True, color=CLR_WARNING).pack(anchor="w")
        for item in items_next:
            make_label(next_f, f"  ○  {item}",
                       font_size=10, color=CLR_WARNING).pack(anchor="w")

    # ── Encryption Card ───────────────────────────────────────────

    def _build_encryption_card(self, parent):
        """Card with Encrypt button and ciphertext display."""
        card = make_card(parent)
        card.pack(fill="x", pady=(0, 10))

        make_label(card, "🔒  Encryption",
                   font_size=15, bold=True, color=CLR_ACCENT).pack(
            anchor="w", padx=14, pady=(12, 8))

        make_label(card, "Formula:  c = m^e mod n",
                   font_size=11, color=CLR_SUBTEXT).pack(anchor="w", padx=14, pady=(0, 6))

        btn_row = ctk.CTkFrame(card, fg_color="transparent")
        btn_row.pack(fill="x", padx=14, pady=(0, 8))
        make_button(btn_row, "🔒  Encrypt Message",
                    command=self._on_encrypt, primary=True, width=180).pack(side="left")
        make_button(btn_row, "📋  Copy Ciphertext",
                    command=self._copy_ciphertext, primary=False, width=160).pack(
            side="left", padx=8)

        make_label(card, "Ciphertext  (integer blocks separated by  |  ):",
                   font_size=11, color=CLR_SUBTEXT).pack(
            anchor="w", padx=14, pady=(0, 4))
        self._cipher_box = make_textbox(card, height=120)
        self._cipher_box.pack(fill="x", padx=14, pady=(0, 14))
        self._cipher_box.configure(state="disabled")

    # ── Decryption Card ───────────────────────────────────────────

    def _build_decryption_card(self, parent):
        """Card with Decrypt button and recovered plaintext display."""
        card = make_card(parent)
        card.pack(fill="x", pady=(0, 10))

        make_label(card, "🔓  Decryption",
                   font_size=15, bold=True, color=CLR_ACCENT).pack(
            anchor="w", padx=14, pady=(12, 8))

        make_label(card, "Formula:  m = c^d mod n",
                   font_size=11, color=CLR_SUBTEXT).pack(anchor="w", padx=14, pady=(0, 6))

        make_button(card, "🔓  Decrypt Ciphertext",
                    command=self._on_decrypt, primary=True, width=180).pack(
            anchor="w", padx=14, pady=(0, 8))

        make_label(card, "Decrypted Message:",
                   font_size=11, color=CLR_SUBTEXT).pack(
            anchor="w", padx=14, pady=(0, 4))
        self._decrypted_box = make_textbox(card, height=80)
        self._decrypted_box.pack(fill="x", padx=14, pady=(0, 14))
        self._decrypted_box.configure(state="disabled")

    # ── Extra Action Buttons Card ─────────────────────────────────

    def _build_action_buttons_card(self, parent):
        """Card with auxiliary action buttons."""
        card = make_card(parent, fg_color="#0d1117")
        card.pack(fill="x", pady=(0, 10))

        make_label(card, "🛠  Tools & Actions",
                   font_size=13, bold=True, color=CLR_ACCENT).pack(
            anchor="w", padx=14, pady=(12, 8))

        row1 = ctk.CTkFrame(card, fg_color="transparent")
        row1.pack(fill="x", padx=14, pady=(0, 6))

        make_button(row1, "📐  Show Mathematics",
                    command=self._on_show_math, primary=False, width=180).pack(
            side="left", padx=(0, 8))
        make_button(row1, "📘  How It Works",
                    command=self._on_how_it_works, primary=False, width=160).pack(
            side="left")

        row2 = ctk.CTkFrame(card, fg_color="transparent")
        row2.pack(fill="x", padx=14, pady=(0, 14))

        make_button(row2, "🗑  Clear All",
                    command=self._on_clear, primary=False, width=140).pack(
            side="left", padx=(0, 8))

        # Security disclaimer label.
        make_label(card,
                   "⚠  Educational implementation — NOT for real-world secure communication.",
                   font_size=10, color=CLR_WARNING).pack(
            anchor="w", padx=14, pady=(0, 14))

    # ── Status Bar ────────────────────────────────────────────────

    def _build_status_bar(self):
        """Bottom status bar that shows the latest operation result."""
        bar = ctk.CTkFrame(self, fg_color=CLR_CARD2, corner_radius=0, height=36)
        bar.pack(fill="x", side="bottom")
        bar.pack_propagate(False)

        self._status_var = ctk.StringVar(value="Ready — Generate keys to begin.")
        self._status_lbl = ctk.CTkLabel(
            bar,
            textvariable=self._status_var,
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color=CLR_SUBTEXT,
            anchor="w",
        )
        self._status_lbl.pack(side="left", padx=16, fill="y")

    # ── Footer ────────────────────────────────────────────────────

    def _build_footer(self):
        """Thin branding footer."""
        footer = ctk.CTkFrame(self, fg_color="#0a0a1a", corner_radius=0, height=24)
        footer.pack(fill="x", side="bottom")
        footer.pack_propagate(False)
        make_label(
            footer,
            "Cryptography Using Modular Arithmetic  |  RSA Educational Project  |  "
            "Phase 1 Prototype",
            font_size=9, color="#475569",
        ).pack(expand=True)

    # ─────────────────────────────────────────────────────────────
    # Status helpers
    # ─────────────────────────────────────────────────────────────

    def _set_status(self, text: str, kind: str = "info"):
        """Update the status bar.  kind = 'info' | 'success' | 'warning' | 'error'"""
        colour_map = {
            "info":    CLR_SUBTEXT,
            "success": CLR_SUCCESS,
            "warning": CLR_WARNING,
            "error":   CLR_ERROR,
        }
        self._status_lbl.configure(text_color=colour_map.get(kind, CLR_SUBTEXT))
        self._status_var.set(text)

    # ─────────────────────────────────────────────────────────────
    # Button Handlers
    # ─────────────────────────────────────────────────────────────

    def _on_generate_keys(self):
        """
        Handler for the 'Generate RSA Keys' button.

        Runs key generation in a background thread so the GUI does not freeze.
        Miller-Rabin primality testing on large primes can take a second or two.
        """
        bits = int(self._key_size_var.get())
        self._set_status(f"⏳  Generating {bits}-bit RSA key pair …", "info")
        self.update_idletasks()

        def _worker():
            try:
                key = generate_keys(bits=bits)
                # Schedule the UI update on the main thread.
                self.after(0, lambda: self._display_keys(key))
            except Exception as exc:
                self.after(0, lambda: self._show_error("Key generation failed", str(exc)))

        threading.Thread(target=_worker, daemon=True).start()

    def _display_keys(self, key: RSAKeyPair):
        """Update the Key Information card with freshly generated values."""
        self._key = key
        self._cipher_blocks = None   # Invalidate old ciphertext.
        self._keys_visible = True

        def fmt(v: int) -> str:
            """Format a large integer: show up to 60 chars then '…'."""
            s = str(v)
            return s if len(s) <= 60 else s[:60] + "…"

        self._lbl_p.configure(text=fmt(key.p))
        self._lbl_q.configure(text=fmt(key.q))
        self._lbl_n.configure(text=fmt(key.n))
        self._lbl_phi.configure(text=fmt(key.phi))
        self._lbl_e.configure(text=str(key.e))
        self._lbl_d.configure(text=fmt(key.d))
        self._lbl_pub.configure(text=f"(e={key.e},  n={fmt(key.n)})")
        self._lbl_priv.configure(text=f"(d={fmt(key.d)},  n={fmt(key.n)})")

        # Clear stale outputs from a previous run.
        self._set_textbox(self._cipher_box, "")
        self._set_textbox(self._decrypted_box, "")

        n_bits = key.n.bit_length()
        self._set_status(
            f"✓  Keys generated  |  n = {n_bits} bits  |  "
            f"Block size = {key.block_size} bytes  |  e = {key.e}",
            "success"
        )

    def _on_encrypt(self):
        """
        Handler for the 'Encrypt' button.

        Validates state, reads the message, calls encrypt_message(), displays result.
        """
        # Validation: keys must exist before encryption.
        if self._key is None:
            self._show_warning("Please generate RSA keys before encrypting.")
            return

        # Validation: message must not be empty.
        message = self._msg_box.get("1.0", "end").strip()
        if not message:
            self._show_warning("Please enter a message to encrypt.")
            return

        self._set_status("⏳  Encrypting …", "info")
        self.update_idletasks()

        try:
            # Encrypt the message using the current key pair.
            cipher_blocks = encrypt_message(message, self._key)
            self._cipher_blocks = cipher_blocks

            # Convert ciphertext blocks to a display string.
            cipher_str = ciphertext_to_str(cipher_blocks)
            self._set_textbox(self._cipher_box, cipher_str)
            self._set_textbox(self._decrypted_box, "")   # Clear old decryption.

            n_blocks = len(cipher_blocks)
            self._set_status(
                f"✓  Encryption successful  |  {n_blocks} block(s)  |  "
                "Use 'Decrypt' to verify.",
                "success"
            )
        except Exception as exc:
            self._show_error("Encryption failed", str(exc))

    def _on_decrypt(self):
        """
        Handler for the 'Decrypt' button.

        Validates state, reads ciphertext, calls decrypt_message(), displays result.
        """
        # Validation: keys must exist.
        if self._key is None:
            self._show_warning("Please generate RSA keys before decrypting.")
            return

        # Validation: ciphertext must be present.
        cipher_str = self._cipher_box.get("1.0", "end").strip()
        if not cipher_str:
            self._show_warning("No ciphertext to decrypt. Please encrypt a message first.")
            return

        self._set_status("⏳  Decrypting …", "info")
        self.update_idletasks()

        try:
            # Parse the displayed ciphertext string back into integer blocks.
            cipher_blocks = str_to_ciphertext(cipher_str)

            # Decrypt using the private key (d, n).
            plaintext = decrypt_message(cipher_blocks, self._key)
            self._set_textbox(self._decrypted_box, plaintext)

            # Verify against the original message for extra confidence.
            original = self._msg_box.get("1.0", "end").strip()
            if plaintext == original:
                self._set_status(
                    "✓  Decryption successful  |  Decrypted text matches original ✓",
                    "success"
                )
            else:
                self._set_status(
                    "⚠  Decryption done but result differs from current message box.",
                    "warning"
                )

        except ValueError as exc:
            self._show_error("Decryption failed", str(exc))
        except Exception as exc:
            self._show_error("Unexpected error during decryption", str(exc))

    def _toggle_key_visibility(self):
        """Show or hide sensitive key values (p, q, φ(n), d, private key)."""
        if self._key is None:
            self._show_warning("Generate keys first.")
            return

        self._keys_visible = not self._keys_visible

        def fmt(v: int) -> str:
            s = str(v)
            return s if len(s) <= 60 else s[:60] + "…"

        # Sensitive fields.
        sensitive_attrs = ["_lbl_p", "_lbl_q", "_lbl_phi", "_lbl_d", "_lbl_priv"]
        sensitive_values = [
            fmt(self._key.p),
            fmt(self._key.q),
            fmt(self._key.phi),
            fmt(self._key.d),
            f"(d={fmt(self._key.d)},  n={fmt(self._key.n)})",
        ]

        for attr, val in zip(sensitive_attrs, sensitive_values):
            lbl = getattr(self, attr)
            if self._keys_visible:
                lbl.configure(text=val)
            else:
                lbl.configure(text="●●●●●●●●  (hidden)")

        # Update button label.
        btn_text = "Show Keys" if not self._keys_visible else "Hide Keys"
        self._toggle_btn_ref.configure(text=btn_text)
        self._set_status(
            "Keys shown." if self._keys_visible else "Sensitive key values hidden.",
            "info"
        )

    def _on_show_math(self):
        """Open the 'Show Mathematics' popup with the current key pair values."""
        if self._key is None:
            self._show_warning("Please generate RSA keys first.")
            return
        MathWindow(self, self._key)

    def _on_how_it_works(self):
        """Open the educational 'How RSA Works' popup."""
        HowItWorksWindow(self)

    def _copy_ciphertext(self):
        """Copy the ciphertext textbox content to the system clipboard."""
        text = self._cipher_box.get("1.0", "end").strip()
        if not text:
            self._show_warning("No ciphertext to copy.")
            return
        self.clipboard_clear()
        self.clipboard_append(text)
        self._set_status("📋  Ciphertext copied to clipboard.", "info")

    def _on_clear(self):
        """Clear all input/output fields and reset application state."""
        self._key = None
        self._cipher_blocks = None

        # Clear message box.
        self._msg_box.delete("1.0", "end")

        # Clear output boxes.
        self._set_textbox(self._cipher_box, "")
        self._set_textbox(self._decrypted_box, "")

        # Reset key info labels.
        for _, attr, _ in self._key_fields:
            getattr(self, attr).configure(text="—")

        self._set_status("Cleared. Ready to start a new session.", "info")

    # ─────────────────────────────────────────────────────────────
    # Utility helpers
    # ─────────────────────────────────────────────────────────────

    @staticmethod
    def _set_textbox(box: ctk.CTkTextbox, text: str):
        """Helper to safely set the content of a read-only CTkTextbox."""
        box.configure(state="normal")
        box.delete("1.0", "end")
        box.insert("1.0", text)
        box.configure(state="disabled")

    def _show_warning(self, message: str):
        """Show a friendly warning in both the status bar and a popup."""
        self._set_status(f"⚠  {message}", "warning")
        messagebox.showwarning("Warning", message, parent=self)

    def _show_error(self, title: str, detail: str):
        """Show an error without exposing a raw Python traceback."""
        self._set_status(f"✗  {title}: {detail}", "error")
        messagebox.showerror(title, detail, parent=self)
