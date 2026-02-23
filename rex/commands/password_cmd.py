"""Generate secure passwords & passphrases."""

import secrets
import string
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box

console = Console()
app = typer.Typer(no_args_is_help=True)

# EFF large wordlist (subset for passphrases)
WORDLIST = [
    "abandon", "ability", "abstract", "academy", "access", "accident", "account",
    "achieve", "acoustic", "acquire", "across", "action", "adapt", "address",
    "adjust", "admiral", "advance", "advice", "aerobic", "afford", "again",
    "agent", "agree", "airport", "alarm", "album", "alert", "alien", "alpha",
    "already", "anchor", "ancient", "anger", "animal", "announce", "another",
    "answer", "antenna", "antique", "anxiety", "apart", "apology", "apple",
    "arena", "armor", "army", "arrow", "artist", "assault", "asset", "atlas",
    "auction", "audit", "august", "autumn", "avenue", "average", "avocado",
    "bamboo", "banana", "banner", "barrel", "basket", "battle", "beacon",
    "beauty", "become", "before", "behind", "believe", "beneath", "benefit",
    "bicycle", "blanket", "blossom", "border", "bounce", "brave", "breeze",
    "bridge", "bronze", "bubble", "budget", "bullet", "bundle", "butter",
    "cabin", "cable", "cactus", "camera", "campus", "candle", "canyon",
    "capital", "captain", "carbon", "carpet", "castle", "catalog", "ceiling",
    "cement", "census", "century", "cereal", "certain", "champion", "chapter",
    "cherry", "chicken", "chimney", "choice", "chronic", "circle", "citizen",
    "clarify", "climate", "cluster", "coconut", "collect", "column", "combine",
    "comfort", "command", "common", "company", "compass", "confirm", "congress",
    "connect", "control", "convert", "cookie", "copper", "coral", "cotton",
    "country", "couple", "course", "cousin", "cradle", "craft", "cream",
    "cricket", "criminal", "crisis", "crystal", "culture", "curtain", "cycle",
    "dagger", "damage", "danger", "daring", "dawn", "debate", "decade",
    "defense", "define", "degree", "delay", "deliver", "demand", "depart",
    "deposit", "desert", "design", "detail", "develop", "device", "devote",
    "diamond", "digital", "dilemma", "dinner", "dinosaur", "direct", "discover",
    "display", "distance", "divide", "dolphin", "domain", "dragon", "drama",
    "dream", "driver", "during", "dynamic", "eagle", "earth", "easily",
    "ecology", "economy", "edition", "educate", "effort", "elastic", "elder",
    "electric", "elegant", "element", "elephant", "elevator", "embrace", "emerge",
    "emotion", "emperor", "enable", "enclose", "encounter", "endorse", "enemy",
    "energy", "enforce", "engage", "engine", "enhance", "enjoy", "enlist",
    "enough", "enrich", "entire", "episode", "equip", "erosion", "escape",
    "essence", "estate", "eternal", "evening", "evidence", "evolve", "example",
    "excess", "exchange", "exclude", "execute", "exhaust", "exhibit", "exile",
    "expand", "expect", "explain", "expose", "express", "extend", "extract",
    "fabric", "faculty", "falcon", "family", "fantasy", "fashion", "father",
    "feature", "federal", "fiction", "figure", "filter", "final", "finger",
    "fiscal", "fitness", "flight", "flower", "flutter", "follow", "force",
    "forest", "fortune", "fossil", "founder", "fragile", "frame", "freedom",
    "frequent", "frozen", "furnace", "future", "galaxy", "garden", "garlic",
    "gather", "general", "genius", "gentle", "gesture", "giant", "glacier",
    "glimpse", "global", "goddess", "golden", "gospel", "gossip", "govern",
    "grace", "grain", "granite", "graphic", "gravity", "guitar", "harvest",
    "hazard", "health", "helmet", "heritage", "hidden", "highway", "history",
    "hockey", "holiday", "hollow", "horizon", "horror", "humble", "hunger",
    "hybrid", "ignore", "illegal", "illusion", "imagine", "impact", "import",
    "impulse", "include", "income", "indicate", "industry", "infant", "inflict",
    "inform", "inherit", "initial", "inject", "inner", "innocent", "input",
    "inquiry", "install", "intact", "interest", "interval", "involve", "island",
    "isolate", "ivory", "jacket", "jaguar", "journey", "jungle", "justice",
    "kangaroo", "kernel", "kingdom", "kitchen", "kiwi", "knight", "label",
    "ladder", "lambda", "language", "laptop", "lateral", "launch", "leader",
    "lecture", "legend", "leisure", "leopard", "letter", "liberty", "library",
    "license", "linger", "liquid", "lobster", "logic", "lottery", "lunar",
    "machine", "magnet", "mammoth", "mandate", "mansion", "manual", "maple",
    "margin", "marine", "market", "martial", "master", "matrix", "maximum",
    "meadow", "measure", "medical", "melody", "mentor", "mercury", "method",
    "midnight", "million", "mineral", "minimum", "miracle", "mission", "mixture",
    "mobile", "model", "modify", "moment", "monitor", "monster", "morning",
    "mountain", "multiply", "muscle", "mystery", "narrow", "nation", "nature",
    "navigate", "network", "neutral", "noble", "nominal", "normal", "notable",
    "nothing", "novel", "nuclear", "number", "observe", "obtain", "obvious",
    "ocean", "october", "officer", "olive", "olympic", "opinion", "oppose",
    "option", "orange", "orbit", "ordinary", "orient", "orphan", "ostrich",
    "outdoor", "output", "oxygen", "oyster", "paddle", "palace", "panda",
    "panther", "parachute", "parcel", "partner", "passage", "patient", "patrol",
    "pattern", "payment", "penalty", "pension", "perfect", "permit", "person",
    "phoenix", "phrase", "physics", "picnic", "picture", "pilgrim", "pioneer",
    "pistol", "planet", "plastic", "platform", "plunge", "pocket", "polar",
    "portion", "position", "possible", "pottery", "poverty", "powder", "prairie",
    "predict", "premium", "present", "prevent", "primary", "priority", "prison",
    "private", "problem", "process", "produce", "program", "project", "promote",
    "prosper", "protect", "protein", "provide", "public", "pudding", "purchase",
    "purpose", "puzzle", "pyramid", "quantum", "quarter", "question", "quiz",
    "rabbit", "raccoon", "radical", "railway", "rainbow", "random", "ranger",
    "rebuild", "receive", "reflect", "reform", "region", "regular", "release",
    "remark", "remind", "remove", "render", "repair", "replace", "require",
    "rescue", "resemble", "resist", "resource", "response", "result", "retreat",
    "reunion", "revenue", "review", "revolve", "rhythm", "ribbon", "ritual",
    "robust", "rocket", "romance", "royal", "rubber", "rumor", "runway",
    "saddle", "safari", "salad", "salmon", "salon", "sample", "sandal",
    "satisfy", "saturn", "sausage", "scatter", "scholar", "scissors", "scorpion",
    "season", "section", "segment", "seminar", "senator", "senior", "session",
    "shadow", "shelter", "sheriff", "shuttle", "sibling", "signal", "silent",
    "silver", "similar", "simple", "siren", "sister", "slender", "slogan",
    "smart", "soccer", "social", "soldier", "solution", "someone", "spatial",
    "special", "sphere", "spider", "sponsor", "spring", "squeeze", "stadium",
    "stairs", "stamp", "station", "stereo", "stomach", "strategy", "student",
    "stumble", "subject", "success", "sugar", "suggest", "summer", "sunset",
    "supreme", "surface", "surplus", "surprise", "surround", "suspect", "sustain",
    "swallow", "symptom", "system", "tactic", "talent", "target", "tattoo",
    "teacher", "temple", "tenant", "terminal", "terrain", "texture", "theater",
    "therapy", "thrive", "thunder", "ticket", "timber", "together", "token",
    "tomato", "tonight", "torpedo", "tortoise", "tourist", "tower", "traffic",
    "transfer", "transit", "treasure", "trigger", "triumph", "trouble", "trumpet",
    "tunnel", "turtle", "umbrella", "uncover", "undergo", "unfair", "uniform",
    "universe", "unknown", "unusual", "upgrade", "uphold", "uranium", "utility",
    "vaccine", "vacuum", "valley", "vampire", "vanilla", "various", "venture",
    "version", "veteran", "vibrant", "victory", "village", "vintage", "violin",
    "virtual", "visible", "visitor", "visual", "volcano", "voltage", "volume",
    "voyage", "vulture", "walnut", "warrior", "weather", "wedding", "welcome",
    "western", "whisper", "wicked", "window", "winner", "winter", "wisdom",
    "witness", "wonder", "wrestle", "zombie",
]


@app.command("generate")
def generate(
    length: int = typer.Option(24, "--length", "-l", help="Password length"),
    count: int = typer.Option(1, "--count", "-c", help="Number of passwords to generate"),
    uppercase: bool = typer.Option(True, "--uppercase/--no-uppercase", help="Include uppercase letters"),
    lowercase: bool = typer.Option(True, "--lowercase/--no-lowercase", help="Include lowercase letters"),
    digits: bool = typer.Option(True, "--digits/--no-digits", help="Include digits"),
    symbols: bool = typer.Option(True, "--symbols/--no-symbols", help="Include symbols"),
    exclude: Optional[str] = typer.Option(None, "--exclude", "-e", help="Characters to exclude"),
):
    """Generate a secure random password."""
    charset = ""
    if uppercase:
        charset += string.ascii_uppercase
    if lowercase:
        charset += string.ascii_lowercase
    if digits:
        charset += string.digits
    if symbols:
        charset += "!@#$%^&*()-_=+[]{}|;:,.<>?"

    if exclude:
        charset = "".join(c for c in charset if c not in exclude)

    if not charset:
        console.print("[red]✗ No characters available with current settings.[/red]")
        raise typer.Exit(1)

    table = Table(title="🔑 Generated Passwords", box=box.ROUNDED, border_style="green")
    table.add_column("#", style="dim", width=4)
    table.add_column("Password", style="bold white")
    table.add_column("Strength", style="cyan")

    for i in range(count):
        pw = "".join(secrets.choice(charset) for _ in range(length))
        entropy = len(pw) * (len(charset).bit_length())
        if entropy >= 128:
            strength = "[green]● Excellent[/green]"
        elif entropy >= 80:
            strength = "[yellow]● Good[/yellow]"
        elif entropy >= 60:
            strength = "[yellow]● Fair[/yellow]"
        else:
            strength = "[red]● Weak[/red]"
        table.add_row(str(i + 1), pw, strength)

    console.print(table)


@app.command("passphrase")
def passphrase(
    words: int = typer.Option(6, "--words", "-w", help="Number of words"),
    separator: str = typer.Option("-", "--separator", "-s", help="Word separator"),
    capitalize: bool = typer.Option(False, "--capitalize", "-c", help="Capitalize first letter of each word"),
    count: int = typer.Option(1, "--count", "-n", help="Number of passphrases"),
):
    """Generate a memorable passphrase."""
    table = Table(title="🔑 Generated Passphrases", box=box.ROUNDED, border_style="green")
    table.add_column("#", style="dim", width=4)
    table.add_column("Passphrase", style="bold white")

    for i in range(count):
        chosen = [secrets.choice(WORDLIST) for _ in range(words)]
        if capitalize:
            chosen = [w.capitalize() for w in chosen]
        phrase = separator.join(chosen)
        table.add_row(str(i + 1), phrase)

    console.print(table)
    console.print(f"[dim]Entropy: ~{int(words * 11)} bits ({len(WORDLIST)} word pool)[/dim]")
