"""
Analysis script to understand the structure of the API response
Reads temp_response.json and analyzes result[0] and result[1] structures

UPDATED: Now checks for segments array in result[0].output with audio_base64 per segment
"""

import json
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

TEMP_RESPONSE_FILE = "temp_response.json"

def analyze_response():
    """
    Analyze the dumped response structure
    """
    if not os.path.exists(TEMP_RESPONSE_FILE):
        logger.error(f"❌ {TEMP_RESPONSE_FILE} not found. Run debug_response.py first!")
        return
    
    logger.info(f"📖 Reading {TEMP_RESPONSE_FILE}...")
    
    with open(TEMP_RESPONSE_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    logger.info("=" * 80)
    logger.info("📊 RESPONSE STRUCTURE ANALYSIS")
    logger.info("=" * 80)
    
    # Top level structure
    logger.info(f"\n📦 Top-level keys: {list(data.keys())}")
    
    # Analyze result array
    results = data.get("result", [])
    logger.info(f"\n📦 Result array length: {len(results)}")
    
    if len(results) < 2:
        logger.error("❌ Not enough results in response!")
        return
    
    # ===== ANALYZE RESULT[0] =====
    logger.info("\n" + "=" * 80)
    logger.info("📦 ANALYZING RESULT[0] (Narration/Image Data)")
    logger.info("=" * 80)
    
    result0 = results[0]
    logger.info(f"Type: {type(result0)}")
    logger.info(f"Keys: {list(result0.keys())}")
    logger.info(f"stepId: {result0.get('stepId')}")
    logger.info(f"stepType: {result0.get('stepType')}")
    
    result0_output = result0.get("output")
    logger.info(f"\n📦 result[0].output type: {type(result0_output)}")
    
    if not result0_output:
        logger.error("❌ result[0].output is missing!")
        parsed_result0 = None
    elif isinstance(result0_output, str):
        logger.info("✅ result[0].output is a JSON string")
        try:
            parsed_result0 = json.loads(result0_output)
            logger.info(f"✅ Successfully parsed as JSON")
            logger.info(f"📦 Parsed keys: {list(parsed_result0.keys())}")
        except json.JSONDecodeError as e:
            logger.error(f"❌ Cannot parse result[0].output as JSON: {e}")
            logger.error(f"   First 200 chars: {result0_output[:200]}")
            parsed_result0 = None
    else:
        logger.info("✅ result[0].output is already a dict")
        parsed_result0 = result0_output
        logger.info(f"📦 Keys: {list(parsed_result0.keys())}")
    
    # Check for segments array in result[0] (should contain narration and image_url per segment)
    result0_segments = None
    if parsed_result0:
        if "segments" in parsed_result0:
            result0_segments = parsed_result0["segments"]
            logger.info(f"\n✅ Found segments array in result[0].output: {len(result0_segments)} segments")
            
            if not isinstance(result0_segments, list):
                logger.error(f"❌ result[0].output.segments is not a list, it's {type(result0_segments)}")
                result0_segments = None
            else:
                # Show segment structure
                if result0_segments:
                    logger.info(f"\n   📋 Result[0] segment structure (first segment):")
                    sample = result0_segments[0]
                    for key, value in sample.items():
                        if isinstance(value, str) and len(value) > 100:
                            logger.info(f"      {key}: (string, {len(value):,} chars)")
                            logger.info(f"         Preview: {value[:80]}...")
                        else:
                            logger.info(f"      {key}: {value}")
                    
                    # Check if all segments have narration and image_url
                    segments_with_narration = [s for s in result0_segments if s.get("narration")]
                    segments_with_image = [s for s in result0_segments if s.get("image_url")]
                    logger.info(f"\n   📊 Segments with narration: {len(segments_with_narration)}/{len(result0_segments)}")
                    logger.info(f"   📊 Segments with image_url: {len(segments_with_image)}/{len(result0_segments)}")
                    
                    if len(segments_with_narration) < len(result0_segments):
                        missing = len(result0_segments) - len(segments_with_narration)
                        logger.warning(f"      ⚠️  {missing} segments are missing narration")
                    
                    if len(segments_with_image) < len(result0_segments):
                        missing = len(result0_segments) - len(segments_with_image)
                        logger.warning(f"      ⚠️  {missing} segments are missing image_url")
                    
                    # Get segment IDs
                    segment_ids_0 = [seg.get("segment_id") for seg in result0_segments if seg.get("segment_id") is not None]
                    logger.info(f"   🔍 Segment IDs: {sorted(segment_ids_0)}")
        else:
            logger.warning(f"   ⚠️  No segments array found in result[0].output")
            logger.info(f"      Available keys: {list(parsed_result0.keys())}")
    
    # ===== ANALYZE RESULT[1] =====
    logger.info("\n" + "=" * 80)
    logger.info("📦 ANALYZING RESULT[1] (Audio Data)")
    logger.info("=" * 80)
    
    result1 = results[1]
    logger.info(f"Type: {type(result1)}")
    logger.info(f"Keys: {list(result1.keys())}")
    logger.info(f"stepId: {result1.get('stepId')}")
    logger.info(f"stepType: {result1.get('stepType')}")
    
    result1_output = result1.get("output")
    logger.info(f"\n📦 result[1].output type: {type(result1_output)}")
    
    if not result1_output:
        logger.error("❌ result[1].output is missing!")
        parsed_result1 = None
    elif isinstance(result1_output, str):
        logger.info("✅ result[1].output is a JSON string")
        try:
            parsed_result1 = json.loads(result1_output)
            logger.info(f"✅ Successfully parsed as JSON")
            logger.info(f"📦 Parsed keys: {list(parsed_result1.keys())}")
        except json.JSONDecodeError as e:
            logger.error(f"❌ Cannot parse result[1].output as JSON: {e}")
            logger.error(f"   First 200 chars: {result1_output[:200]}")
            parsed_result1 = None
    else:
        logger.info("✅ result[1].output is already a dict")
        parsed_result1 = result1_output
    
    # Extract segments from result[1] (should contain audio_base64 per segment)
    result1_segments = None
    if parsed_result1:
        if "segments" in parsed_result1:
            result1_segments = parsed_result1["segments"]
            logger.info(f"\n✅ Found segments array in result[1].output: {len(result1_segments)} segments")
            
            if not isinstance(result1_segments, list):
                logger.error(f"❌ result[1].output.segments is not a list, it's {type(result1_segments)}")
                result1_segments = None
            else:
                # Show segment structure
                if result1_segments:
                    logger.info(f"\n   📋 Result[1] segment structure (first segment):")
                    sample = result1_segments[0]
                    for key, value in sample.items():
                        if key == "audio_base64" and isinstance(value, str):
                            logger.info(f"      {key}: (string, {len(value):,} chars)")
                            logger.info(f"         Preview: {value[:50]}...")
                        else:
                            logger.info(f"      {key}: {value}")
                    
                    # Check if all segments have audio_base64
                    segments_with_audio = [s for s in result1_segments if s.get("audio_base64")]
                    logger.info(f"\n   📊 Segments with audio_base64: {len(segments_with_audio)}/{len(result1_segments)}")
                    
                    if len(segments_with_audio) < len(result1_segments):
                        missing = len(result1_segments) - len(segments_with_audio)
                        logger.warning(f"      ⚠️  {missing} segments are missing audio_base64")
                    
                    # Get segment IDs
                    segment_ids_1 = [seg.get("segment_id") for seg in result1_segments if seg.get("segment_id") is not None]
                    logger.info(f"   🔍 Segment IDs: {sorted(segment_ids_1)}")
        else:
            logger.warning(f"   ⚠️  No segments array found in result[1].output")
            logger.info(f"      Available keys: {list(parsed_result1.keys())}")
    
    # ===== COMPARE AND MATCH SEGMENTS =====
    if parsed_result0 and parsed_result1 and result0_segments and result1_segments:
        logger.info("\n" + "=" * 80)
        logger.info("🔍 SEGMENT ID COMPARISON AND MATCHING")
        logger.info("=" * 80)
        
        # Get segment IDs from both results
        segment_ids_0 = [seg.get("segment_id") for seg in result0_segments if seg.get("segment_id") is not None]
        segment_ids_1 = [seg.get("segment_id") for seg in result1_segments if seg.get("segment_id") is not None]
        
        segment_ids_0_set = set(segment_ids_0)
        segment_ids_1_set = set(segment_ids_1)
        
        common_ids = segment_ids_0_set & segment_ids_1_set
        only_in_0 = segment_ids_0_set - segment_ids_1_set
        only_in_1 = segment_ids_1_set - segment_ids_0_set
        
        logger.info(f"\n📦 Result[0] segment IDs: {sorted(segment_ids_0)}")
        logger.info(f"📦 Result[1] segment IDs: {sorted(segment_ids_1)}")
        logger.info(f"✅ Common segment IDs (in both): {sorted(common_ids)}")
        
        if only_in_0:
            logger.warning(f"⚠️  Segment IDs only in result[0]: {sorted(only_in_0)}")
        if only_in_1:
            logger.warning(f"⚠️  Segment IDs only in result[1]: {sorted(only_in_1)}")
        
        # Match segments and show combined structure
        logger.info(f"\n" + "=" * 80)
        logger.info("🔗 MATCHING LOGIC AND COMBINED SEGMENTS")
        logger.info("=" * 80)
        
        logger.info(f"\n📋 Matching logic:")
        logger.info(f"   1. Find segment with matching segment_id in result[0].segments")
        logger.info(f"      → Extract narration, image_url")
        logger.info(f"   2. Find segment with matching segment_id in result[1].segments")
        logger.info(f"      → Extract audio_base64")
        logger.info(f"   3. Combine into single segment object")
        
        # Show sample combined segments
        logger.info(f"\n📋 Combined segments structure (for all common segment_ids):")
        matched_count = 0
        for segment_id in sorted(common_ids):
            seg0 = next((s for s in result0_segments if s.get("segment_id") == segment_id), None)
            seg1 = next((s for s in result1_segments if s.get("segment_id") == segment_id), None)
            
            if seg0 and seg1:
                matched_count += 1
                combined = {
                    "segment_id": segment_id,
                    "audioBase64": seg1.get("audio_base64", ""),  # From result[1]
                    "imageUrl": seg0.get("image_url"),  # From result[0]
                    "narration": seg0.get("narration", ""),  # From result[0]
                    "duration": seg0.get("duration"),  # From result[0]
                }
                
                logger.info(f"\n   ✅ Segment {segment_id}:")
                has_audio = bool(combined['audioBase64'])
                logger.info(f"      audioBase64: {'✅' if has_audio else '❌'} ({len(combined['audioBase64']):,} chars)" if has_audio else "      audioBase64: ❌ (missing)")
                has_image = bool(combined['imageUrl'])
                logger.info(f"      imageUrl: {'✅' if has_image else '❌'} {combined['imageUrl'] or '(missing)'}")
                has_narration = bool(combined['narration'])
                logger.info(f"      narration: {'✅' if has_narration else '❌'} ({len(combined['narration']):,} chars)" if has_narration else "      narration: ❌ (missing)")
                if combined.get('duration') is not None:
                    logger.info(f"      duration: ✅ {combined['duration']}s")
            else:
                logger.warning(f"\n   ❌ Segment {segment_id}: Cannot find in both results")
                if seg0:
                    logger.info(f"      Found in result[0]: ✅")
                else:
                    logger.warning(f"      Missing from result[0]: ❌")
                if seg1:
                    logger.info(f"      Found in result[1]: ✅")
                else:
                    logger.warning(f"      Missing from result[1]: ❌")
        
        logger.info(f"\n✅ Successfully matched {matched_count}/{len(common_ids)} segments")
        
        if matched_count < len(common_ids):
            logger.warning(f"⚠️  {len(common_ids) - matched_count} segments could not be fully matched")
        
        # ===== SUMMARY =====
        logger.info("\n" + "=" * 80)
        logger.info("📊 SUMMARY")
        logger.info("=" * 80)
        
        logger.info(f"\n✅ Result[0] structure:")
        logger.info(f"   - Has segments array with {len(result0_segments)} segments")
        logger.info(f"   - Each segment has: segment_id, narration, image_url, duration")
        logger.info(f"   - Segment IDs: {sorted(segment_ids_0)}")
        
        logger.info(f"\n✅ Result[1] structure:")
        logger.info(f"   - Has segments array with {len(result1_segments)} segments")
        logger.info(f"   - Each segment has: segment_id, audio_base64")
        logger.info(f"   - Segment IDs: {sorted(segment_ids_1)}")
        
        logger.info(f"\n✅ Matching:")
        logger.info(f"   - Common segment IDs: {len(common_ids)}")
        logger.info(f"   - Successfully matched: {matched_count}")
        logger.info(f"   - Match by segment_id from both arrays")
        
        logger.info(f"\n✅ Expected final structure per segment:")
        logger.info(f"   {{")
        logger.info(f"     'segment_id': int,")
        logger.info(f"     'audioBase64': str,  # from result[1].segments[segment_id]")
        logger.info(f"     'imageUrl': str,     # from result[0].segments[segment_id]")
        logger.info(f"     'narration': str,    # from result[0].segments[segment_id]")
        logger.info(f"     'duration': int      # from result[0].segments[segment_id] (optional)")
        logger.info(f"   }}")
    
    elif not result0_segments:
        logger.error("\n❌ Cannot match segments - result[0] does not have segments array!")
        logger.error("   Please check if result[0].output structure is correct")
    elif not result1_segments:
        logger.error("\n❌ Cannot match segments - result[1] does not have segments array!")
        logger.error("   Please check if result[1].output structure is correct")


if __name__ == "__main__":
    logger.info("Starting response analysis...")
    analyze_response()
    logger.info("✅ Analysis complete!")
