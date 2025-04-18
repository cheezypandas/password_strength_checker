import math
import hashlib
import requests
import tkinter as tk
from tkinter import ttk, messagebox

# 📖 The secret alphabets of password wisdom
LOWERCASE = "abcdefghijklmnopqrstuvwxyz"
UPPERCASE = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
DIGITS = "0123456789"
SYMBOLS = "!\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~"

# 🧙 Step into the Oracle's chamber...
def get_charset_size(password):
    """Figures out how many types of characters your password uses."""
    charset = 0
    if any(c in LOWERCASE for c in password):
        charset += len(LOWERCASE)
    if any(c in UPPERCASE for c in password):
        charset += len(UPPERCASE)
    if any(c in DIGITS for c in password):
        charset += len(DIGITS)
    if any(c in SYMBOLS for c in password):
        charset += len(SYMBOLS)
    return charset

def calculate_entropy(password):
    """Calculates how unpredictable (aka secure) your password is."""
    length = len(password)
    charset_size = get_charset_size(password)
    return 0 if charset_size == 0 else length * math.log2(charset_size)

def estimate_crack_time(entropy, guesses_per_second=10_000_000_000):
    """Estimates how long a brute-force attacker would need (offline attack)."""
    total_combos = 2 ** entropy
    return total_combos / guesses_per_second

def format_time(seconds):
    """Translates seconds into a more human-friendly format."""
    if seconds < 1:
        return "🤯 less than 1 second"
    minute, hour, day, year = 60, 3600, 86400, 31557600
    if seconds < minute:
        return f"{seconds:.1f} seconds"
    elif seconds < hour:
        return f"{seconds / minute:.1f} minutes"
    elif seconds < day:
        return f"{seconds / hour:.1f} hours"
    elif seconds < year:
        return f"{seconds / day:.1f} days"
    else:
        return f"{seconds / year:.2f} years"

def rate_entropy(entropy):
    """Returns a sassy label for your entropy score."""
    if entropy < 28:
        return "🧻 Very Weak"
    elif entropy < 36:
        return "🚪 Weak"
    elif entropy < 60:
        return "🔐 Moderate"
    elif entropy < 128:
        return "🛡️ Strong"
    else:
        return "🧠 Legendary"

def check_pwned(password):
    """Talks to the HaveIBeenPwned oracle to check if this password has ever been spotted in the wild."""
    sha1 = hashlib.sha1(password.encode('utf-8')).hexdigest().upper()
    prefix, suffix = sha1[:5], sha1[5:]

    url = f"https://api.pwnedpasswords.com/range/{prefix}"
    try:
        res = requests.get(url, timeout=5)
        if res.status_code != 200:
            return None
        hashes = res.text.splitlines()
        for line in hashes:
            hash_suffix, count = line.split(":")
            if hash_suffix == suffix:
                return int(count)
        return 0
    except:
        return None

def check_password():
    """The Big Button handler: crunch the stats, speak the truth."""
    password = entry.get()
    if not password:
        messagebox.showinfo("Oracle whispers...", "You must enter a password, brave one.")
        return

    # 👀 Easter eggs
    if password.lower() in ["password", "123456", "admin", "letmein"]:
        messagebox.showwarning("👀 Really?", "This password is basically a welcome mat for hackers.")

    entropy = calculate_entropy(password)
    rating = rate_entropy(entropy)
    crack_time = estimate_crack_time(entropy)
    crack_estimate = format_time(crack_time)
    breach_count = check_pwned(password)

    entropy_var.set(f"{entropy:.2f} bits of entropy")
    rating_var.set(f"Rating: {rating}")
    crack_var.set(f"⏳ Crack Time: {crack_estimate}")

    if breach_count is None:
        breach_var.set("⚠️ Couldn't reach the breach oracle.")
        breach_label.config(fg="orange")
    elif breach_count == 0:
        breach_var.set("✅ Not found in any known breaches!")
        breach_label.config(fg="green")
    else:
        breach_var.set(f"🚨 Found in {breach_count:,} breaches!")
        breach_label.config(fg="red")

# 🌟 GUI Setup – Welcome to the Oracle Interface
root = tk.Tk()
root.title("PassSage – Your Password Oracle")
root.geometry("480x330")
root.resizable(False, False)

style = ttk.Style()
style.configure("TLabel", font=("Segoe UI", 11))
style.configure("TButton", font=("Segoe UI", 11))

frame = ttk.Frame(root, padding=20)
frame.pack(fill=tk.BOTH, expand=True)

ttk.Label(frame, text="🔐 Enter your password:", font=("Segoe UI", 12, "bold")).pack(anchor="w", pady=(0, 5))
entry = ttk.Entry(frame, show="*", font=("Segoe UI", 12), width=35)
entry.pack(pady=5)

ttk.Button(frame, text="🧙 Reveal My Password Strength", command=check_password).pack(pady=10)

entropy_var = tk.StringVar()
rating_var = tk.StringVar()
crack_var = tk.StringVar()
breach_var = tk.StringVar()

ttk.Label(frame, textvariable=entropy_var, foreground="#333").pack(anchor="w", pady=(10, 0))
ttk.Label(frame, textvariable=rating_var, foreground="#333").pack(anchor="w")
ttk.Label(frame, textvariable=crack_var, foreground="#555").pack(anchor="w")
breach_label = tk.Label(frame, textvariable=breach_var, font=("Segoe UI", 10))
breach_label.pack(anchor="w", pady=(5, 0))

# 🌌 Begin the journey
root.mainloop()
