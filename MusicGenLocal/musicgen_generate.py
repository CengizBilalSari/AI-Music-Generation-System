import os
import time
import json
import datetime
import scipy.io.wavfile

from musicgen_utils import (
    MODEL_NAME,
    MODEL_SIZE,
    DEFAULT_DURATION_S,
    SAMPLE_RATE,
    OUTPUT_DIR,
    OUTPUT_FORMAT,
    DEVICE,
    validate_params,
)

_model = None
_processor = None


def _load_model():
    """Load the MusicGen model (downloads on first run)."""
    global _model, _processor

    if _model is not None:
        return _model, _processor

    from transformers import AutoProcessor, MusicgenForConditionalGeneration

    print(f"[MusicGen] Loading model: {MODEL_NAME} (device={DEVICE})...")
    load_start = time.time()

    _processor = AutoProcessor.from_pretrained(MODEL_NAME)
    _model = MusicgenForConditionalGeneration.from_pretrained(MODEL_NAME)
    _model = _model.to(DEVICE)

    load_time = round(time.time() - load_start, 2)
    print(f"[MusicGen] Model loaded in {load_time}s")

    return _model, _processor


def generate_music(
    prompt: str,
    duration_s: int = DEFAULT_DURATION_S,
    output_filename: str | None = None,
) -> dict:

    validate_params(prompt, duration_s)

    model, processor = _load_model()

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    if not output_filename:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_prompt = prompt[:40].replace(" ", "_").replace("/", "_").replace("\\", "_")
        safe_prompt = "".join(c for c in safe_prompt if c.isalnum() or c == "_")
        output_filename = f"{timestamp}_{safe_prompt}.{OUTPUT_FORMAT}"

    output_path = os.path.join(OUTPUT_DIR, output_filename)

    print(f"[MusicGen] Generating music (model={MODEL_SIZE}, "
          f"duration={duration_s}s, device={DEVICE}) ...")
    print(f"[MusicGen] Prompt: \"{prompt[:80]}{'...' if len(prompt) > 80 else ''}\"")

    start_time = time.time()

    # Tokenize prompt
    inputs = processor(
        text=[prompt],
        padding=True,
        return_tensors="pt",
    ).to(DEVICE)

    # Calculate max new tokens based on desired duration
    # MusicGen generates ~50 tokens per second of audio
    max_new_tokens = int(duration_s * 50)

    # Generate
    audio_values = model.generate(
        **inputs,
        max_new_tokens=max_new_tokens,
        do_sample=True,
    )

    generation_time = round(time.time() - start_time, 3)

    # Save to WAV
    audio_data = audio_values[0, 0].cpu().numpy()
    scipy.io.wavfile.write(output_path, rate=SAMPLE_RATE, data=audio_data)

    file_size = os.path.getsize(output_path)
    actual_duration = round(len(audio_data) / SAMPLE_RATE, 2)

    print(f"[MusicGen] Generation complete! ({generation_time}s)")
    print(f"[MusicGen] Saved to: {output_path} ({file_size / 1024:.1f} KB)")
    print(f"[MusicGen] Actual duration: {actual_duration}s")

    result = {
        "prompt": prompt,
        "model": MODEL_NAME,
        "model_size": MODEL_SIZE,
        "device": DEVICE,
        "duration_requested_s": duration_s,
        "duration_actual_s": actual_duration,
        "output_file": output_path,
        "file_size_bytes": file_size,
        "generation_time_s": generation_time,
        "created_at": datetime.datetime.now().isoformat(),
    }

    return result


def print_results(result: dict):
    """Pretty-print a generation result."""
    print()
    print("=" * 60)
    print("  Generated Track (Local)")
    print("=" * 60)
    print(f"  ├── Prompt       : {result['prompt'][:70]}{'...' if len(result['prompt']) > 70 else ''}")
    print(f"  ├── Model        : {result['model']} ({result['model_size']})")
    print(f"  ├── Device       : {result['device']}")
    print(f"  ├── Duration     : {result['duration_actual_s']}s (requested {result['duration_requested_s']}s)")
    print(f"  ├── File         : {result['output_file']}")
    print(f"  ├── File Size    : {result['file_size_bytes'] / 1024:.1f} KB")
    print(f"  ├── Gen Time     : {result['generation_time_s']}s")
    print(f"  └── Created      : {result['created_at']}")
    print()


def save_results(results: list, filepath: str = "results.json"):
    """Save all results to a JSON file."""
    output = {
        "api": "MusicGen (Local)",
        "model": MODEL_NAME,
        "device": DEVICE,
        "total_generations": len(results),
        "results": results,
    }
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    print(f"[MusicGen] Results saved to: {filepath}")


if __name__ == "__main__":
    print("=" * 60)
    print("  MusicGen Local - Music Generation")
    print(f"  Model: {MODEL_NAME} | Device: {DEVICE}")
    print("=" * 60)

    all_results = []

    # Simple prompt (30s)
    print("\n" + "─" * 60)
    print("  EXAMPLE 1: Lo-fi study beat (30s)")
    print("─" * 60)
    result = generate_music(
        prompt="A relaxing lo-fi beat for studying late at night with soft piano and vinyl crackle",
        duration_s=30,
    )
    print_results(result)
    all_results.append(result)

    #Orchestral (30s)
    print("\n" + "─" * 60)
    print("  EXAMPLE 2: Cinematic orchestral (30s)")
    print("─" * 60)
    result = generate_music(
        prompt="An epic cinematic orchestral piece with rising strings, powerful brass, and dramatic timpani",
        duration_s=30,
    )
    print_results(result)
    all_results.append(result)

    # Pop (20s)
    print("\n" + "─" * 60)
    print("Upbeat pop (20s)")
    print("─" * 60)
    result = generate_music(
        prompt="A catchy upbeat pop song with bright guitars, punchy drums, and a fun singalong melody",
        duration_s=20,
    )
    print_results(result)
    all_results.append(result)

    #Acoustic guitar (30s)
    print("\n" + "─" * 60)
    print("  EXAMPLE 4: Acoustic folk (30s)")
    print("─" * 60)
    result = generate_music(
        prompt="An intimate acoustic folk piece with fingerpicked guitar, warm and emotional, slow tempo",
        duration_s=30,
    )
    print_results(result)
    all_results.append(result)

    save_results(all_results)
