"""
Lightweight, deterministic demo responder.

It lets the app be explored before an API key is added, and it demonstrates the same
domain guardrail as the system prompt (off-topic questions are redirected). The UI
clearly labels when Demo mode is active, so it is never confused with the live model.
"""

from __future__ import annotations

OFF_TOPIC_WORDS = (
    "weather", "football", "cricket", "politics", "president", "election", "homework",
    "python", "javascript", "coding", "recipe", "movie", "celebrity", "stock",
    "investment", "doctor", "diagnose", "lawyer", "lawsuit", "translate", "math problem",
)

REDIRECT = (
    "I'm the furniture and interiors specialist here at Maison & Grain, so I'll leave "
    "that one to the experts! Tell me about your space instead — what room are we "
    "working on? 🛋️"
)


def demo_reply(text: str) -> str:
    """Keyword-based stand-in used only when Demo mode is enabled."""
    t = text.lower().strip()

    if any(word in t for word in OFF_TOPIC_WORDS):
        return REDIRECT

    if any(word in t for word in ("hello", "hi ", "hey", "good morning", "good evening")):
        return (
            "Hello! Welcome to Maison & Grain. ✨ I'm Maya. Tell me what room you're "
            "working on, your style, or a piece you're considering, and I'll help you "
            "find a lovely fit."
        )

    if any(word in t for word in ("sofa", "couch", "settee", "small living", "sectional")):
        return (
            "For a living room, two of our favourites are:\n\n"
            "- **Linden Bouclé Sofa** — 210 cm wide, cream bouclé, from $1,890 indicative. "
            "Its light tone and low profile make small rooms feel more open, and there's "
            "a stain-resistant option.\n"
            "- **Marlow Modular Sectional** — from $2,450 indicative. Start with two "
            "modules and add more as your space grows.\n\n"
            "Leave about 90 cm of walkway around the seating. What are your room's "
            "approximate dimensions?"
        )

    if any(word in t for word in ("chair", "armchair", "lounge", "accent seat")):
        return (
            "Our **Arlo Lounge Chair** is a customer favourite — cognac leather on a "
            "walnut frame, 78 × 82 × 76 cm, from $740 indicative. It pairs beautifully "
            "with a neutral sofa and adds a warm accent. Would you like styling tips for "
            "placing it? 🌿"
        )

    if any(word in t for word in ("table", "dining", "eat", "kitchen")):
        return (
            "The **Onda Round Dining Table** is a lovely choice: solid oak, 120 cm "
            "diameter, seats 4–6, from $1,290 indicative. Its round shape keeps "
            "conversation flowing and works well in smaller dining areas. Allow about "
            "90 cm behind each chair for comfortable movement."
        )

    if any(word in t for word in ("lamp", "light", "lighting")):
        return (
            "For a warm glow, the **Halo Arc Floor Lamp** (brushed brass, linen shade, "
            "190 cm tall, from $320 indicative) is ideal beside a sofa or reading chair. "
            "Layer it with a small table lamp for a cosy, inviting room. ✨"
        )

    if any(word in t for word in ("price", "cost", "budget", "cheap", "affordable", "how much")):
        return (
            "Our indicative starting prices range from $260 for the Nori Side Table, "
            "$740 for the Arlo Lounge Chair, $1,290 for the Onda Dining Table, and "
            "$1,890 for the Linden Sofa. These are indicative only — pop into the "
            "showroom to confirm current pricing and fabric options."
        )

    if any(word in t for word in ("clean", "care", "maintain", "stain", "leather", "fabric", "bouclé", "boucle")):
        return (
            "A few simple habits go a long way:\n\n"
            "- **Bouclé:** vacuum gently with a soft brush; blot spills straight away.\n"
            "- **Leather:** wipe with a dry cloth and condition every 6–12 months.\n"
            "- **Oak:** use a slightly damp cloth and avoid standing water.\n\n"
            "Avoid harsh chemicals on all finishes. 🌿"
        )

    if any(word in t for word in ("deliver", "assembly", "warranty", "return", "shipping")):
        return (
            "Delivery within the metro area takes 3–7 business days, and assembly "
            "service is available. Sofa frames carry a 10-year warranty and tables 5 "
            "years. Our style consultations in the showroom are complimentary."
        )

    if any(word in t for word in ("measure", "size", "dimension", "fit", "space")):
        return (
            "Start by measuring the room, plus doorways and stairwells for delivery. "
            "Mark out the footprint with masking tape and leave around 90 cm of walkway "
            "on main routes. If you tell me the room's length and width, I can suggest "
            "pieces that fit. 📏"
        )

    if any(word in t for word in ("colour", "color", "style", "palette", "decor", "match")):
        return (
            "Warm neutrals — oatmeal, sand, terracotta and walnut — are timeless and "
            "pair beautifully with our cream bouclé and cognac leather pieces. Add "
            "texture with a woven rug and a linen throw. What colours are already in "
            "your room? ✨"
        )

    return (
        "I'd love to help you find the right piece. I can advise on sofas and chairs, "
        "materials and care, sizing and layout, styling, and our delivery and warranty "
        "options. Which room are we working on?"
    )
