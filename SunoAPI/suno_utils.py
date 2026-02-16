"""
Suno API - Configuration & Utilities
=====================================
Centralized configuration, constants, and helper functions.
"""

import os
from dotenv import load_dotenv

load_dotenv()

# API Configuration 

BASE_URL = "https://api.sunoapi.org/api/v1"

ENDPOINTS = {
    "generate": f"{BASE_URL}/generate",
    "record_info": f"{BASE_URL}/generate/record-info",
}


API_KEY = os.environ.get("SUNO_API_KEY", "")

# Model Versions 
# V5         : Superior musical expression, faster generation
# V4_5PLUS   : Richer sound, new ways to create, max 8 min
# V4_5ALL    : Better song structure, max 8 min
# V4_5       : Superior genre blending, smarter prompts, up to 8 min
# V4         : Best audio quality, refined song structure, up to 4 min

MODELS = ["V5", "V4_5PLUS", "V4_5ALL", "V4_5", "V4"]
DEFAULT_MODEL = "V4_5ALL"

#  Task Status Constants 

STATUS_PENDING = "PENDING"
STATUS_TEXT_SUCCESS = "TEXT_SUCCESS"
STATUS_FIRST_SUCCESS = "FIRST_SUCCESS"
STATUS_SUCCESS = "SUCCESS"

FAILURE_STATUSES = [
    "CREATE_TASK_FAILED",
    "GENERATE_AUDIO_FAILED",
    "CALLBACK_EXCEPTION",
    "SENSITIVE_WORD_ERROR",
]

#  Polling & Timeout Defaults 

DEFAULT_POLL_INTERVAL = 30   # seconds between each status poll
DEFAULT_MAX_WAIT = 300       # maximum seconds to wait for completion
REQUEST_TIMEOUT = 30         # seconds for HTTP request timeout

# Default callback URL (required by the API, but unused when polling)
DEFAULT_CALLBACK_URL = "https://example.com/callback"

#  Character Limits (per model) 

PROMPT_LIMITS = {"V4": 3000, "V4_5": 5000, "V4_5PLUS": 5000, "V4_5ALL": 5000, "V5": 5000}
STYLE_LIMITS  = {"V4": 200,  "V4_5": 1000, "V4_5PLUS": 1000, "V4_5ALL": 1000, "V5": 1000}
TITLE_LIMITS  = {"V4": 80,   "V4_5": 100,  "V4_5PLUS": 100,  "V4_5ALL": 80,   "V5": 100}

NON_CUSTOM_PROMPT_LIMIT = 500

# ─── Payload field mapping ───────────────────────────────────────────────────
# Maps Python kwarg names → Suno API JSON field names.
# Used by build_payload() to construct the request body declaratively.

OPTIONAL_FIELDS = {
    "persona_id":          "personaId",
    "persona_model":       "personaModel",
    "negative_tags":       "negativeTags",
    "vocal_gender":        "vocalGender",
    "style_weight":        "styleWeight",
    "weirdness_constraint": "weirdnessConstraint",
    "audio_weight":        "audioWeight",
}


#  Helper Functions 


def get_headers(api_key: str | None = None) -> dict:
    """Build request headers with Bearer token authentication."""
    key = api_key or API_KEY
    if not key:
        raise ValueError(
            "No API key provided. Set SUNO_API_KEY in your .env file "
            "or pass api_key explicitly."
        )
    return {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
    }


def validate_params(
    prompt: str,
    custom_mode: bool,
    instrumental: bool,
    style: str | None,
    title: str | None,
    model: str,
) -> None:
    """
    Validate required fields and character limits based on mode & model.

    Raises ValueError with a clear message on any violation.
    """
    if model not in MODELS:
        raise ValueError(f"Invalid model '{model}'. Choose from: {MODELS}")

    if custom_mode:
        _require(style, "style", "customMode is True")
        _require(title, "title", "customMode is True")
        if not instrumental:
            _require(prompt, "prompt", "customMode is True and instrumental is False")
        # Per-model character limits
        if prompt:
            _check_limit(prompt, PROMPT_LIMITS[model], "prompt", model)
        if style:
            _check_limit(style, STYLE_LIMITS[model], "style", model)
        if title:
            _check_limit(title, TITLE_LIMITS[model], "title", model)
    else:
        _require(prompt, "prompt", "non-custom mode")
        _check_limit(prompt, NON_CUSTOM_PROMPT_LIMIT, "prompt", "non-custom mode")


def build_payload(
    prompt: str,
    custom_mode: bool,
    instrumental: bool,
    model: str,
    style: str | None = None,
    title: str | None = None,
    callback_url: str | None = None,
    **optional,
) -> dict:
    """
    Build the JSON payload for the /generate endpoint.

    Core fields are always included. Custom-mode fields (style, title)
    are added when applicable. Optional fields are added dynamically
    from the OPTIONAL_FIELDS mapping — no value means it's skipped.
    """
    payload = {
        "customMode": custom_mode,
        "instrumental": instrumental,
        "model": model,
        "prompt": prompt,
        "callBackUrl": callback_url or DEFAULT_CALLBACK_URL,
    }

    if custom_mode:
        payload["style"] = style
        payload["title"] = title

    # Add any optional fields that were provided (not None)
    for kwarg_name, api_name in OPTIONAL_FIELDS.items():
        value = optional.get(kwarg_name)
        if value is not None:
            payload[api_name] = value

    return payload

def _require(value, field_name: str, context: str) -> None:
    """Raise ValueError if a required value is missing."""
    if not value:
        raise ValueError(f"'{field_name}' is required when {context}.")


def _check_limit(value: str, limit: int, field_name: str, context: str) -> None:
    """Raise ValueError if a string exceeds its character limit."""
    if len(value) > limit:
        raise ValueError(
            f"'{field_name}' too long for {context} "
            f"({len(value)} chars, max {limit})."
        )
