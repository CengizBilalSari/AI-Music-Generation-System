"""
MusicGen Local - Configuration & Utilities
============================================
Configuration for Meta's MusicGen model running locally
via HuggingFace transformers. No API key needed.

Models available (from HuggingFace):
  - facebook/musicgen-small   (~300M params, ~1.5 GB, fastest)
  - facebook/musicgen-medium  (~1.5B params, ~3.3 GB)
  - facebook/musicgen-large   (~3.3B params, ~6.7 GB, best quality)
"""

import os
import torch

# Model selection (change to "medium" or "large" for better quality)
MODEL_SIZE = "small"
MODEL_NAME = f"facebook/musicgen-{MODEL_SIZE}"

# Generation defaults
DEFAULT_DURATION_S = 30          # seconds (small model handles 30s well)
MAX_DURATION_S = 120             # max recommended for small model
SAMPLE_RATE = 32000              # MusicGen outputs at 32kHz
MAX_PROMPT_LENGTH = 1500         # practical limit for good results

# Output
OUTPUT_DIR = "generated_music"
OUTPUT_FORMAT = "wav"            # MusicGen outputs raw audio -> WAV

# Device selection
def get_device() -> str:
    """Auto-detect best available device."""
    if torch.cuda.is_available():
        return "cuda"
    else:
        return "cpu"

DEVICE = get_device()


# Validation

def validate_params(prompt: str, duration_s: int):
    """Validate generation parameters."""
    if not prompt or not prompt.strip():
        raise ValueError("prompt is required and cannot be empty.")

    if len(prompt) > MAX_PROMPT_LENGTH:
        raise ValueError(
            f"prompt exceeds {MAX_PROMPT_LENGTH} characters "
            f"(got {len(prompt)})."
        )

    if duration_s < 1 or duration_s > MAX_DURATION_S:
        raise ValueError(
            f"duration_s must be between 1 and {MAX_DURATION_S} "
            f"(got {duration_s})."
        )
