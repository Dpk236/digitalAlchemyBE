# Helpers/guardrail_manager.py

import re
from typing import Optional, Tuple
from guardrails_config import GuardrailConfig, get_guardrail_config

class GuardrailManager:
    """
    Manages user query filtering based on GuardrailConfig.
    """
    
    def __init__(self, subject: str = "physics"):
        self.config: GuardrailConfig = get_guardrail_config(subject)
        self.subject = subject
        
        # Pre-compile regex patterns for performance
        self.always_allowed_regex = [re.compile(p, re.IGNORECASE) for p in self.config.ALWAYS_ALLOWED_PATTERNS]
        self.educational_frames_regex = [re.compile(re.escape(f), re.IGNORECASE) for f in self.config.EDUCATIONAL_FRAMES]
        
        # For subject specific frames
        if hasattr(self.config, f"{subject.upper()}_FRAMES"):
            extra_frames = getattr(self.config, f"{subject.upper()}_FRAMES")
            self.educational_frames_regex.extend([re.compile(re.escape(f), re.IGNORECASE) for f in extra_frames])

    def check_query(self, query: str) -> Tuple[bool, Optional[str]]:
        """
        Checks if a query should be blocked.
        Returns: (is_blocked, redirect_message)
        """
        query_lower = query.lower().strip()
        
        # 1. Check Blocked Topics First (with Educational Framing as exception)
        blocked_category = None
        blocked_keyword = None
        
        for category, keywords in self.config.BLOCKED_TOPICS.items():
            for kw in keywords:
                # Use word boundaries for keyword matching to avoid partial matches
                pattern = re.compile(r'\b' + re.escape(kw) + r'\b', re.IGNORECASE)
                if pattern.search(query_lower):
                    blocked_category = category
                    blocked_keyword = kw
                    break
            if blocked_category:
                break
                
        if blocked_category:
            # Topic is blocked, but check if there's a "saving grace"
            
            # A. Educational Framing
            for frame_pattern in self.educational_frames_regex:
                if frame_pattern.search(query_lower):
                    return False, None
            
            # B. Subject-Specific Extensions
            allowed_extensions = self.config.EDUCATIONAL_EXTENSIONS.get(self.subject, [])
            for ext in allowed_extensions:
                if ext in query_lower:
                    return False, None
            
            # C. Subject-Specific Additional Allowed
            if hasattr(self.config, "ADDITIONAL_ALLOWED"):
                for allowed in self.config.ADDITIONAL_ALLOWED:
                    if allowed.lower() in query_lower:
                        return False, None

            # D. Specific Always Allowed Patterns (only if high confidence)
            # We filter out generic "what is" from being a saving grace for blocked topics
            for pattern in self.always_allowed_regex:
                p_str = pattern.pattern
                # Generic patterns shouldn't unblock a specific topic like "Marvel" or "IPL"
                if p_str in [r"what is", r"what are"]:
                    continue
                if pattern.search(query_lower):
                    return False, None

            # If no saving grace, definitely block
            return True, self.get_redirect_message(blocked_category)

        # 2. If no blocked topic, check if it's generally allowed (Always Allowed Pattern)
        # This is mostly for catch-all safety if we had an "everything else is blocked" policy,
        # but here it's helpful for explicitly allowing certain formats.
        for pattern in self.always_allowed_regex:
            if pattern.search(query_lower):
                return False, None

        # 3. Default to ALLOW if nothing else matched
        return False, None

    def get_redirect_message(self, category: str) -> str:
        """
        Returns a formatted redirect message based on the blocked category.
        """
        # Map sub-categories to main redirect templates
        mapping = {
            "movies": "entertainment",
            "tv_shows": "entertainment",
            "cartoons_anime": "entertainment",
            "music_entertainment": "entertainment",
            "celebrities": "entertainment",
            "sports_entertainment": "sports",
            "video_games": "gaming",
            "social_media": "social",
            "relationships": "social",
            "fashion_beauty": "default",
            "casual_food": "default",
            "casual_travel": "default",
            "shopping": "default",
            "news_politics": "default"
        }
        
        template_key = mapping.get(category, "default")
        template = self.config.REDIRECT_TEMPLATES.get(template_key, self.config.REDIRECT_TEMPLATES["default"])
        
        # Try to find a concept to fill the {concept} placeholder
        # In a real app, this might come from the current video/chapter
        concept = "your current topic"
        if hasattr(self.config, "subject"): # Fallback
             concept = self.subject
             
        return template.format(concept=concept)
