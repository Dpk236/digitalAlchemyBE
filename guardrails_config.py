# config/guardrails_config.py
"""
Guardrail Configuration

Customize what's allowed and blocked in student interactions.
This file makes it easy to adjust guardrails without changing code.
"""

from typing import Dict, List, Set


class GuardrailConfig:
    """
    Configuration for content guardrails.
    
    Modify these settings to customize what students can ask about.
    """
    
    # ===== BLOCKED TOPICS =====
    # These topics will be blocked unless they have educational framing
    
    BLOCKED_TOPICS: Dict[str, List[str]] = {
        # Entertainment
        "movies": [
            "movie", "film", "actor", "actress", "hollywood", "bollywood", 
            "cinema", "netflix", "disney", "marvel", "dc comics", "avengers",
            "spider-man", "batman", "oscar", "blockbuster"
        ],
        "tv_shows": [
            "tv show", "series", "episode", "season", "sitcom", "drama series",
            "reality show", "game of thrones", "stranger things", "breaking bad"
        ],
        "cartoons_anime": [
            "cartoon", "anime", "animated", "pokemon", "naruto", "dragon ball",
            "ben 10", "doraemon", "one piece", "attack on titan", "shinchan",
            "tom and jerry", "oggy", "motu patlu"
        ],
        "music_entertainment": [
            "singer", "song lyrics", "album", "concert", "band", "rapper",
            "pop star", "playlist", "spotify", "music video", "billboard",
            "bts", "taylor swift", "arijit singh"
        ],
        "celebrities": [
            "celebrity", "famous person", "star", "influencer", "youtuber",
            "tiktoker", "instagram model", "kardashian", "gossip"
        ],
        
        # Sports (non-physics context)
        "sports_entertainment": [
            "match score", "tournament", "world cup", "ipl", "fifa", "nba", 
            "nfl", "cricket score", "football score", "player stats",
            "team ranking", "who won", "championship", "league table",
            "transfer news", "injury update"
        ],
        
        # Gaming
        "video_games": [
            "video game", "gaming", "fortnite", "minecraft", "pubg", "gta",
            "call of duty", "fifa game", "free fire", "roblox", "valorant",
            "playstation", "xbox", "nintendo", "esports", "twitch stream"
        ],
        
        # Social Media
        "social_media": [
            "instagram post", "tiktok video", "snapchat", "twitter trending",
            "facebook", "followers", "viral video", "meme", "reels",
            "social media influencer"
        ],
        
        # Personal/Lifestyle
        "relationships": [
            "boyfriend", "girlfriend", "dating", "relationship advice",
            "breakup", "crush", "love life", "marriage"
        ],
        "fashion_beauty": [
            "fashion trend", "outfit", "makeup tutorial", "skincare routine",
            "hairstyle", "shopping haul", "brand recommendation"
        ],
        
        # Food/Travel (casual)
        "casual_food": [
            "restaurant recommendation", "food review", "best pizza",
            "where to eat", "cooking show", "mukbang"
        ],
        "casual_travel": [
            "vacation destination", "holiday spot", "tourist attraction",
            "travel vlog", "hotel review"
        ],
        
        # Other
        "shopping": [
            "buy online", "amazon deal", "flipkart sale", "discount code",
            "product review", "shopping recommendation"
        ],
        "news_politics": [
            "political news", "election", "politician", "controversy",
            "scandal", "debate"
        ],
    }
    
    # ===== ALLOWED EDUCATIONAL EXTENSIONS =====
    # When studying subject X, topics in this list are allowed
    
    EDUCATIONAL_EXTENSIONS: Dict[str, List[str]] = {
        "physics": [
            # Mathematics
            "mathematics", "calculus", "differential equations", "integration",
            "differentiation", "algebra", "trigonometry", "geometry", "vectors",
            "matrices", "linear algebra", "statistics", "probability",
            
            # Related Sciences
            "chemistry", "thermodynamics", "quantum mechanics", "relativity",
            "astronomy", "astrophysics", "cosmology", "engineering",
            "electronics", "electrical circuits", "optics",
            
            # Applications
            "robotics", "aerospace", "mechanical engineering", "civil engineering",
        ],
        
        "chemistry": [
            "physics", "mathematics", "biology", "biochemistry",
            "organic chemistry", "inorganic chemistry", "physical chemistry",
            "thermodynamics", "quantum chemistry", "electrochemistry",
            "pharmacology", "materials science", "environmental science",
        ],
        
        "biology": [
            "chemistry", "biochemistry", "physics", "biophysics",
            "genetics", "molecular biology", "cell biology", "anatomy",
            "physiology", "ecology", "evolution", "microbiology",
            "botany", "zoology", "neuroscience", "immunology",
        ],
        
        "mathematics": [
            "physics", "statistics", "computer science", "logic",
            "number theory", "abstract algebra", "topology", "analysis",
            "discrete mathematics", "combinatorics", "graph theory",
            "cryptography", "game theory", "optimization",
        ],
        
        "computer_science": [
            "mathematics", "logic", "algorithms", "data structures",
            "programming", "machine learning", "artificial intelligence",
            "databases", "networking", "operating systems", "cryptography",
            "software engineering", "computer architecture",
        ],
    }
    
    # ===== ALWAYS ALLOWED =====
    # These patterns are always allowed regardless of topic
    
    ALWAYS_ALLOWED_PATTERNS: List[str] = [
        # Direct video references
        r"in the video",
        r"from the lecture",
        r"at timestamp",
        r"at \d+:\d+",
        r"the teacher said",
        r"you mentioned",
        
        # Learning actions
        r"explain",
        r"understand",
        r"how does",
        r"why does",
        r"what is",
        r"what are",
        r"define",
        r"describe",
        
        # Study aids
        r"quiz me",
        r"test me",
        r"give me.*problem",
        r"practice",
        r"example",
        r"exercise",
        
        # Concept requests
        r"summary",
        r"flashcard",
        r"simulation",
        r"formula",
        r"equation",
        r"derivation",
        r"proof",
        
        # Math operations
        r"solve",
        r"calculate",
        r"compute",
        r"derive",
        r"integrate",
        r"differentiate",
    ]
    
    # ===== EDUCATIONAL FRAMING =====
    # If these phrases appear with blocked keywords, allow them
    
    EDUCATIONAL_FRAMES: List[str] = [
        "physics of",
        "science behind",
        "mathematics of",
        "calculate the",
        "trajectory of",
        "velocity of",
        "force on",
        "energy of",
        "equation for",
        "real world example",
        "application of",
        "how does.*work",
        "scientific explanation",
    ]
    
    # ===== RESPONSE TEMPLATES =====
    # Customize redirect messages
    
    REDIRECT_TEMPLATES: Dict[str, str] = {
        "entertainment": """🎬 That sounds fun, but let's focus on learning!

I'm here to help you master **{concept}**. What would you like to understand better?

💡 Try: "Explain the key concept" or "Give me a practice problem"
""",
        
        "sports": """⚽ Sports are exciting! Did you know physics is everywhere in sports?

Instead of game scores, let's explore the **science of motion**!

💡 Try: "How does physics apply to throwing a ball?"
""",
        
        "gaming": """🎮 Gaming is cool! But let's level up your **knowledge** first!

Think of learning like a game - each concept mastered = achievement unlocked! 🏆

💡 Current quest: Master **{concept}**
""",
        
        "social": """📱 Social media can wait - your future self will thank you for focusing now!

Let's make sure you understand **{concept}** really well.

💡 What part would you like me to explain?
""",
        
        "default": """🎯 Let's stay on track with your learning!

I'm here to help you with **{concept}** and related educational topics.

💡 What would you like to know about the current topic?
""",
    }
    
    # ===== ESCALATION THRESHOLDS =====
    # How to handle repeated off-topic attempts
    
    OFF_TOPIC_WARNING_THRESHOLD: int = 3  # Warnings after this many attempts
    OFF_TOPIC_STRICT_THRESHOLD: int = 5   # Stricter responses after this
    
    # ===== FEATURE FLAGS =====
    
    ENABLE_LLM_CLASSIFICATION: bool = True  # Use LLM for ambiguous cases
    ENABLE_CONTEXT_AWARENESS: bool = True   # Consider video context
    ENABLE_ESCALATION: bool = True          # Escalate for repeat offenders
    LOG_BLOCKED_QUERIES: bool = True        # Log blocked queries for review


# ===== SUBJECT-SPECIFIC CONFIGS =====

class PhysicsGuardrailConfig(GuardrailConfig):
    """Physics-specific guardrail configuration"""
    
    # Additional allowed topics for physics
    ADDITIONAL_ALLOWED = [
        "projectile motion in sports",
        "physics of cricket",
        "physics of football",
        "aerodynamics",
        "biomechanics",
        "sports science",
    ]
    
    # Physics-specific educational frames
    PHYSICS_FRAMES = [
        "trajectory", "velocity", "acceleration", "force",
        "momentum", "energy", "work", "power", "friction",
        "gravity", "motion", "kinematics", "dynamics",
    ]


class ChemistryGuardrailConfig(GuardrailConfig):
    """Chemistry-specific guardrail configuration"""
    
    ADDITIONAL_ALLOWED = [
        "cooking chemistry",
        "food science",
        "biochemistry of",
    ]
    
    CHEMISTRY_FRAMES = [
        "reaction", "compound", "element", "molecule",
        "bond", "electron", "atom", "ion", "solution",
    ]


class BiologyGuardrailConfig(GuardrailConfig):
    """Biology-specific guardrail configuration"""
    
    ADDITIONAL_ALLOWED = [
        "human body",
        "animal behavior",
        "plant biology",
        "health science",
    ]
    
    BIOLOGY_FRAMES = [
        "cell", "organism", "species", "evolution",
        "genetics", "dna", "protein", "enzyme",
    ]


# ===== FACTORY =====

def get_guardrail_config(subject: str = "physics") -> GuardrailConfig:
    """Get subject-specific guardrail configuration"""
    
    configs = {
        "physics": PhysicsGuardrailConfig,
        "chemistry": ChemistryGuardrailConfig,
        "biology": BiologyGuardrailConfig,
    }
    
    return configs.get(subject, GuardrailConfig)()
