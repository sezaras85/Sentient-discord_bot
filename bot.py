import discord
import requests
import re

# Fireworks AI API credentials
FIREWORKS_API_KEY = "YOUR_FIREWORKS_API_KEY"
FIREWORKS_API_URL = "https://api.fireworks.ai/inference/v1/completions"

# Discord bot token
DISCORD_BOT_TOKEN = "YOUR_DISCORD_BOT_TOKEN"

# Discord client permissions
intents = discord.Intents.default()
intents.message_content = True  # Needed to read user messages

# Initialize bot
client = discord.Client(intents=intents)

# List of profane and toxic words (can be expanded)
BAD_WORDS = [
    "fuck", "shit", "bitch", "asshole", "damn", "dick", "piss", "fucking", "motherfucker",
    "cunt", "fag", "retard", "nigger", "dyke", "slut", "whore", "bollocks", "arsehole"
]

def clean_toxic_language(text):
    """Censors profane and toxic language, reduces repeated characters, and softens excessive shouting."""
    
    # Censor bad words
    for word in BAD_WORDS:
        pattern = re.compile(rf"\b{word}\b", re.IGNORECASE)
        text = pattern.sub("[censored]", text)

    # Reduce excessively repeated characters (e.g. aaaa -> aaa)
    text = re.sub(r'(.)\1{3,}', r'\1\1\1', text)

    # Soften ALL-CAPS words (yelling)
    def fix_caps(m):
        word = m.group()
        return word.capitalize() if len(word) > 2 else word
    text = re.sub(r'\b[A-Z]{3,}\b', fix_caps, text)

    # Replace specific aggressive phrases
    aggressive_replacements = {
        r"fuck off": "[censored]",
        r"shut up": "[please be kind]",
        r"bitch": "[censored]",
        r"dogshit": "bad",
        r"idiot": "a bit careless",
    }
    for pattern, replacement in aggressive_replacements.items():
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)

    return text.strip()

def generate_reply(message_text):
    """Generates a reply using Fireworks AI"""
    headers = {
        "Authorization": f"Bearer {FIREWORKS_API_KEY}",
        "Content-Type": "application/json"
    }

    prompt = f'Reply to this Discord message in a helpful, friendly tone: "{message_text}"'

    payload = {
        "model": "accounts/sentientfoundation/models/dobby-unhinged-llama-3-3-70b-new",
        "prompt": prompt,
        "max_tokens": 240,
        "temperature": 0.7,
        "top_p": 0.9
    }

    try:
        response = requests.post(FIREWORKS_API_URL, json=payload, headers=headers)
        response.raise_for_status()
        reply = response.json().get("choices", [{}])[0].get("text", "").strip()
        cleaned_reply = clean_toxic_language(reply)
        return cleaned_reply if cleaned_reply else "Sorry, I didn't understand that."
    except Exception as e:
        print(f"❌ Fireworks API Error: {e}")
        return "Something went wrong 😞"

@client.event
async def on_ready():
    print(f"✅ Logged in as: {client.user}")

@client.event
async def on_message(message):
    if message.author == client.user:
        return  # Don't respond to own messages

    if message.content.startswith("!"):
        return  # Skip bot commands

    reply = generate_reply(message.content)
    await message.channel.send(reply)

# Run the bot
client.run(DISCORD_BOT_TOKEN)
