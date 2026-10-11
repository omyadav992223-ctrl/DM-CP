"""
test_logic.py
=============
Headless test script — runs WITHOUT opening a GUI window.
Tests all RSA mathematical functions and the full encrypt→decrypt flow.
"""

import sys
sys.path.insert(0, ".")

from crypto_utils import gcd, extended_gcd, modular_inverse, is_prime, generate_prime, text_to_blocks, blocks_to_text
from rsa import generate_keys, encrypt_message, decrypt_message, ciphertext_to_str, str_to_ciphertext

PASS = "[PASS]"
FAIL = "[FAIL]"

def test_gcd():
    assert gcd(12, 8) == 4
    assert gcd(17, 5) == 1
    assert gcd(100, 25) == 25
    assert gcd(0, 5) == 5
    print(f"{PASS}  gcd()")

def test_extended_gcd():
    g, x, y = extended_gcd(35, 15)
    assert g == 5
    assert 35*x + 15*y == g
    print(f"{PASS}  extended_gcd()")

def test_modular_inverse():
    # 3 * 7 = 21 ≡ 1 (mod 10) → inverse of 3 mod 10 = 7
    assert modular_inverse(3, 10) == 7
    # 17 * 2753 mod 3120 = 1  (classical RSA textbook example)
    assert modular_inverse(17, 3120) == 2753
    print(f"{PASS}  modular_inverse()")

def test_is_prime():
    primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 61, 53]
    composites = [1, 4, 6, 8, 9, 10, 15, 100, 3233]
    for p in primes:
        assert is_prime(p), f"Expected {p} to be prime"
    for c in composites:
        assert not is_prime(c), f"Expected {c} to be composite"
    print(f"{PASS}  is_prime()")

def test_generate_prime():
    p = generate_prime(bits=64)
    assert p.bit_length() >= 62   # Allow some slack.
    assert is_prime(p)
    print(f"{PASS}  generate_prime(64-bit) = {p}")

def test_text_blocks_roundtrip():
    # Use a known n large enough to hold multi-byte blocks.
    from rsa import generate_keys
    key = generate_keys(bits=64)
    texts = ["Hello", "A", "Hello World!", "RSA 123 @#$"]
    for t in texts:
        blocks = text_to_blocks(t, key.n)
        recovered = blocks_to_text(blocks, key.block_size)
        assert recovered == t, f"Roundtrip failed: '{t}' → '{recovered}'"
    print(f"{PASS}  text_to_blocks / blocks_to_text roundtrip")

def test_encrypt_decrypt(message, bits=128):
    key = generate_keys(bits=bits)
    cipher_blocks = encrypt_message(message, key)
    assert len(cipher_blocks) > 0
    cipher_str = ciphertext_to_str(cipher_blocks)
    parsed = str_to_ciphertext(cipher_str)
    assert parsed == cipher_blocks
    recovered = decrypt_message(parsed, key)
    assert recovered == message, f"FAIL: original='{message}' recovered='{recovered}'"
    print(f"{PASS}  Encrypt→Decrypt: '{message}'")

def main():
    print("=" * 60)
    print("  RSA LOGIC UNIT TESTS")
    print("=" * 60)

    test_gcd()
    test_extended_gcd()
    test_modular_inverse()
    test_is_prime()
    test_generate_prime()
    test_text_blocks_roundtrip()

    test_cases = [
        "Hello World",
        "Cryptography using Modular Arithmetic",
        "RSA 123! @#",
        "The quick brown fox jumps over the lazy dog.",
        "a",
        "12345",
        "Hello, World! This is a test message with punctuation: .,:;!?",
    ]
    for msg in test_cases:
        test_encrypt_decrypt(msg, bits=128)

    print("=" * 60)
    print("  ALL TESTS PASSED")
    print("=" * 60)

if __name__ == "__main__":
    main()
