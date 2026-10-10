import re
import math
import hashlib
import httpx

# Top 200 common weak passwords sample for fast offline checking
COMMON_WEAK_PASSWORDS = {
    "123456", "password", "123456789", "12345678", "12345", "111111", "1234567",
    "sunshine", "qwerty", "iloveyou", "princess", "admin", "welcome", "666666",
    "abc123", "football", "monkey", "charlie", "donald", "password1", "123123",
    "trustno1", "master", "shadow", "superman", "batman", "letmein", "dragon",
    "baseball", "000000", "pass123", "hello", "secret", "killer", "login"
}

COMMON_WORDS = {
    "password", "passw", "welcome", "summer", "winter", "spring", "autumn", "football", "baseball", "dragon",
    "monkey", "sunshine", "princess", "admin", "letmein", "qwerty", "iloveyou", "shadow", "master", "superman",
    "batman", "trustno", "secret", "login", "hello", "charlie", "freedom", "michael", "jordan", "hunter",
}

LEET = str.maketrans({"0": "o", "1": "i", "3": "e", "4": "a", "5": "s", "7": "t", "@": "a", "$": "s", "!": "i"})


def find_common_word(password: str):
    lowered = password.lower()
    candidates = {lowered, lowered.translate(LEET), lowered.translate(LEET).replace("i", "l")}
    for word in sorted(COMMON_WORDS, key=len, reverse=True):
        if any(word in c for c in candidates):
            return word
    return None


def calculate_entropy(password: str) -> float:
    if not password:
        return 0.0
    
    pool_size = 0
    if re.search(r'[a-z]', password):
        pool_size += 26
    if re.search(r'[A-Z]', password):
        pool_size += 26
    if re.search(r'[0-9]', password):
        pool_size += 10
    if re.search(r'[^a-zA-Z0-9]', password):
        pool_size += 32
        
    if pool_size == 0:
        return 0.0
        
    entropy = len(password) * math.log2(pool_size)
    return round(entropy, 2)

def estimate_crack_time(entropy: float) -> str:
    # Assuming 100 Billion (10^11) guesses per second for standard offline brute-force attack
    guesses = 2 ** entropy
    seconds = guesses / 100_000_000_000
    
    if seconds < 1:
        return "Instantly"
    elif seconds < 60:
        return f"{int(seconds)} seconds"
    elif seconds < 3600:
        return f"{int(seconds / 60)} minutes"
    elif seconds < 86400:
        return f"{int(seconds / 3600)} hours"
    elif seconds < 31536000:
        return f"{int(seconds / 86400)} days"
    elif seconds < 31536000 * 100:
        return f"{int(seconds / 31536000)} years"
    elif seconds < 31536000 * 1_000_000:
        return "Centuries"
    else:
        return "Millions of years"

async def check_hibp_breached(password: str) -> dict:
    """Uses HaveIBeenPwned k-Anonymity API (safe SHA-1 prefix lookup)"""
    try:
        sha1_pwd = hashlib.sha1(password.encode('utf-8')).hexdigest().upper()
        prefix = sha1_pwd[:5]
        suffix = sha1_pwd[5:]
        
        async with httpx.AsyncClient(timeout=4.0) as client:
            resp = await client.get(f"https://api.pwnedpasswords.com/range/{prefix}", headers={"Add-Padding": "true"})
            resp.raise_for_status()
            for line in resp.text.splitlines():
                parts = line.strip().split(':')
                if len(parts) == 2 and parts[0] == suffix and int(parts[1]) > 0:
                    return {"is_breached": True, "count": int(parts[1]), "checked": True, "source": "Have I Been Pwned"}
        return {"is_breached": False, "count": 0, "checked": True, "source": "Have I Been Pwned"}
    except Exception:
        # Fallback to local offline check if offline or API blocked
        if password.lower() in COMMON_WEAK_PASSWORDS:
            return {"is_breached": True, "count": None, "checked": False, "source": "Built-in list of common passwords"}
        return {"is_breached": False, "count": 0, "checked": False, "source": "Breach database unreachable"}

def analyze_password(password: str) -> dict:
    length = len(password)
    has_lower = bool(re.search(r'[a-z]', password))
    has_upper = bool(re.search(r'[A-Z]', password))
    has_digit = bool(re.search(r'[0-9]', password))
    has_symbol = bool(re.search(r'[^a-zA-Z0-9]', password))
    
    entropy = calculate_entropy(password)
    crack_time = estimate_crack_time(entropy)
    
    warnings = []
    suggestions = []
    score = 0
    
    # Length checks
    if length < 8:
        warnings.append("Password is too short (fewer than 8 characters).")
        suggestions.append("Increase length to at least 12–16 characters.")
    elif length >= 16:
        score += 40
    elif length >= 12:
        score += 30
    else:
        score += 15
        
    # Complexity checks
    types_count = sum([has_lower, has_upper, has_digit, has_symbol])
    score += types_count * 15
    
    if not has_upper:
        suggestions.append("Add uppercase letters (A-Z).")
    if not has_lower:
        suggestions.append("Add lowercase letters (a-z).")
    if not has_digit:
        suggestions.append("Add numbers (0-9).")
    if not has_symbol:
        suggestions.append("Add special symbols (!@#$%^&*).")
        
    # Pattern checks
    if password.lower() in COMMON_WEAK_PASSWORDS:
        score = min(score, 10)
        warnings.append("This is an extremely common password.")
        suggestions.append("Avoid generic dictionary words or common phrases.")
        
    if re.search(r'(1234|qwerty|asdf|abcd|0000|1111|password)', password.lower()):
        score = max(0, score - 20)
        warnings.append("Contains easy keyboard patterns or sequential numbers.")
        
    common_word = find_common_word(password)
    if common_word and password.lower() not in COMMON_WEAK_PASSWORDS:
        score = max(0, score - 30)
        warnings.append(f"Built around a common word ('{common_word}'), even with letters swapped for numbers or symbols.")
        suggestions.append("Use several random, unrelated words instead of one common word.")

    if re.search(r'(19|20)\d{2}', password):
        score = max(0, score - 10)
        warnings.append("Contains a year, which attackers routinely add to their guesses.")

    if re.search(r'(.)\1{2,}', password):
        score = max(0, score - 15)
        warnings.append("Contains repeated characters (e.g. 'aaa').")
        
    # Entropy booster
    if entropy > 60:
        score = min(100, score + 10)
        
    score = max(0, min(100, score))
    
    # Rating label
    if score >= 80:
        rating = "Very Strong"
        badge_color = "success"
    elif score >= 60:
        rating = "Strong"
        badge_color = "info"
    elif score >= 40:
        rating = "Moderate"
        badge_color = "warning"
    else:
        rating = "Weak"
        badge_color = "danger"
        
    return {
        "password_length": length,
        "score": score,
        "rating": rating,
        "badge_color": badge_color,
        "entropy_bits": entropy,
        "crack_time": crack_time,
        "checks": {
            "has_uppercase": has_upper,
            "has_lowercase": has_lower,
            "has_digits": has_digit,
            "has_symbols": has_symbol,
            "sufficient_length": length >= 12
        },
        "warnings": warnings,
        "suggestions": suggestions
    }
