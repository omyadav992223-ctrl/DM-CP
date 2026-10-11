"""
crypto_utils.py
================
Low-level mathematical helpers for RSA.

This module contains pure number-theory functions that are imported by rsa.py.
Keeping them here makes each function easy to find and explain during a viva.

Concepts covered:
  - Greatest Common Divisor (GCD)
  - Extended Euclidean Algorithm
  - Modular Multiplicative Inverse
  - Primality Testing (trial division + Miller-Rabin)
  - Prime Generation
  - Text ↔ Block conversion for RSA
"""

import math
import random
import secrets


# ─────────────────────────────────────────────────────────────────
# GCD  (Greatest Common Divisor)
# ─────────────────────────────────────────────────────────────────

def gcd(a: int, b: int) -> int:
    """
    Return the Greatest Common Divisor of a and b using the Euclidean algorithm.

    The GCD is the largest integer that divides both a and b without remainder.

    Example:
        gcd(12, 8) → 4

    In RSA, gcd(e, φ(n)) must equal 1, meaning e and φ(n) share no common factor.
    This ensures that e has a modular inverse modulo φ(n).
    """
    # Keep replacing (a, b) with (b, a mod b) until b reaches zero.
    # At that point, a holds the GCD — this is the Euclidean algorithm.
    while b != 0:
        a, b = b, a % b
    return a


# ─────────────────────────────────────────────────────────────────
# Extended Euclidean Algorithm
# ─────────────────────────────────────────────────────────────────

def extended_gcd(a: int, b: int) -> tuple[int, int, int]:
    """
    Extended Euclidean Algorithm.

    Returns (gcd, x, y) such that:
        a*x + b*y = gcd(a, b)

    This is used to compute the modular inverse.
    If gcd(a, b) == 1 then x is the modular inverse of a mod b.

    Viva explanation:
        The standard Euclidean algorithm only finds the GCD.
        The *extended* version also finds integers x and y (Bézout coefficients)
        that satisfy the equation above.  When gcd == 1, x % b is the answer we
        want for the modular inverse.
    """
    # Base case: when b reaches 0, gcd = a, and the coefficients are trivially (1, 0).
    if b == 0:
        return a, 1, 0

    # Recursive call — solve the smaller sub-problem first.
    gcd_val, x1, y1 = extended_gcd(b, a % b)

    # Back-substitute to find the coefficients for the current (a, b).
    x = y1
    y = x1 - (a // b) * y1
    return gcd_val, x, y


# ─────────────────────────────────────────────────────────────────
# Modular Multiplicative Inverse
# ─────────────────────────────────────────────────────────────────

def modular_inverse(a: int, m: int) -> int:
    """
    Return the modular multiplicative inverse of a modulo m.

    By definition:
        (a * inverse) % m == 1

    In RSA this is used to find the private exponent d:
        d = modular_inverse(e, φ(n))
        so that (e * d) % φ(n) == 1

    Raises ValueError if the inverse does not exist
    (i.e., gcd(a, m) ≠ 1).
    """
    gcd_val, x, _ = extended_gcd(a % m, m)

    # The inverse only exists when a and m are coprime (share no factor > 1).
    if gcd_val != 1:
        raise ValueError(f"Modular inverse does not exist: gcd({a}, {m}) = {gcd_val}")

    # x may be negative, so we reduce it into the range [0, m-1].
    return x % m


# ─────────────────────────────────────────────────────────────────
# Primality Testing — Miller-Rabin
# ─────────────────────────────────────────────────────────────────

def _miller_rabin_round(n: int, d: int, r: int, a: int) -> bool:
    """
    Single round of the Miller-Rabin probabilistic primality test.

    Returns True if n is *probably* prime for the given witness a.
    Returns False if n is definitely composite.

    The algorithm checks whether a^d ≡ 1 (mod n) or
    a^(d * 2^j) ≡ -1 (mod n) for some j in [0, r-1].
    """
    # Compute a^d mod n using Python's built-in modular exponentiation.
    x = pow(a, d, n)

    # If x == 1 or x == n-1, n passes this round.
    if x == 1 or x == n - 1:
        return True

    # Square x repeatedly up to r-1 times.
    for _ in range(r - 1):
        x = pow(x, 2, n)
        if x == n - 1:
            return True

    # None of the conditions were met — n is composite.
    return False


def is_prime(n: int, rounds: int = 10) -> bool:
    """
    Test whether n is prime using trial division + Miller-Rabin.

    Miller-Rabin is a *probabilistic* test: it can confirm "definitely composite"
    or "probably prime".  With 10 rounds the probability of a false positive
    (composite reported as prime) is less than 4^-10 ≈ 1 in a million.

    For educational key sizes (128-bit to 512-bit), this is more than sufficient.

    Args:
        n      – the number to test
        rounds – number of Miller-Rabin witness checks (more → more accurate)
    """
    # Handle small and trivial cases first.
    if n < 2:
        return False
    if n == 2 or n == 3:
        return True
    if n % 2 == 0:
        return False

    # Quick trial division against small primes to eliminate obvious composites fast.
    small_primes = [3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37]
    for sp in small_primes:
        if n == sp:
            return True
        if n % sp == 0:
            return False

    # Write n-1 as 2^r * d where d is odd.
    # This factorisation is required by the Miller-Rabin algorithm.
    r, d = 0, n - 1
    while d % 2 == 0:
        r += 1
        d //= 2

    # Run the specified number of witness rounds.
    # Using random witnesses rather than fixed ones gives better coverage.
    for _ in range(rounds):
        a = random.randrange(2, n - 1)
        if not _miller_rabin_round(n, d, r, a):
            return False  # Definitely composite.

    return True  # Probably prime with high confidence.


# ─────────────────────────────────────────────────────────────────
# Prime Generation
# ─────────────────────────────────────────────────────────────────

def generate_prime(bits: int = 128) -> int:
    """
    Generate a random prime number of approximately `bits` bits.

    Strategy:
        1. Generate a random odd integer in the correct bit range.
        2. Test it with is_prime().
        3. Repeat until a prime is found.

    For educational purposes 128-bit primes are the default — fast to generate
    and large enough that the RSA maths is real.  Production RSA uses 1024+ bits
    per prime, but that is slower and unnecessary for classroom demonstration.

    Args:
        bits – approximate bit-length of the prime to generate
    """
    while True:
        # secrets.randbits is cryptographically random — better than random.randint.
        candidate = secrets.randbits(bits)

        # Force the candidate to be odd (LSB = 1) and to have the correct bit length
        # by setting the two most-significant bits.
        candidate |= (1 << (bits - 1))  # Ensure it has exactly `bits` bits.
        candidate |= 1                  # Ensure it is odd (even numbers are never prime > 2).

        if is_prime(candidate):
            return candidate


# ─────────────────────────────────────────────────────────────────
# Text ↔ Integer Block Conversion
# ─────────────────────────────────────────────────────────────────

def _compute_block_size(n: int) -> int:
    """
    Compute the safe byte-length for each RSA plaintext block.

    The block integer must be strictly less than n.  Using
    (byte-length of n  −  1) bytes per block guarantees this,
    because the maximum value of a (k-1)-byte number is 2^(8(k-1))-1,
    which is always less than a k-byte number like n.

    We further reserve 2 bytes for a length prefix (see text_to_blocks),
    so the usable payload per block = block_size - 2.
    """
    n_byte_length = (n.bit_length() + 7) // 8
    # One byte less than n's byte length to keep block integer < n.
    # Must be at least 3 so we have room for the 2-byte prefix + 1 byte payload.
    return max(3, n_byte_length - 1)


def text_to_blocks(text: str, n: int) -> list[int]:
    """
    Convert a text string into a list of integer blocks suitable for RSA encryption.

    Why blocks?
        RSA can only encrypt an integer m where 0 <= m < n.
        If the message is long, its integer representation may exceed n,
        so we split it into smaller chunks that each fit below n.

    Encoding scheme (length-prefixed):
        Each block is encoded as:
            [ 2 bytes: chunk length  |  up to (block_size - 2) bytes: payload ]
        The 2-byte length prefix allows exact recovery without null-stripping hacks.

    Returns a list of integers, each representing one block.
    """
    # Encode text to bytes so we can handle any Unicode character.
    raw_bytes = text.encode("utf-8")

    # Determine how many payload bytes fit per block.
    # block_size = total bytes per block integer.
    # payload_size = block_size - 2  (2 bytes reserved for the length prefix).
    block_size = _compute_block_size(n)
    payload_size = block_size - 2

    blocks = []
    for i in range(0, len(raw_bytes), payload_size):
        chunk = raw_bytes[i : i + payload_size]
        chunk_len = len(chunk)

        # Build the block bytes: 2-byte big-endian length + payload.
        # Using a length prefix means we always know the exact payload length
        # during decryption, with no ambiguity about trailing zeros.
        block_bytes = chunk_len.to_bytes(2, byteorder="big") + chunk

        # Pad to exactly block_size bytes so the integer is the right size.
        block_bytes = block_bytes.ljust(block_size, b"\x00")

        # Convert the byte sequence to a big-endian integer.
        block_int = int.from_bytes(block_bytes, byteorder="big")
        blocks.append(block_int)

    return blocks


def blocks_to_text(blocks: list[int], block_size: int) -> str:
    """
    Reconstruct the original text string from a list of integer blocks.

    This is the inverse of text_to_blocks().
    Each block integer is converted back to block_size bytes, then the
    2-byte length prefix tells us how many payload bytes to extract.

    Args:
        blocks     - list of integer blocks (output of RSA decryption)
        block_size - the total byte-length used during text_to_blocks()
    """
    raw_bytes = b""
    for block in blocks:
        # Convert the integer back to exactly block_size bytes.
        block_bytes = block.to_bytes(block_size, byteorder="big")

        # Read the 2-byte length prefix to know how many payload bytes follow.
        chunk_len = int.from_bytes(block_bytes[:2], byteorder="big")

        # Extract exactly chunk_len bytes of payload (no trailing null confusion).
        payload = block_bytes[2 : 2 + chunk_len]
        raw_bytes += payload

    # Decode the reassembled UTF-8 byte string to recover the original text.
    return raw_bytes.decode("utf-8")

