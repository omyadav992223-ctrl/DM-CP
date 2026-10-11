"""
main.py
========
Entry point for the "Cryptography Using Modular Arithmetic" desktop application.

Run this file to start the application:
    python main.py

Project structure:
    main.py        — this file, starts the GUI
    gui.py         — CustomTkinter interface
    rsa.py         — RSA key generation, encryption, decryption
    crypto_utils.py — GCD, modular inverse, primality, prime generation
    README.md      — project documentation
    requirements.txt — Python dependencies
"""

import sys

# Ensure Python 3.10+ is available (we use newer type hints such as X | Y).
if sys.version_info < (3, 10):
    print("ERROR: This application requires Python 3.10 or later.")
    print(f"       You are running Python {sys.version}")
    sys.exit(1)

from gui import CryptoApp


def main():
    """
    Create and run the main application window.

    CryptoApp is a subclass of customtkinter.CTk (the root window).
    Calling mainloop() enters the Tk event loop and keeps the window open
    until the user closes it.
    """
    app = CryptoApp()
    app.mainloop()


if __name__ == "__main__":
    main()
