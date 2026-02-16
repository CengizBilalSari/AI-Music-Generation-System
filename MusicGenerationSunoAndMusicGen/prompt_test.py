import sys
import os
import json
import time
import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "SunoAPI"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "MusicGenLocal"))

# Prompt Pool 

PROMPTS = [
    {
        "name": "2000s Pop - Narrative",
        "description": "Descriptive/Narrative: Focuses on the vibe, era, and feeling of early 2000s pop.",
        "suno": {
            "prompt": (
                "[Intro: Sparkly synth and clean electric guitar strumming]\n"
                "[Verse 1]\n"
                "Glitter in the air, phone is ringing off the hook\n"
                "Got that Y2K style, didn't even have to look\n"
                "Low-rise jeans and a butterfly clip in my hair\n"
                "Walking down the block like I'm a billionaire\n"
                "\n[Pre-Chorus]\n"
                "The beat is kicking in, I'm feeling so alive\n"
                "It's a Friday night, yeah we're ready to drive\n"
                "\n[Chorus]\n"
                "Bubblegum dreams and a neon sky\n"
                "We're never gonna let this feeling die\n"
                "Early 2000s rhythm in my soul\n"
                "Taking back the night, losing all control\n"
                "\n[Bridge: Funky bass line and drum break]\n"
                "\n[Chorus]\n"
                "Bubblegum dreams and a neon sky\n"
                "We're never gonna let this feeling die\n"
                "Early 2000s rhythm in my soul\n"
                "Taking back the night, losing all control\n"
                "\n[Outro: Fading guitar riff and giggle]"
            ),
            "style": "Pop, Early 2000s, Teen Pop, Female Vocals, Upbeat, Radio-Friendly, Bright",
            "title": "Bubblegum Dreams",
            "custom_mode": True,
            "instrumental": False,
            "model": "V4_5ALL",
            "vocal_gender": "f",
            "negative_tags": "Dark, Slow, Electronic, Metal, Rap, Male Vocals",
        },
        "musicgen": {
            "prompt": (
                "A bright, upbeat early 2000s teen pop song. Female lead vocals, high-energy, "
                "sparkly synths, clean electric guitar riffs, and punchy acoustic drums. "
                "Catchy melody, radio-friendly production. 120 BPM."
            ),
            "duration_s": 30,
        },
    },
    {
        "name": "2000s Pop - Structural",
        "description": "Structural/Formal: Emphasizing technical structure and specific instrument roles.",
        "suno": {
            "prompt": (
                "[Intro: Driving palm-muted electric guitar]\n"
                "[Verse 1]\n"
                "Check the mirror once, check the mirror twice\n"
                "Everything is perfect, everything is nice\n"
                "Britney on the stereo, volume way up high\n"
                "Catching every glance from every single guy\n"
                "\n[Chorus]\n"
                "It's a radio-friendly masterpiece\n"
                "Where the upbeat energy will never cease\n"
                "Guitar riffs driving all through the night\n"
                "Female vocals shining ever so bright\n"
                "\n[Verse 2]\n"
                "Lip gloss shining, walking through the mall\n"
                "Waiting for the weekend, waiting for the call\n"
                "\n[Chorus]\n"
                "It's a radio-friendly masterpiece\n"
                "Where the upbeat energy will never cease\n"
                "Guitar riffs driving all through the night\n"
                "Female vocals shining ever so bright\n"
            ),
            "style": "Pop, Early 2000s, Radio-friendly, Guitar-driven, Female Vocals, Verse-Chorus Structure",
            "title": "Masterpiece",
            "custom_mode": True,
            "instrumental": False,
            "model": "V4_5ALL",
            "vocal_gender": "f",
            "negative_tags": "Acoustic, Slow, Lo-fi, Orchestral",
        },
        "musicgen": {
            "prompt": (
                "Catchy pop song, early 2000s, female vocals, guitar-driven. "
                "Structure: Verse-Chorus-Verse-Chorus. "
                "Instrumentation: Electric guitar, bass, drums, synth pads. "
                "Vibe: Radio-friendly, high energy, upbeat."
            ),
            "duration_s": 30,
        },
    },
    {
        "name": "2000s Pop - Tag-based",
        "description": "Keyword/Tag-based: Focuses on descriptive keywords and genre tags for best model steering.",
        "suno": {
            "prompt": (
                "Catchy pop, early 2000s, female vocals, guitar-driven, radio-friendly, upbeat energy, verse-chorus structure"
            ),
            "style": "Pop, Early 2000s, Guitar-driven, Female Vocals, Upbeat, Radio-Friendly",
            "title": "Radio Hits",
            "custom_mode": True,
            "instrumental": False,
            "model": "V4_5ALL",
            "vocal_gender": "f",
            "negative_tags": "Metal, Dark, Ambient",
        },
        "musicgen": {
            "prompt": (
                "Pop, 2000s, female lead, electric guitar, radio-friendly, 4/4 time, 128 BPM, upbeat, happy."
            ),
            "duration_s": 30,
        },
    },
]

RESULTS_FILE = "prompt_comparison.json"




def run_suno(prompt_config: dict, prompt_name: str) -> dict:
    try:
        import suno_utils
        from suno_generate import generate_music, wait_for_completion

        if not suno_utils.API_KEY:
            return {"api": "Suno", "prompt_name": prompt_name, "error": "API key not set", "tracks": []}

        cfg = prompt_config["suno"]
        start_time = time.time()

        kwargs = {
            "prompt": cfg["prompt"],
            "custom_mode": cfg.get("custom_mode", False),
            "instrumental": cfg.get("instrumental", False),
            "style": cfg.get("style"),
            "title": cfg.get("title"),
            "model": cfg.get("model", "V4_5ALL"),
        }
        if cfg.get("vocal_gender"):
            kwargs["vocal_gender"] = cfg["vocal_gender"]
        if cfg.get("negative_tags"):
            kwargs["negative_tags"] = cfg["negative_tags"]

        result = generate_music(**kwargs)
        task_id = result["data"]["taskId"]
        task_data = wait_for_completion(task_id)

        total_time = round(time.time() - start_time, 3)

        tracks = []
        suno_data = task_data.get("response", {}).get("sunoData", [])
        for track in suno_data:
            tracks.append({
                "title": track.get("title"),
                "tags": track.get("tags"),
                "duration_s": track.get("duration"),
                "model_name": track.get("modelName"),
                "audio_url": track.get("audioUrl"),
                "stream_url": track.get("streamAudioUrl"),
                "image_url": track.get("imageUrl"),
            })

        return {
            "api": "Suno",
            "prompt_name": prompt_name,
            "model": cfg.get("model", "V4_5ALL"),
            "prompt_chars": len(cfg["prompt"]),
            "total_time_s": total_time,
            "tracks_generated": len(tracks),
            "error": None,
            "tracks": tracks,
        }
    except Exception as e:
        return {"api": "Suno", "prompt_name": prompt_name, "error": str(e), "tracks": []}


def run_musicgen(prompt_config: dict, prompt_name: str) -> dict:
    try:
        from musicgen_generate import generate_music

        cfg = prompt_config["musicgen"]
        result = generate_music(
            prompt=cfg["prompt"],
            duration_s=cfg.get("duration_s", 30),
        )

        has_output = result.get("output_file") is not None
        return {
            "api": "MusicGen (Local)",
            "prompt_name": prompt_name,
            "model": result.get("model", "facebook/musicgen-small"),
            "device": result.get("device", "cpu"),
            "prompt_chars": len(cfg["prompt"]),
            "total_time_s": result.get("generation_time_s"),
            "tracks_generated": 1 if has_output else 0,
            "error": None,
            "tracks": [{
                "output_file": result.get("output_file"),
                "file_size_kb": round(result.get("file_size_bytes", 0) / 1024, 1),
                "duration_actual_s": result.get("duration_actual_s"),
                "duration_requested_s": cfg.get("duration_s", 30),
            }] if has_output else [],
        }
    except Exception as e:
        return {"api": "MusicGen (Local)", "prompt_name": prompt_name, "error": str(e), "tracks": []}





if __name__ == "__main__":
    print("=" * 60)
    print("  Q2: Prompt Engineering - Suno vs MusicGen")
    print(f"  {len(PROMPTS)} prompts × 2 APIs = {len(PROMPTS) * 2} total generations")
    print("=" * 60)

    all_results = []

    for i, prompt_config in enumerate(PROMPTS, 1):
        name = prompt_config["name"]
        desc = prompt_config["description"]

        print(f"\n{'─' * 60}")
        print(f"  PROMPT {i}/{len(PROMPTS)}: {name}")
        print(f"  {desc}")
        print(f"{'─' * 60}")

        # Run on Suno
        print(f"\n  [Suno] Testing '{name}'...")
        suno_result = run_suno(prompt_config, name)
        status = "OK" if not suno_result.get("error") else f"FAILED: {suno_result['error'][:60]}"
        print(f"  [Suno] {status} | tracks={suno_result.get('tracks_generated', 0)} | time={suno_result.get('total_time_s', 'N/A')}s")
        all_results.append(suno_result)

        # Run on MusicGen (Local)
        print(f"\n  [MusicGen] Testing '{name}'...")
        mg_result = run_musicgen(prompt_config, name)
        status = "OK" if not mg_result.get("error") else f"FAILED: {mg_result['error'][:60]}"
        print(f"  [MusicGen] {status} | tracks={mg_result.get('tracks_generated', 0)} | time={mg_result.get('total_time_s', 'N/A')}s")
        all_results.append(mg_result)

    output = {
        "question": "Q2: Prompt Engineering",
        "timestamp": datetime.datetime.now().isoformat(),
        "total_prompts": len(PROMPTS),
        "prompts": [{"name": p["name"], "description": p["description"]} for p in PROMPTS],
        "results": all_results,
    }

    with open(RESULTS_FILE, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    # Summary table
    print(f"\n{'=' * 60}")
    print("  SUMMARY")
    print(f"{'=' * 60}")
    print(f"  {'Prompt':<25s} {'API':<12s} {'Status':<10s} {'Tracks':<8s} {'Time':>8s}")
    print(f"  {'─' * 25} {'─' * 12} {'─' * 10} {'─' * 8} {'─' * 8}")
    for r in all_results:
        status = "OK" if not r.get("error") else "FAILED"
        t = f"{r.get('total_time_s', 0)}s" if r.get("total_time_s") else "N/A"
        print(f"  {r['prompt_name']:<25s} {r['api']:<12s} {status:<10s} {r.get('tracks_generated', 0):<8d} {t:>8s}")

    print(f"\n  Results saved to: {RESULTS_FILE}")
    print(f"{'=' * 60}\n")

