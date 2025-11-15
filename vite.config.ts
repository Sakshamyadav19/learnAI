import { defineConfig } from "vite";
import react from "@vitejs/plugin-react-swc";
import path from "path";
import { componentTagger } from "lovable-tagger";

// https://vitejs.dev/config/
export default defineConfig(({ mode }) => ({
  server: {
    host: "::",
    port: 8080,
    // Proxy removed - now using FastAPI backend directly
  },
  plugins: [
    react(),
    mode === 'development' &&
    componentTagger(),
  ].filter(Boolean),
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
}));



/*
import json
import requests
import re

# Airia requirement → output must be set
output = input


# ----------------------------------------------------
# 1️⃣ DIRECTLY PARSE JSON (Airia passes valid JSON)
# ----------------------------------------------------
try:
    data = json.loads(input)
except Exception as e:
    output = json.dumps({"error": f"Invalid JSON input: {str(e)}"})
    raise SystemExit

topic = data.get("topic", "Untitled")
segments = data.get("segments", [])

if not segments:
    output = json.dumps({"error": "No segments found"})
    raise SystemExit

# ----------------------------------------------------
# 2️⃣ ElevenLabs Setup
# ----------------------------------------------------
api_key = "sk_756dcbfb5cf18bdeb468e1ac0b6d706202e864a7291c0568"
voice_id = "JBFqnCBsd6RMkjVDRZzb"

results = []

# ----------------------------------------------------
# 3️⃣ Process each segment
# ----------------------------------------------------
for seg in segments:
    seg_id = seg.get("segment_id") or seg.get("id")
    text = seg.get("narration")  # using prompt as narration
    image_url = seg.get("image_url")

    if not text:
        results.append({
            "segment_id": seg_id,
            "error": "Missing text"
        })
        continue

    clean_text = text.strip().replace("\n", " ")

    # ------------------------------------------------
    # 4️⃣ CALL /text-to-dialogue/stream/with-timestamps
    # ------------------------------------------------
    try:
        resp = requests.post(
            "https://api.elevenlabs.io/v1/text-to-dialogue/stream/with-timestamps",
            headers={
                "xi-api-key": api_key,
                "Content-Type": "application/json"
            },
            json={
                "inputs": [
                    {
                        "text": clean_text,
                        "voice_id": voice_id
                    }
                ]
            },
            timeout=60,
            stream=True
        )

        audio_chunks = []
        alignment_chunks = []

        # ------------------------------------------------
        # 5️⃣ READ STREAMED JSON CHUNKS
        # ------------------------------------------------
        for chunk in resp.iter_lines(decode_unicode=True):

            if not chunk:
                continue

            json_obj = None

            # Try direct JSON
            try:
                json_obj = json.loads(chunk)
            except:
                # Try to extract JSON inside text
                matches = re.findall(r"\{.*\}", chunk)
                for m in matches:
                    try:
                        json_obj = json.loads(m)
                        break
                    except:
                        pass

            if not json_obj:
                continue

            # audio chunks
            if "audio_base64" in json_obj:
                audio_chunks.append(json_obj["audio_base64"])

            # timestamp chunks
            if "alignment" in json_obj:
                alignment_chunks.append(json_obj["alignment"])

        # ------------------------------------------------
        # 6️⃣ Save combined output
        # ------------------------------------------------
        results.append({
            "segment_id": seg_id,
            "audio_base64": audio_chunks,
            "alignment": alignment_chunks,
            "image_url": image_url
        })

    except Exception as e:
        results.append({
            "segment_id": seg_id,
            "error": f"Request failed: {str(e)}"
        })

# ----------------------------------------------------
# 7️⃣ Final Output
# ----------------------------------------------------
output = json.dumps({
    "topic": topic,
    "segments": results
}, indent=2)

*/