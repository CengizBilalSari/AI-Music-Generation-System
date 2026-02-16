import time
import requests

from utils import (
    API_KEY,
    ENDPOINTS,
    DEFAULT_MODEL,
    STATUS_SUCCESS,
    FAILURE_STATUSES,
    DEFAULT_POLL_INTERVAL,
    DEFAULT_MAX_WAIT,
    REQUEST_TIMEOUT,
    get_headers,
    validate_params,
    build_payload,
)


# API Functions
def generate_music(
    prompt: str,
    custom_mode: bool = False,
    instrumental: bool = False,
    style: str | None = None,
    title: str | None = None,
    model: str = DEFAULT_MODEL,
    api_key: str | None = None,
    **optional,
) -> dict:
    validate_params(prompt, custom_mode, instrumental, style, title, model)

    payload = build_payload(
        prompt=prompt,
        custom_mode=custom_mode,
        instrumental=instrumental,
        model=model,
        style=style,
        title=title,
        **optional,
    )

    print(f"[Suno] Submitting generation request (model={model}) ...")
    response = requests.post(
        ENDPOINTS["generate"],
        headers=get_headers(api_key),
        json=payload,
        timeout=REQUEST_TIMEOUT,
    )
    response.raise_for_status()
    result = response.json()

    if result.get("code") != 200:
        raise RuntimeError(
            f"Suno API error {result.get('code')}: {result.get('msg')}"
        )

    task_id = result["data"]["taskId"]
    print(f"[Suno] Task submitted successfully! taskId = {task_id}")
    return result


def get_task_status(task_id: str, api_key: str | None = None) -> dict:
    response = requests.get(
        ENDPOINTS["record_info"],
        headers=get_headers(api_key),
        params={"taskId": task_id},
        timeout=REQUEST_TIMEOUT,
    )
    response.raise_for_status()
    return response.json()


def wait_for_completion(
    task_id: str,
    api_key: str | None = None,
    poll_interval: int = DEFAULT_POLL_INTERVAL,
    max_wait: int = DEFAULT_MAX_WAIT,
) -> dict:
    """
    Poll the Suno API until the task completes or fails.
    """
    elapsed = 0
    status = "PENDING"
    print(f"[Suno] Waiting for task {task_id} to complete ...")

    while elapsed < max_wait:
        result = get_task_status(task_id, api_key)
        data = result.get("data", {})
        status = data.get("status", "UNKNOWN")

        print(f"[Suno]  Status: {status}  ({elapsed}s elapsed)")

        if status == STATUS_SUCCESS:
            print("[Suno] Generation complete!")
            return data

        if status in FAILURE_STATUSES:
            error_msg = data.get("errorMessage") or status
            raise RuntimeError(f"[Suno] Generation failed: {error_msg}")

        time.sleep(poll_interval)
        elapsed += poll_interval

    raise RuntimeError(
        f"[Suno]   Timed out after {max_wait}s. "
        f"Task {task_id} is still in status: {status}"
    )


def print_results(task_data: dict) -> None:
    """Pretty-print the generated track details."""
    response = task_data.get("response", {})
    tracks = response.get("sunoData", [])

    if not tracks:
        print("[Suno] No tracks found in response.")
        return

    print(f"\n{'='*60}")
    print(f"    Generated {len(tracks)} track(s)")
    print(f"{'='*60}\n")

    for i, track in enumerate(tracks, 1):
        print(f"  Track {i}: {track.get('title', 'Untitled')}")
        print(f"  ├── Style/Tags : {track.get('tags', 'N/A')}")
        print(f"  ├── Duration   : {track.get('duration', 'N/A')}s")
        print(f"  ├── Model      : {track.get('modelName', 'N/A')}")
        print(f"  ├── Created    : {track.get('createTime', 'N/A')}")
        print(f"  ├── Audio URL  : {track.get('audioUrl', 'N/A')}")
        print(f"  ├── Stream URL : {track.get('streamAudioUrl', 'N/A')}")
        print(f"  └── Image URL  : {track.get('imageUrl', 'N/A')}")
        print()


if __name__ == "__main__":
    if not API_KEY:
        print("Error: SUNO_API_KEY not found.")
        print("Create a .env file in the project root with:")
        print("  SUNO_API_KEY=your_key_here")
        exit(1)

    # non custom mode
    result = generate_music(
        prompt="A short relaxing piano tune with gentle melodies",
    )
    task_data = wait_for_completion(result["data"]["taskId"])
    print_results(task_data)

    # Custom mode – instrumental
    result = generate_music(
        prompt="A calm and relaxing piano track with soft melodies",
        custom_mode=True,
        instrumental=True,
        style="Classical",
        title="Peaceful Piano Meditation",
        negative_tags="Heavy Metal, Upbeat Drums",
        vocal_gender="m",
        style_weight=0.65,
    )
    task_data = wait_for_completion(result["data"]["taskId"])
    print_results(task_data)

    # Custom mode – with lyrics
    result = generate_music(
        prompt="[Verse]\nSunrise over the hills\n[Chorus]\nA brand new day begins",
        custom_mode=True,
        instrumental=False,
        style="Pop, Acoustic",
        title="Brand New Day",
        model="V5",
    )
    task_data = wait_for_completion(result["data"]["taskId"])
    print_results(task_data)
