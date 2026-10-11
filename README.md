# Cryptography Using Modular Arithmetic
### RSA Encryption & Decryption — Educational Desktop Application
**Phase 1 Prototype** | Python + CustomTkinter

---

## Project Description

This is a college-level computer science project that demonstrates the mathematics
of **RSA public-key cryptography** through an interactive Python desktop application.

The application implements RSA entirely from mathematical first principles using only
Python's built-in `math`, `random`, and `secrets` modules — no cryptographic libraries
are used. The goal is educational clarity so that every line of code can be explained
during a viva/presentation.

> ⚠ **Educational implementation — NOT intended for real-world secure communication.**

---

## Objectives

- Demonstrate modular arithmetic in a practical context
- Implement RSA key generation, encryption, and decryption from scratch
- Provide an interactive GUI for teacher/examiner demonstration
- Explain the mathematics clearly in the application itself
- Produce viva-ready, well-commented source code

---

## Features (Phase 1)

| Feature | Status |
|---|---|
| Modern CustomTkinter dark-theme GUI | ✅ Done |
| RSA key generation (64 / 128 / 256-bit primes) | ✅ Done |
| Display of all RSA parameters (p, q, n, φ(n), e, d) | ✅ Done |
| RSA encryption (block-based, UTF-8 safe) | ✅ Done |
| RSA decryption with verification | ✅ Done |
| Show Mathematics popup (step-by-step with real values) | ✅ Done |
| How It Works educational popup | ✅ Done |
| Hide/Show sensitive key values | ✅ Done |
| Copy ciphertext to clipboard | ✅ Done |
| Friendly error handling (no crashes) | ✅ Done |
| Key size selector (64 / 128 / 256 bit) | ✅ Done |

---

## Technology Stack

| Layer | Tool | Why |
|---|---|---|
| Language | Python 3.10+ | Native big integers, huge math ecosystem |
| GUI | CustomTkinter 5.2+ | Modern dark theme with almost zero effort |
| Math / Number Theory | Built-in `math`, `random`, `secrets` | GCD, mod inverse, modular exponentiation |
| No extras needed | — | NumPy / SymPy / Matplotlib NOT required |

---

## Mathematical Concepts

- **Modular Arithmetic** — arithmetic on a "clock" (numbers wrap around a modulus)
- **Prime Numbers** — integers divisible only by 1 and themselves
- **GCD** — Greatest Common Divisor (Euclidean Algorithm)
- **Extended Euclidean Algorithm** — finds Bézout coefficients
- **Euler's Totient Function φ(n)** — count of integers < n coprime with n
- **Modular Multiplicative Inverse** — the value d such that (e × d) mod φ(n) = 1
- **Modular Exponentiation** — fast computation of `base^exp mod n`
- **Miller-Rabin Primality Test** — probabilistic prime detection

---

## RSA Algorithm

```
1. Choose two distinct primes:   p, q
2. Compute modulus:              n = p × q
3. Compute Euler's totient:      φ(n) = (p-1)(q-1)
4. Choose public exponent:       e  such that  gcd(e, φ(n)) = 1
5. Compute private exponent:     d = modular_inverse(e, φ(n))
6. Public key:                   (e, n)
7. Private key:                  (d, n)
8. Encrypt:                      c = m^e mod n
9. Decrypt:                      m = c^d mod n
```

Python uses `pow(base, exponent, modulus)` for fast modular exponentiation.

---

## Project Structure

```
CryptoRSA/
│
├── main.py           — Application entry point (run this)
├── gui.py            — CustomTkinter interface
├── rsa.py            — RSA key generation, encryption, decryption
├── crypto_utils.py   — GCD, extended GCD, modular inverse, primality, primes
├── README.md         — This file
└── requirements.txt  — Python dependencies
```

---

## Installation

```bash
# 1. Make sure Python 3.10+ is installed
python --version

# 2. Install the only required package
python -m pip install customtkinter

# 3. Navigate to the project folder
cd CryptoRSA
```

---

## How to Run

```bash
python main.py
```

---

## How to Use (Demo Flow)

1. **Launch** the application with `python main.py`
2. **Enter** a message in the "Message" text box (default: "Hello World")
3. **Select** a key size (64 / 128 / 256 bit) — 128 bit is good for demos
4. **Click** `Generate RSA Keys` — watch p, q, n, φ(n), e, d appear
5. **Click** `Encrypt Message` — see the ciphertext (blocks of large integers)
6. **Click** `Decrypt Ciphertext` — see the original message recovered
7. **Click** `Show Mathematics` — see the step-by-step RSA calculations

---

## Sample Demonstration

**Input message:** `Hello World`

**After Generate Keys (128-bit example):**
```
p = 287438...  (large prime)
q = 319521...  (large prime)
n = p × q
φ(n) = (p-1)(q-1)
e = 65537
d = computed modular inverse
```

**After Encrypt:**
```
Ciphertext: 18273645... | 99234512... | ...
```

**After Decrypt:**
```
Hello World
```
✓ Decrypted text matches original.

---

## Limitations (Phase 1)

- Small key sizes (64-bit primes) are used for demo speed — not secure
- Block encoding is byte-based; very unusual Unicode may need padding adjustment
- No file import/export for keys or ciphertext
- Single RSA algorithm only (more algorithms planned for Phase 2)

---

## Future Work (Phase 2)

- Improved Unicode and large-message block handling
- Visual RSA process diagram (CustomTkinter canvas)
- Digital signatures demonstration
- Export/import keys to/from file
- Additional algorithms: Caesar, Vigenère, Diffie-Hellman
- Full unit tests

---

## Security Disclaimer

This application is an **educational prototype**.

- It uses smaller key sizes than production RSA (for demo speed)
- It does not implement OAEP padding (used in real RSA)
- It should **never** be used to protect real sensitive data
- Real-world RSA uses 2048-bit or 4096-bit keys

---

## Likely Viva Questions & Answers

### 1. What is modular arithmetic?
Modular arithmetic is arithmetic where numbers "wrap around" after reaching a maximum value (the modulus). For example, `17 mod 5 = 2` because 17 = 3×5 + 2. A clock is a real-world example (12-hour clock is mod 12).

### 2. What is RSA?
RSA (Rivest-Shamir-Adleman) is a public-key cryptosystem invented in 1977. It allows two parties to communicate securely without ever sharing a secret key in advance. One key encrypts (public), the other decrypts (private).

### 3. Why does RSA use prime numbers?
Prime numbers are required because RSA's security relies on the difficulty of factoring a large composite number n = p × q back into p and q. If p and q were not prime, φ(n) could not be computed simply, and the mathematical structure of RSA breaks down.

### 4. What is Euler's Totient Function φ(n)?
φ(n) counts how many integers from 1 to n are coprime with n (share no common factor other than 1). For n = p × q where p and q are distinct primes: φ(n) = (p-1)(q-1).

### 5. Why do we calculate φ(n)?
φ(n) defines the "group order" for modular exponentiation. By Euler's theorem, m^φ(n) ≡ 1 (mod n). This property is what allows RSA decryption to perfectly undo encryption.

### 6. What is GCD?
GCD (Greatest Common Divisor) is the largest integer that divides two numbers without remainder. Example: gcd(12, 8) = 4. Computed efficiently using the Euclidean Algorithm.

### 7. Why must gcd(e, φ(n)) = 1?
If gcd(e, φ(n)) = 1, then e and φ(n) are coprime, which guarantees that the modular inverse d exists. If gcd ≠ 1, d cannot be found and the key pair is invalid.

### 8. What is a modular inverse?
The modular inverse of e modulo m is a number d such that (e × d) mod m = 1. We find it using the Extended Euclidean Algorithm. In RSA, d = modular_inverse(e, φ(n)).

### 9. What are the public and private keys in RSA?
- **Public Key**: (e, n) — shared openly with everyone
- **Private Key**: (d, n) — kept secret by the owner

### 10. Why can the public key be shared?
Knowing (e, n) lets anyone encrypt a message. But decryption requires d, which requires knowing φ(n), which requires knowing p and q. Factoring n to find p and q is computationally infeasible for large n.

### 11. Why is the private key kept secret?
d is the "undo" operation for encryption. Anyone with d can decrypt any message encrypted with the corresponding public key. Revealing d breaks all security.

### 12. How does encryption work?
Convert the message to an integer m, then compute: **c = m^e mod n** (using the public key). The result c is the ciphertext.

### 13. How does decryption work?
Apply the private key to the ciphertext: **m = c^d mod n**. By RSA mathematics (Euler's theorem), this recovers the original m exactly.

### 14. Why is modular exponentiation used?
Direct computation of m^e (without mod) would produce astronomically large numbers. Modular exponentiation keeps numbers small by reducing modulo n at each step, making it computationally practical.

### 15. What does pow(a, b, m) do in Python?
`pow(a, b, m)` computes **(a ** b) % m** efficiently using the square-and-multiply algorithm. It runs in O(log b) multiplications instead of computing a^b first (which would be impossibly large).

### 16. Why are p and q kept secret in real RSA?
Knowing p and q allows anyone to compute φ(n) = (p-1)(q-1), and from that compute d = modular_inverse(e, φ(n)), which is the private key. So revealing p or q completely breaks the encryption.

### 17. Why is this educational implementation not production-ready?
- Uses small key sizes (faster but less secure)
- No OAEP padding (real RSA includes randomised padding to prevent attacks)
- No constant-time operations (vulnerable to timing attacks)
- No certificate infrastructure
- Intended only for understanding the mathematics

### 18. What happens if the message is larger than the RSA modulus n?
The message integer m must satisfy m < n for RSA to work. If the message is larger, we split it into smaller "blocks" (chunks of bytes), encrypt each block separately, and concatenate the results. Decryption reverses this.

### 19. Why do we split the message into blocks?
RSA can only encrypt integers in the range [0, n-1]. A long message encoded as one big integer would exceed n. Block splitting solves this while keeping each block's integer value strictly below n.

### 20. What is the time complexity of RSA operations?
- Key generation: O(k³) approximately, where k is the key size in bits (primality testing with Miller-Rabin runs in O(k²) per round × log(k) rounds)
- Encryption/Decryption: O(k²) per block using fast modular exponentiation
- This is why real-world RSA with 2048-bit keys is slower than symmetric ciphers like AES
