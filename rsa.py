"""
rsa.py
=======
RSA Key Generation, Encryption, and Decryption.

This module implements RSA from first mathematical principles using only
the helper functions from crypto_utils.py.  No external cryptography
libraries are used — the goal is educational clarity.

RSA Algorithm Overview
──────────────────────
1.  Choose two distinct prime numbers  p  and  q.
2.  Compute the modulus:               n = p × q
3.  Compute Euler's totient:           φ(n) = (p-1)(q-1)
4.  Choose public exponent e such that: 1 < e < φ(n)  and  gcd(e, φ(n)) = 1
5.  Compute private exponent:          d ≡ e⁻¹  (mod φ(n))
6.  Public key  = (e, n)
7.  Private key = (d, n)
8.  Encryption: c = m^e mod n
9.  Decryption: m = c^d mod n

Why does decryption recover the original message?
    By Euler's theorem, m^(φ(n)) ≡ 1 (mod n) for m coprime to n.
    Since d*e ≡ 1 (mod φ(n)), we have:
        (m^e)^d = m^(ed) = m^(1 + k·φ(n)) = m · (m^φ(n))^k ≡ m (mod n)
    Therefore decrypting the ciphertext returns the original message.
"""

from dataclasses import dataclass
from crypto_utils import (
    gcd,
    modular_inverse,
    generate_prime,
    text_to_blocks,
    blocks_to_text,
    _compute_block_size,
)


# ─────────────────────────────────────────────────────────────────
# Data Structures
# ─────────────────────────────────────────────────────────────────

@dataclass
class RSAKeyPair:
    """
    Holds all RSA parameters for display and use.

    Fields
    ------
    p, q   – the two secret prime numbers
    n      – the public modulus  (p × q)
    phi    – Euler's totient     ((p-1)(q-1))
    e      – public exponent
    d      – private exponent
    block_size – byte-length of each plaintext block
    """
    p: int
    q: int
    n: int
    phi: int
    e: int
    d: int
    block_size: int


# ─────────────────────────────────────────────────────────────────
# Key Generation
# ─────────────────────────────────────────────────────────────────

def choose_public_exponent(phi: int) -> int:
    """
    Choose a valid public exponent e.

    Requirements:
        1 < e < φ(n)
        gcd(e, φ(n)) == 1   ← e must be coprime with φ(n)

    Strategy:
        - Try the widely-used value e = 65537 (a Fermat prime: 2^16 + 1) first.
          It is fast for modular exponentiation because it has very few 1-bits
          in binary.  Real-world RSA almost always uses this value.
        - If 65537 does not work (unlikely but possible with tiny φ), fall back
          to scanning small odd numbers until a valid e is found.
    """
    # 65537 is the standard choice in real RSA (e.g., used in OpenSSL, TLS).
    preferred = 65537
    if phi > preferred and gcd(preferred, phi) == 1:
        return preferred

    # Fallback: try common small odd values.
    for candidate in [3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41]:
        if candidate < phi and gcd(candidate, phi) == 1:
            return candidate

    # Last resort: scan upward from 3.
    e = 3
    while e < phi:
        if gcd(e, phi) == 1:
            return e
        e += 2  # Only test odd numbers.

    raise ValueError("Could not find a valid public exponent e.")


def generate_keys(bits: int = 128) -> RSAKeyPair:
    """
    Generate a complete RSA key pair.

    Args:
        bits – approximate bit-length of each prime p and q.
               Default 128 bits → n is roughly 256 bits.
               Small enough for fast classroom generation,
               large enough that the maths is genuine.

    Returns:
        RSAKeyPair dataclass containing all RSA parameters.

    Steps (matching the algorithm overview at the top of this file):
    """
    # ── Step 1: Choose two distinct prime numbers p and q ──────────
    # RSA security relies on the difficulty of factoring n = p × q.
    # p and q must be distinct; if p == q then n = p² and φ(n) = p(p-1),
    # which is much easier to factor.
    p = generate_prime(bits)
    q = generate_prime(bits)
    while q == p:                      # Ensure p ≠ q.
        q = generate_prime(bits)

    # ── Step 2: Compute n = p × q ──────────────────────────────────
    # n is called the RSA modulus.  It is part of both the public and private keys.
    # Its bit-length determines the key size (here ~256 bits).
    n = p * q

    # ── Step 3: Compute Euler's totient φ(n) ───────────────────────
    # For n = p × q where p and q are distinct primes:
    #     φ(n) = (p - 1)(q - 1)
    # φ(n) counts how many integers from 1 to n-1 are coprime with n.
    # It is the "order" of the multiplicative group mod n used by RSA.
    phi = (p - 1) * (q - 1)

    # ── Step 4: Choose the public exponent e ───────────────────────
    # e must satisfy: 1 < e < φ(n)  and  gcd(e, φ(n)) = 1
    # The condition gcd(e, φ(n)) = 1 guarantees that the modular inverse d exists.
    e = choose_public_exponent(phi)

    # ── Step 5: Compute the private exponent d ─────────────────────
    # d is the modular multiplicative inverse of e modulo φ(n).
    # By definition:   (e × d) mod φ(n) = 1
    # This means e and d "undo" each other in the modular sense.
    d = modular_inverse(e, phi)

    # ── Compute block size ─────────────────────────────────────────
    # Each plaintext block must be an integer strictly less than n.
    # _compute_block_size() uses the same formula as text_to_blocks()
    # so the two are always consistent.
    block_size = _compute_block_size(n)

    return RSAKeyPair(p=p, q=q, n=n, phi=phi, e=e, d=d, block_size=block_size)


# ─────────────────────────────────────────────────────────────────
# Block-level Encryption / Decryption
# ─────────────────────────────────────────────────────────────────

def encrypt_block(m: int, e: int, n: int) -> int:
    """
    Encrypt a single integer block using the RSA public key.

    Formula:
        c = m^e mod n

    Python's three-argument pow() computes (m ** e) % n efficiently using
    the fast modular exponentiation (square-and-multiply) algorithm.
    This avoids computing the astronomically large m**e before taking mod.

    Args:
        m – plaintext integer (must satisfy 0 ≤ m < n)
        e – public exponent
        n – RSA modulus

    Returns:
        c – ciphertext integer
    """
    if m >= n:
        raise ValueError(f"Plaintext block ({m}) must be less than modulus n ({n}).")
    # pow(base, exponent, modulus) — built-in Python fast modular exponentiation.
    return pow(m, e, n)


def decrypt_block(c: int, d: int, n: int) -> int:
    """
    Decrypt a single integer block using the RSA private key.

    Formula:
        m = c^d mod n

    By RSA mathematics, applying the private exponent d to a ciphertext c
    (which was encrypted with public exponent e) recovers the original m.
    This works because e × d ≡ 1 (mod φ(n)), which — via Euler's theorem —
    means m^(e×d) ≡ m (mod n).

    Args:
        c – ciphertext integer
        d – private exponent
        n – RSA modulus

    Returns:
        m – recovered plaintext integer
    """
    # pow(base, exponent, modulus) — same efficient modular exponentiation.
    return pow(c, d, n)


# ─────────────────────────────────────────────────────────────────
# Full Message Encryption / Decryption
# ─────────────────────────────────────────────────────────────────

def encrypt_message(message: str, key: RSAKeyPair) -> list[int]:
    """
    Encrypt a full text message using an RSA public key.

    Steps:
        1. Convert the message text into integer blocks via text_to_blocks().
        2. Encrypt each block with encrypt_block(m, e, n).
        3. Return the list of ciphertext integers.

    Why blocks?
        RSA requires the plaintext integer to be smaller than n.
        A long message encoded as one big integer would exceed n,
        so we split it into chunks that each fit within the modulus.

    Args:
        message – plaintext string (any UTF-8 text)
        key     – RSAKeyPair containing the public key (e, n) and block_size

    Returns:
        List of ciphertext integer blocks.
    """
    # Convert text → list of integers, each < n.
    plaintext_blocks = text_to_blocks(message, key.n)

    # Encrypt every block individually using the public key.
    ciphertext_blocks = [encrypt_block(m, key.e, key.n) for m in plaintext_blocks]

    return ciphertext_blocks


def decrypt_message(ciphertext_blocks: list[int], key: RSAKeyPair) -> str:
    """
    Decrypt a list of RSA ciphertext blocks back to the original text.

    Steps:
        1. Decrypt each block with decrypt_block(c, d, n).
        2. Reconstruct the original text via blocks_to_text().

    Args:
        ciphertext_blocks – list of ciphertext integers (from encrypt_message)
        key               – RSAKeyPair containing the private key (d, n) and block_size

    Returns:
        The original plaintext string.
    """
    # Decrypt every block individually using the private key.
    plaintext_blocks = [decrypt_block(c, key.d, key.n) for c in ciphertext_blocks]

    # Reassemble the byte chunks and decode UTF-8 to get the original string.
    return blocks_to_text(plaintext_blocks, key.block_size)


# ─────────────────────────────────────────────────────────────────
# Serialisation helpers (for display and storage of ciphertext)
# ─────────────────────────────────────────────────────────────────

def ciphertext_to_str(blocks: list[int]) -> str:
    """
    Convert a list of ciphertext integers to a human-readable string.

    Format: integers separated by ' | '
    Example: "123456789 | 987654321 | 112233445"

    This string can be parsed back with str_to_ciphertext().
    """
    return " | ".join(str(b) for b in blocks)


def str_to_ciphertext(s: str) -> list[int]:
    """
    Parse the string representation of ciphertext back to a list of integers.

    Inverse of ciphertext_to_str().

    Raises ValueError if the string is malformed.
    """
    try:
        return [int(part.strip()) for part in s.split("|") if part.strip()]
    except ValueError as exc:
        raise ValueError("Ciphertext is invalid or corrupted.") from exc
