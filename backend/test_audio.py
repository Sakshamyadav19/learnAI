"""
Test script to decode audio_base64 from result[1].output segments and save as audio files
Verifies that audio can be successfully decoded and played for all segments

UPDATED: 
- Now handles segments array in result[1].output with segment_id and audio_base64 per segment
- Uses combine_audio_base64 pattern to handle chunks properly
"""

import json
import base64
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

TEMP_RESPONSE_FILE = "temp_response.json"
AUDIO_OUTPUT_DIR = "test_audio"


def combine_audio_base64(chunks):
    """
    Combine audio base64 chunks by decoding each chunk to binary,
    combining the binary data, then re-encoding to base64.
    
    Args:
        chunks: List of base64 strings or a single base64 string
        
    Returns:
        Combined base64 string
    """
    # Handle single string (wrap in list)
    if isinstance(chunks, str):
        chunks = [chunks]
    elif not isinstance(chunks, list):
        chunks = [str(chunks)]
    
    combined = b""
    for c in chunks:
        # Decode each chunk to binary and combine
        combined += base64.b64decode(str(c))
    
    # Re-encode combined binary to base64
    return base64.b64encode(combined).decode("utf-8")


def decode_audio_base64(audio_base64, output_path: str):
    """
    Decode base64 audio string to audio file (MP3/WAV)
    
    IMPORTANT: audio_base64 for a segment is entirely before the alignment key.
    We decode the FULL audio_base64 string without any truncation.
    Uses combine_audio_base64 pattern to properly handle chunks.
    
    Args:
        audio_base64: Base64 string or list of base64 strings (chunks)
        output_path: Path to save the decoded audio file
    """
    try:
        # Handle data URI prefix if present
        if isinstance(audio_base64, str) and audio_base64.startswith("data:"):
            audio_base64 = audio_base64.split(",")[1]
        
        # Combine audio chunks if it's a list, or use directly if string
        if isinstance(audio_base64, list):
            logger.info(f"   📦 Combining {len(audio_base64)} audio chunks...")
            final_audio_b64 = combine_audio_base64(audio_base64)
        else:
            # Single base64 string
            audio_base64_str = str(audio_base64).strip()
            final_audio_b64 = audio_base64_str
        
        # Decode the final combined base64 to binary
        try:
            audio_data = base64.b64decode(final_audio_b64)
            logger.debug(f"   📊 Decoded audio size: {len(audio_data):,} bytes from {len(final_audio_b64):,} base64 chars")
        except Exception as e:
            logger.error(f"   ❌ Base64 decode error: {e}")
            logger.error(f"   First 100 chars: {final_audio_b64[:100]}")
            return False
        
        # Write to file (use .mp3 extension as per example, but detect format if possible)
        with open(output_path, 'wb') as f:
            f.write(audio_data)
        
        file_size = os.path.getsize(output_path)
        logger.info(f"   ✅ Saved audio to {output_path} ({file_size:,} bytes, {file_size / 1024:.2f} KB)")
        
        # Try to detect audio format from header
        try:
            with open(output_path, 'rb') as f:
                header = f.read(4)
                if header == b'RIFF':
                    logger.info(f"   ✅ Detected WAV format (RIFF header)")
                elif header[:3] == b'ID3' or header[:2] == b'\xff\xfb':
                    logger.info(f"   ✅ Detected MP3 format")
                elif header[:4] == b'fLaC':
                    logger.info(f"   ✅ Detected FLAC format")
                else:
                    logger.warning(f"   ⚠️  Unknown audio format (header: {header})")
        except Exception:
            pass
        
        return True
    except Exception as e:
        logger.error(f"   ❌ Failed to decode audio: {e}")
        logger.error(f"   Type: {type(audio_base64)}")
        return False


def test_audio_decoding():
    """
    Extract and decode audio from temp_response.json for all segments
    """
    if not os.path.exists(TEMP_RESPONSE_FILE):
        logger.error(f"❌ {TEMP_RESPONSE_FILE} not found. Run debug_response.py first!")
        return
    
    # Create output directory
    os.makedirs(AUDIO_OUTPUT_DIR, exist_ok=True)
    
    logger.info(f"📖 Reading {TEMP_RESPONSE_FILE}...")
    
    with open(TEMP_RESPONSE_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    logger.info("=" * 80)
    logger.info("🔊 TESTING AUDIO DECODING FOR ALL SEGMENTS")
    logger.info("=" * 80)
    
    results = data.get("result", [])
    if len(results) < 2:
        logger.error("❌ Not enough results! Need at least result[0] and result[1]")
        return
    
    # Extract audio from result[1] (swapped structure)
    result1 = results[1]
    result1_output = result1.get("output")
    
    if not result1_output:
        logger.error("❌ result[1].output is missing!")
        return
    
    # Parse result[1].output if it's a string
    if isinstance(result1_output, str):
        try:
            parsed_result1 = json.loads(result1_output)
            logger.info(f"✅ Parsed result[1].output JSON")
        except json.JSONDecodeError as e:
            logger.error(f"❌ Cannot parse result[1].output: {e}")
            return
    else:
        parsed_result1 = result1_output
    
    # Check for segments array in result[1].output (contains audio_base64)
    segments = parsed_result1.get("segments", [])
    
    if not isinstance(segments, list):
        logger.error(f"❌ result[1].output.segments is not a list, it's {type(segments)}")
        return
    
    if len(segments) == 0:
        logger.error("❌ result[1].output.segments is empty!")
        return
    
    logger.info(f"📦 Found {len(segments)} segments in result[1].output")
    
    # Get segment IDs and validate structure
    segment_ids = []
    for i, segment in enumerate(segments):
        segment_id = segment.get("segment_id")
        if segment_id is None:
            logger.warning(f"⚠️  Segment at index {i} has no segment_id, skipping")
            continue
        segment_ids.append(segment_id)
    
    logger.info(f"🔍 Segment IDs found: {sorted(segment_ids)}")
    logger.info(f"📊 Processing {len(segment_ids)} segments with valid segment_id")
    
    # Decode audio for all segments
    logger.info(f"\n🎵 Decoding audio for all segments...")
    successful_decodes = []
    failed_decodes = []
    
    for segment in segments:
        segment_id = segment.get("segment_id")
        audio_base64 = segment.get("audio_base64")
        
        if segment_id is None:
            logger.warning(f"⚠️  Skipping segment with no segment_id")
            continue
        
        logger.info(f"\n🎵 Processing segment {segment_id}...")
        
        if not audio_base64:
            logger.warning(f"   ⚠️  Segment {segment_id} has no audio_base64")
            failed_decodes.append((segment_id, "Missing audio_base64"))
            continue
        
        # Check audio_base64 type and length
        audio_type = type(audio_base64).__name__
        if isinstance(audio_base64, str):
            audio_len = len(audio_base64)
            logger.info(f"   📦 audio_base64: {audio_type}, length: {audio_len:,} characters")
            logger.info(f"      Preview: {audio_base64[:50]}...")
        elif isinstance(audio_base64, list):
            audio_len = sum(len(str(chunk)) for chunk in audio_base64)
            logger.info(f"   📦 audio_base64: {audio_type} with {len(audio_base64)} chunks, total length: {audio_len:,} characters")
        else:
            logger.warning(f"   ⚠️  audio_base64 is unexpected type: {audio_type}")
            failed_decodes.append((segment_id, f"Unexpected type: {audio_type}"))
            continue
        
        # Validate base64 format (check first few characters)
        try:
            if isinstance(audio_base64, str):
                test_str = audio_base64.strip()
            else:
                test_str = "".join(str(chunk) for chunk in audio_base64).strip()
            
            # Try to decode a small portion
            if test_str:
                test_decode = base64.b64decode(test_str[:100])
                logger.info(f"   ✅ Base64 format appears valid")
            else:
                logger.error(f"   ❌ audio_base64 is empty")
                failed_decodes.append((segment_id, "Empty audio_base64"))
                continue
        except Exception as e:
            logger.error(f"   ❌ Invalid base64 format: {e}")
            failed_decodes.append((segment_id, f"Invalid base64: {str(e)}"))
            continue
        
        # Decode and save (use .mp3 extension as per example pattern)
        output_path = os.path.join(AUDIO_OUTPUT_DIR, f"audio_segment_{segment_id}.mp3")
        logger.info(f"   💾 Decoding to {output_path}...")
        
        if decode_audio_base64(audio_base64, output_path):
            # Verify file was created (format detection is done inside decode_audio_base64)
            if os.path.exists(output_path):
                file_size = os.path.getsize(output_path)
                successful_decodes.append((segment_id, output_path, file_size))
            else:
                logger.error(f"   ❌ File was not created")
                failed_decodes.append((segment_id, "File creation failed"))
        else:
            failed_decodes.append((segment_id, "Decode function failed"))
    
    # Summary
    logger.info("\n" + "=" * 80)
    logger.info("📊 DECODING SUMMARY")
    logger.info("=" * 80)
    
    logger.info(f"\n✅ Successfully decoded: {len(successful_decodes)}/{len(segment_ids)} segments")
    
    if successful_decodes:
        logger.info(f"\n✅ Successful decodes:")
        total_size = 0
        for segment_id, file_path, file_size in successful_decodes:
            logger.info(f"   Segment {segment_id}: {file_path} ({file_size:,} bytes, {file_size / 1024:.2f} KB)")
            total_size += file_size
        logger.info(f"\n   Total size: {total_size:,} bytes ({total_size / (1024*1024):.2f} MB)")
    
    if failed_decodes:
        logger.error(f"\n❌ Failed decodes: {len(failed_decodes)}/{len(segment_ids)} segments")
        for segment_id, error_msg in failed_decodes:
            logger.error(f"   Segment {segment_id}: {error_msg}")
    
    logger.info(f"\n📁 Audio files saved in: {AUDIO_OUTPUT_DIR}/")
    logger.info(f"✅ Audio decoding test complete!")


if __name__ == "__main__":
    logger.info("Starting audio decoding test...")
    test_audio_decoding()
    logger.info("✅ Done!")
