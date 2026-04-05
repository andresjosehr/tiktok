#!/usr/bin/env python3
"""
Genera todos los clips de audio para Tug of War usando ElevenLabs API.
Usa el modelo eleven_v3 con audio tags para maxima expresividad.

Uso:
    python generate_audio.py TU_API_KEY
    python generate_audio.py TU_API_KEY --list-voices
    python generate_audio.py TU_API_KEY --force   (regenera todos)
"""

import os
import sys
import json
import time
import requests

# ─── CONFIG ───
BASE_URL = "https://api.elevenlabs.io/v1"
MODEL_ID = "eleven_v3"  # Most expressive, supports audio tags
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "audio")

# Voice IDs - run with --list-voices to see yours
VOICE_MALE = "TxGEqnHWrfWFTfGW9XjX"    # Josh - deep young male
VOICE_FEMALE = "21m00Tcm4TlvDq8ikWAM"  # Rachel - clear female

# ─── AUDIO CLIPS ───
# Audio tags: [laughs] [whispers] [shouts] [excited] [sarcastic] [crying]
#             [curious] [mischievously] [sighs] [gasps] [applause] [explosion]
CLIPS = [
    # ── ROUND START ──
    {
        "id": "round_start_1",
        "text": "[shouts] ¡¡PELEEN!!",
        "desc": "Fight call",
        "settings": {"stability": 0.25, "similarity_boost": 0.7, "style": 0.8}
    },
    {
        "id": "round_start_2",
        "text": "[shouts] ¡¡A LA GUERRA!!",
        "desc": "To war",
        "settings": {"stability": 0.25, "similarity_boost": 0.7, "style": 0.8}
    },

    # ── COMBOS (ultra short, just the power word) ──
    {
        "id": "combo_t1",
        "text": "[excited] ¡Combo!",
        "desc": "Tier 1",
        "settings": {"stability": 0.4, "similarity_boost": 0.6, "style": 0.5}
    },
    {
        "id": "combo_t2",
        "text": "[shouts] ¡¡Súper!!",
        "desc": "Tier 2",
        "settings": {"stability": 0.3, "similarity_boost": 0.7, "style": 0.7}
    },
    {
        "id": "combo_t3_a",
        "text": "[shouts] ¡¡¡MEGA!!!",
        "desc": "Tier 3",
        "settings": {"stability": 0.25, "similarity_boost": 0.8, "style": 0.8}
    },
    {
        "id": "combo_t3_b",
        "text": "[shouts] ¡¡¡BRUTAL!!!",
        "desc": "Tier 3 alt",
        "settings": {"stability": 0.25, "similarity_boost": 0.8, "style": 0.8}
    },
    {
        "id": "combo_t4_a",
        "text": "[shouts] ¡¡¡ULTRA!!!",
        "desc": "Tier 4",
        "settings": {"stability": 0.2, "similarity_boost": 0.8, "style": 0.9}
    },
    {
        "id": "combo_t4_b",
        "text": "[shouts] ¡¡¡DESTRUCCIÓN!!!",
        "desc": "Tier 4 alt",
        "settings": {"stability": 0.2, "similarity_boost": 0.8, "style": 0.9}
    },
    {
        "id": "combo_t5_a",
        "text": "[shouts] ¡¡¡GODLIKE!!!",
        "desc": "Tier 5",
        "settings": {"stability": 0.15, "similarity_boost": 0.9, "style": 1.0}
    },
    {
        "id": "combo_t5_b",
        "text": "[shouts] ¡¡¡LEGENDARIO!!!",
        "desc": "Tier 5 alt",
        "settings": {"stability": 0.15, "similarity_boost": 0.9, "style": 1.0}
    },

    # ── DANGER ZONE ──
    {
        "id": "danger_1",
        "text": "[curious] Ohhh... ¡Están en peligro!",
        "desc": "Danger warning",
        "settings": {"stability": 0.3, "similarity_boost": 0.7, "style": 0.7}
    },
    {
        "id": "danger_critical",
        "text": "[shouts] ¡¡A punto de perder!!",
        "desc": "Critical danger",
        "settings": {"stability": 0.2, "similarity_boost": 0.8, "style": 0.9}
    },

    # ── COMEBACK ──
    {
        "id": "comeback_1",
        "text": "[shouts] ¡¡¡COMEBACK!!!",
        "desc": "Comeback",
        "settings": {"stability": 0.2, "similarity_boost": 0.8, "style": 0.9}
    },
    {
        "id": "comeback_2",
        "text": "[shouts] ¡¡¡LA REMONTADA!!!",
        "desc": "Comeback alt",
        "settings": {"stability": 0.2, "similarity_boost": 0.8, "style": 0.9}
    },

    # ── ROUND WIN ──
    {
        "id": "round_win_1",
        "text": "[shouts] ¡¡SIIII!! ¡¡GANAMOS ESTA RONDA!!",
        "desc": "Round win celebration",
        "settings": {"stability": 0.2, "similarity_boost": 0.8, "style": 0.9}
    },
    {
        "id": "round_win_2",
        "text": "[shouts] ¡¡ESA ES LA NUESTRA!! ¡¡VAMOS!!",
        "desc": "Round win alt",
        "settings": {"stability": 0.2, "similarity_boost": 0.8, "style": 0.9}
    },

    # ── REGALO (big gift) ──
    {
        "id": "regalo_1",
        "text": "[shouts] ¡¡¡REGALAZO!!!",
        "desc": "Big gift",
        "settings": {"stability": 0.25, "similarity_boost": 0.8, "style": 0.8}
    },

    # ── TENSION ──
    {
        "id": "tension_30s",
        "text": "[excited] ¡¡Últimos treinta segundos!!",
        "desc": "30 seconds left",
        "settings": {"stability": 0.3, "similarity_boost": 0.7, "style": 0.8}
    },
    {
        "id": "tension_10s",
        "text": "[shouts] ¡¡DIEZ SEGUNDOS!!",
        "desc": "10 seconds left",
        "settings": {"stability": 0.2, "similarity_boost": 0.8, "style": 0.9}
    },

    # ── GLORY MOMENT ──
    {
        "id": "glory_1",
        "text": "[shouts] ¡¡¡GLORY!!! [applause] ¡¡¡CAMPEONES!!!",
        "desc": "Glory",
        "settings": {"stability": 0.15, "similarity_boost": 0.9, "style": 1.0}
    },
    {
        "id": "glory_2",
        "text": "[shouts] ¡¡¡VICTORIA ABSOLUTA!!! [applause]",
        "desc": "Glory alt",
        "settings": {"stability": 0.15, "similarity_boost": 0.9, "style": 1.0}
    },

    # ── EMPATE ──
    {
        "id": "empate",
        "text": "[shouts] ¡¡EMPATE!! ¡¡Tiempo extra!!",
        "desc": "Tie",
        "settings": {"stability": 0.25, "similarity_boost": 0.8, "style": 0.8}
    },

    # ── HYPE REACTIONS (short) ──
    {
        "id": "hype_1",
        "text": "[excited] ¡¡Ohhh!!",
        "desc": "Amazed",
        "settings": {"stability": 0.2, "similarity_boost": 0.8, "style": 0.9}
    },
    {
        "id": "hype_2",
        "text": "[shouts] ¡¡Vamos!!",
        "desc": "Cheering",
        "settings": {"stability": 0.2, "similarity_boost": 0.8, "style": 0.9}
    },
    {
        "id": "hype_3",
        "text": "[excited] ¡Está parejo!",
        "desc": "Close match",
        "settings": {"stability": 0.3, "similarity_boost": 0.7, "style": 0.7}
    },
    {
        "id": "hype_4",
        "text": "[excited] ¡¡Qué locura!!",
        "desc": "Chaos",
        "settings": {"stability": 0.2, "similarity_boost": 0.8, "style": 0.9}
    },
]


def list_voices(api_key):
    """List available voices"""
    headers = {"Accept": "application/json", "xi-api-key": api_key}
    resp = requests.get(f"{BASE_URL}/voices", headers=headers)
    if resp.status_code == 200:
        voices = resp.json().get("voices", [])
        print(f"\n{'='*70}")
        print(f"{'NAME':<30} {'VOICE ID':<25} {'LABELS'}")
        print(f"{'='*70}")
        for v in voices:
            labels = v.get("labels", {})
            label_str = ", ".join(f"{k}:{val}" for k, val in labels.items()) if labels else ""
            print(f"{v['name']:<30} {v['voice_id']:<25} {label_str}")
        print(f"\nTotal: {len(voices)} voices")
    else:
        print(f"Error {resp.status_code}: {resp.text}")


def list_models(api_key):
    """List available models"""
    headers = {"Accept": "application/json", "xi-api-key": api_key}
    resp = requests.get(f"{BASE_URL}/models", headers=headers)
    if resp.status_code == 200:
        models = resp.json()
        print(f"\n{'='*70}")
        print(f"{'NAME':<40} {'MODEL ID'}")
        print(f"{'='*70}")
        for m in models:
            print(f"{m['name']:<40} {m['model_id']}")
    else:
        print(f"Error {resp.status_code}: {resp.text}")


def generate_clip(api_key, clip, voice_id):
    """Generate a single audio clip"""
    url = f"{BASE_URL}/text-to-speech/{voice_id}"

    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": api_key
    }

    data = {
        "text": clip["text"],
        "model_id": MODEL_ID,
        "language_code": "es",
        "voice_settings": {
            **clip["settings"],
            "use_speaker_boost": True
        }
    }

    try:
        resp = requests.post(url, json=data, headers=headers)

        if resp.status_code == 200:
            filepath = os.path.join(OUTPUT_DIR, f"{clip['id']}.mp3")
            with open(filepath, "wb") as f:
                f.write(resp.content)
            size_kb = len(resp.content) / 1024
            print(f"  [OK] {clip['id']}.mp3 ({size_kb:.1f}KB) - {clip['desc']}")
            return True
        else:
            print(f"  [ERROR] {clip['id']}: {resp.status_code} - {resp.text[:300]}")
            return False

    except Exception as e:
        print(f"  [ERROR] {clip['id']}: {str(e)}")
        return False


def main():
    api_key = os.environ.get("ELEVENLABS_API_KEY") or (
        sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("--") else None
    )

    if not api_key:
        print("Uso: python generate_audio.py TU_API_KEY")
        print("  python generate_audio.py TU_API_KEY --list-voices")
        print("  python generate_audio.py TU_API_KEY --list-models")
        print("  python generate_audio.py TU_API_KEY --force")
        sys.exit(1)

    if "--list-voices" in sys.argv:
        list_voices(api_key)
        sys.exit(0)

    if "--list-models" in sys.argv:
        list_models(api_key)
        sys.exit(0)

    force = "--force" in sys.argv

    voices = {
        "male": VOICE_MALE,
        "female": VOICE_FEMALE,
    }

    total_clips = len(CLIPS) * len(voices)
    print(f"\nGenerando {total_clips} clips ({len(CLIPS)} x {len(voices)} voces)")
    print(f"Modelo: {MODEL_ID} (audio tags + language_code=es)")
    print(f"Output: {OUTPUT_DIR}/male/ y {OUTPUT_DIR}/female/\n")

    ok = 0
    fail = 0

    for gender, voice_id in voices.items():
        gender_dir = os.path.join(OUTPUT_DIR, gender)
        os.makedirs(gender_dir, exist_ok=True)
        print(f"── {gender.upper()} ({voice_id}) ──")

        for i, clip in enumerate(CLIPS):
            filepath = os.path.join(gender_dir, f"{clip['id']}.mp3")

            if os.path.exists(filepath) and not force:
                print(f"  [SKIP] {clip['id']}.mp3 ya existe")
                ok += 1
                continue

            # Override output path
            url = f"{BASE_URL}/text-to-speech/{voice_id}"
            headers = {
                "Accept": "audio/mpeg",
                "Content-Type": "application/json",
                "xi-api-key": api_key
            }
            data = {
                "text": clip["text"],
                "model_id": MODEL_ID,
                "language_code": "es",
                "voice_settings": {**clip["settings"], "use_speaker_boost": True}
            }
            try:
                resp = requests.post(url, json=data, headers=headers)
                if resp.status_code == 200:
                    with open(filepath, "wb") as f:
                        f.write(resp.content)
                    size_kb = len(resp.content) / 1024
                    print(f"  [OK] {clip['id']}.mp3 ({size_kb:.1f}KB) - {clip['desc']}")
                    ok += 1
                else:
                    print(f"  [ERROR] {clip['id']}: {resp.status_code} - {resp.text[:200]}")
                    fail += 1
            except Exception as e:
                print(f"  [ERROR] {clip['id']}: {str(e)}")
                fail += 1

            time.sleep(0.3)

        print()

    print(f"Resultado TTS: {ok} OK, {fail} errores")

    # ── SOUND EFFECTS (SFX) ──
    SFX_CLIPS = [
        {
            "id": "sfx_round_win_fanfare",
            "text": "Short triumphant brass fanfare, victory trumpets, heroic, 3 seconds, videogame style",
            "duration": 3,
            "prompt_influence": 0.5,
            "loop": False,
            "desc": "Victory trumpets for round win"
        },
        {
            "id": "sfx_glory_anthem",
            "text": "Epic orchestral victory anthem with brass fanfare, drums, and choir, triumphant and glorious, videogame final boss defeated",
            "duration": 8,
            "prompt_influence": 0.5,
            "loop": False,
            "desc": "Glory moment victory anthem"
        },
        {
            "id": "sfx_battle_loop",
            "text": "Playful competitive background music, 120bpm, bouncy plucked melody with light claps, subtle tension but mostly fun and groovy, like a casual mobile game or party game, clean bright mix, not too intense",
            "duration": 30,
            "prompt_influence": 0.6,
            "loop": True,
            "desc": "Background battle music - casual fun v2"
        },
        {
            "id": "sfx_drum_roll",
            "text": "Military snare drum roll, steady and clean, building intensity, crisp high frequency snare hits getting faster and louder",
            "duration": 5,
            "prompt_influence": 0.7,
            "loop": True,
            "desc": "Drum roll tension loop"
        },
        {
            "id": "sfx_countdown_tick",
            "text": "Deep dramatic clock tick tock, suspenseful, slow heartbeat rhythm",
            "duration": 3,
            "prompt_influence": 0.5,
            "loop": True,
            "desc": "Tension clock ticking loop"
        },
        {
            "id": "sfx_comeback_hit",
            "text": "Dramatic orchestral hit with reverse cymbal crash, powerful impact, cinematic",
            "duration": 2,
            "prompt_influence": 0.5,
            "loop": False,
            "desc": "Comeback dramatic impact"
        },
    ]

    sfx_dir = os.path.join(OUTPUT_DIR, "sfx")
    os.makedirs(sfx_dir, exist_ok=True)
    print(f"\n── SFX ({len(SFX_CLIPS)} clips) ──")

    sfx_ok = 0
    sfx_fail = 0
    for sfx in SFX_CLIPS:
        filepath = os.path.join(sfx_dir, f"{sfx['id']}.mp3")
        if os.path.exists(filepath) and not force:
            print(f"  [SKIP] {sfx['id']}.mp3 ya existe")
            sfx_ok += 1
            continue

        url = f"{BASE_URL}/sound-generation"
        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": api_key
        }
        data = {
            "text": sfx["text"],
            "model_id": "eleven_text_to_sound_v2",
            "duration_seconds": sfx["duration"],
            "prompt_influence": sfx["prompt_influence"],
            "loop": sfx["loop"]
        }
        try:
            resp = requests.post(url, json=data, headers=headers)
            if resp.status_code == 200:
                with open(filepath, "wb") as f:
                    f.write(resp.content)
                size_kb = len(resp.content) / 1024
                print(f"  [OK] {sfx['id']}.mp3 ({size_kb:.1f}KB) - {sfx['desc']}")
                sfx_ok += 1
            else:
                print(f"  [ERROR] {sfx['id']}: {resp.status_code} - {resp.text[:200]}")
                sfx_fail += 1
        except Exception as e:
            print(f"  [ERROR] {sfx['id']}: {str(e)}")
            sfx_fail += 1

        time.sleep(0.5)

    print(f"Resultado SFX: {sfx_ok} OK, {sfx_fail} errores")

    # Generate manifest
    manifest = {"male": {}, "female": {}, "sfx": {}}
    for gender in voices:
        for clip in CLIPS:
            filepath = os.path.join(OUTPUT_DIR, gender, f"{clip['id']}.mp3")
            if os.path.exists(filepath):
                manifest[gender][clip["id"]] = f"audio/{gender}/{clip['id']}.mp3"
    for sfx in SFX_CLIPS:
        filepath = os.path.join(sfx_dir, f"{sfx['id']}.mp3")
        if os.path.exists(filepath):
            manifest["sfx"][sfx["id"]] = f"audio/sfx/{sfx['id']}.mp3"

    manifest_path = os.path.join(OUTPUT_DIR, "manifest.json")
    with open(manifest_path, "w") as f:
        json.dump(manifest, f, indent=2)
    print(f"Manifest: {manifest_path}")


if __name__ == "__main__":
    main()
