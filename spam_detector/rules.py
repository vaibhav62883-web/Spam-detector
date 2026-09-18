"""
rules.py
--------
All keyword lists and regex patterns used by the detector.

To add a new rule, simply add a string to the appropriate list below.
No other file needs to change. All matching is case-insensitive.

Sections:
  1. Spam rules
  2. Fake / impersonation rules
  3. Scam rules
  4. Shared URL pattern
"""

# ---------------------------------------------------------------------------
# 1. SPAM RULES
# ---------------------------------------------------------------------------

# Words and phrases commonly found in unsolicited promotional messages.
SPAM_KEYWORDS: list[str] = [
    "winner",           # prize / lottery spam
    "you have been selected",
    "free offer",
    "free gift",
    "click here",
    "click below",
    "unsubscribe",      # bulk-mail footer trick
    "limited time",
    "limited time offer",
    "act now",
    "buy now",
    "order now",
    "earn money",
    "earn cash",
    "make money",
    "work from home",
    "100% free",
    "risk free",
    "no cost",
    "congratulations",  # often used in prize spam
    "special promotion",
    "exclusive deal",
    "you are a winner",
    "claim your reward",
    "double your income",
    "extra income",
    "extra cash",
]

# Regex patterns for spam formatting signals.
# Each pattern is a raw string; compiled with re.IGNORECASE in detector.py.
SPAM_PATTERNS: list[str] = [
    r"!{3,}",                       # Three or more consecutive exclamation marks
    r"\b[A-Z]{5,}\b",               # A word written entirely in capitals (5+ letters)
    r"\b(\w+)\s+\1\b",              # Immediately repeated word, e.g. "buy buy"
    r"\$\d+(?:,\d{3})*(?:\.\d+)?", # Currency amounts like $500 or $1,000
]

# ---------------------------------------------------------------------------
# 2. FAKE / IMPERSONATION RULES
# ---------------------------------------------------------------------------

# Phrases used to impersonate banks, tech companies, or services.
FAKE_KEYWORDS: list[str] = [
    "your account has been",
    "your account will be",
    "account suspended",
    "account blocked",
    "account locked",
    "verify your identity",
    "verify your account",
    "verify your details",
    "unusual activity",
    "suspicious activity",
    "security alert",
    "security notice",
    "confirm your details",
    "confirm your information",
    "your password",
    "reset your password",
    "dear customer",
    "dear user",
    "dear valued customer",
    "dear account holder",
    "update your information",
    "update your details",
    "we noticed",
    "we have detected",
    "your profile needs",
    "action required",
    "immediate action required",
    "failure to verify",
]

# Patterns for lookalike/misspelled domains used in phishing.
FAKE_PATTERNS: list[str] = [
    r"paypa[l1][^\w]",              # paypal / paypa1
    r"ama[z2]on[^\w]",              # amazon / ama2on / arnazon
    r"g[o0]{2}gle[^\w]",           # google / g00gle
    r"micr[o0]s[o0]ft[^\w]",       # microsoft / micr0s0ft
    r"app[l1]e[^\w]",              # apple / app1e
    r"ba[n]k[^\w].*verif",         # bank ... verif (bank verification scam pattern)
    r"netfl[i1]x[^\w]",           # netflix / netfl1x
]

# ---------------------------------------------------------------------------
# 3. SCAM RULES
# ---------------------------------------------------------------------------

# Phrases associated with financial scams, social engineering, and fraud.
SCAM_KEYWORDS: list[str] = [
    "send money",
    "transfer money",
    "wire transfer",
    "gift card",
    "itunes card",
    "google play card",
    "western union",
    "moneygram",
    "you have won",
    "you've won",
    "claim your prize",
    "claim your winnings",
    "bank details",
    "bank account",
    "account number",
    "routing number",
    "social security",
    "social security number",
    "ssn",
    "one time password",
    "one-time password",
    "otp",
    "enter your otp",
    "share your otp",
    "your otp is",
    "password",
    "pin number",
    "credit card",
    "debit card",
    "card number",
    "cvv",
    "urgent",
    "confidential",
    "do not tell anyone",
    "keep this secret",
    "lottery",
    "inheritance",
    "million dollars",
    "million pounds",
    "you owe",
    "arrest warrant",
    "legal action",
    "lawsuit",
    "irs",
    "tax refund",
    "customs fee",
    "delivery fee",
    "release fee",
    "processing fee",
    "prince",                       # "Nigerian prince" scam opener
    "nigerian",
    "i need your help",
    "i am contacting you",
    "dear beneficiary",
    "next of kin",
]

# Patterns for scam-specific signals.
SCAM_PATTERNS: list[str] = [
    r"https?://(?:bit\.ly|tinyurl\.com|t\.co|goo\.gl|ow\.ly|shorturl)[/\w]+",  # shortlink services
    r"\b(?:\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b",               # US/CA phone numbers
    r"\b\d{4}[\s\-]?\d{4}[\s\-]?\d{4}[\s\-]?\d{4}\b",                         # 16-digit card number
    r"\b\d{3}-\d{2}-\d{4}\b",                                                  # SSN pattern
    r"(?i)\burgen[tc](?:ly)?\b",                                                # urgently / urgent
]

# ---------------------------------------------------------------------------
# 4. SHARED URL PATTERN
# ---------------------------------------------------------------------------

# Matches any bare URL — used to flag suspicious links in general.
SUSPICIOUS_URL_PATTERN: str = r"https?://\S+"
