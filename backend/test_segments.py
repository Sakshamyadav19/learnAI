"""
Test script to understand segment matching between result[0] and result[1]
Maps segments by segment_id and shows how to combine them

UPDATED: 
- result[0].output.segments contains narration and image_url
- result[1].output.segments contains audio_base64
"""

import json
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

TEMP_RESPONSE_FILE = "temp_response.json"

def test_segment_matching():
    """
    Analyze segment structure and matching logic
    """
    if not os.path.exists(TEMP_RESPONSE_FILE):
        logger.error(f"❌ {TEMP_RESPONSE_FILE} not found. Run debug_response.py first!")
        return
    
    logger.info(f"📖 Reading {TEMP_RESPONSE_FILE}...")
    
    with open(TEMP_RESPONSE_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    results = data.get("result", [])
    if len(results) < 2:
        logger.error("❌ Not enough results!")
        return
    
    logger.info("=" * 80)
    logger.info("🔍 SEGMENT MATCHING ANALYSIS")
    logger.info("=" * 80)
    
    # ===== PARSE RESULT[0] =====
    result0 = results[0]
    result0_output = result0.get("output")
    
    if isinstance(result0_output, str):
        try:
            parsed_result0 = json.loads(result0_output)
        except json.JSONDecodeError as e:
            logger.error(f"❌ Cannot parse result[0].output: {e}")
            return
    else:
        parsed_result0 = result0_output
    
    logger.info(f"\n📦 RESULT[0] STRUCTURE (Narration/Image Data):")
    logger.info(f"   Keys: {list(parsed_result0.keys())}")
    
    # Check for segments array in result[0] (should contain narration and image_url)
    if "segments" in parsed_result0:
        result0_segments = parsed_result0["segments"]
        logger.info(f"   ✅ Has segments array: {len(result0_segments)} segments")
        
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
            
            # Check for required fields
            has_narration = any(s.get("narration") for s in result0_segments)
            has_image_url = any(s.get("image_url") for s in result0_segments)
            logger.info(f"\n   📊 Segments with narration: {sum(1 for s in result0_segments if s.get('narration'))}/{len(result0_segments)}")
            logger.info(f"   📊 Segments with image_url: {sum(1 for s in result0_segments if s.get('image_url'))}/{len(result0_segments)}")
    else:
        logger.error(f"   ❌ No segments array found in result[0]!")
        logger.error(f"      Available keys: {list(parsed_result0.keys())}")
        result0_segments = None
    
    # ===== PARSE RESULT[1] =====
    result1 = results[1]
    result1_output = result1.get("output")
    
    if isinstance(result1_output, str):
        try:
            parsed_result1 = json.loads(result1_output)
        except json.JSONDecodeError as e:
            logger.error(f"❌ Cannot parse result[1].output: {e}")
            return
    else:
        parsed_result1 = result1_output
    
    logger.info(f"\n📦 RESULT[1] STRUCTURE (Audio Data):")
    logger.info(f"   Keys: {list(parsed_result1.keys())}")
    
    result1_segments = parsed_result1.get("segments", [])
    logger.info(f"   ✅ Has segments array: {len(result1_segments)} segments")
    
    if result1_segments:
        logger.info(f"\n   📋 Result[1] segment structure (first segment):")
        sample = result1_segments[0]
        for key, value in sample.items():
            if key == "audio_base64" and isinstance(value, str):
                logger.info(f"      {key}: (string, {len(value):,} chars)")
                logger.info(f"         Preview: {value[:50]}...")
            else:
                logger.info(f"      {key}: {value}")
        
        # Check for audio_base64
        segments_with_audio = [s for s in result1_segments if s.get("audio_base64")]
        logger.info(f"\n   📊 Segments with audio_base64: {len(segments_with_audio)}/{len(result1_segments)}")
        
        if len(segments_with_audio) < len(result1_segments):
            missing = len(result1_segments) - len(segments_with_audio)
            logger.warning(f"      ⚠️  {missing} segments are missing audio_base64")
    
    # ===== MATCHING LOGIC =====
    logger.info("\n" + "=" * 80)
    logger.info("🔗 SEGMENT MATCHING LOGIC")
    logger.info("=" * 80)
    
    # Get segment IDs from both results
    if result0_segments:
        segment_ids_0 = [seg.get("segment_id") for seg in result0_segments if seg.get("segment_id") is not None]
        logger.info(f"\n📦 Result[0] segment IDs: {sorted(segment_ids_0)}")
    else:
        segment_ids_0 = []
        logger.warning(f"\n⚠️  Result[0] has no segments array")
    
    if result1_segments:
        segment_ids_1 = [seg.get("segment_id") for seg in result1_segments if seg.get("segment_id") is not None]
        logger.info(f"📦 Result[1] segment IDs: {sorted(segment_ids_1)}")
    else:
        segment_ids_1 = []
        logger.warning(f"⚠️  Result[1] has no segments array")
    
    # Match segments
    if result0_segments and result1_segments:
        all_ids = set(segment_ids_0 + segment_ids_1)
        common_ids = set(segment_ids_0) & set(segment_ids_1)
        only_in_0 = set(segment_ids_0) - set(segment_ids_1)
        only_in_1 = set(segment_ids_1) - set(segment_ids_0)
        
        logger.info(f"\n📦 All unique segment IDs: {sorted(all_ids)}")
        logger.info(f"✅ Common segment IDs (in both): {sorted(common_ids)}")
        
        if only_in_0:
            logger.warning(f"⚠️  Segment IDs only in result[0]: {sorted(only_in_0)}")
        if only_in_1:
            logger.warning(f"⚠️  Segment IDs only in result[1]: {sorted(only_in_1)}")
        
        # Match segments
        logger.info(f"\n🔗 MATCHING LOGIC:")
        logger.info(f"   For each segment_id:")
        logger.info(f"   1. Get narration, image_url from result[0].segments[segment_id]")
        logger.info(f"   2. Get audio_base64 from result[1].segments[segment_id]")
        logger.info(f"   3. Combine into single segment object")
        
        # Show sample matching for all common segments
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
    else:
        logger.error(f"\n❌ Cannot match segments - missing segments array in one or both results")
        if not result0_segments:
            logger.error(f"   Result[0] missing segments array")
        if not result1_segments:
            logger.error(f"   Result[1] missing segments array")
    
    # ===== FINAL SUMMARY =====
    logger.info("\n" + "=" * 80)
    logger.info("📊 SUMMARY")
    logger.info("=" * 80)
    
    if result0_segments:
        logger.info(f"\n✅ Result[0] has {len(result0_segments)} segments with:")
        logger.info(f"   - segment_id")
        logger.info(f"   - narration")
        logger.info(f"   - image_url")
        logger.info(f"   - duration (optional)")
    else:
        logger.warning(f"\n⚠️  Result[0] has no segments array")
    
    if result1_segments:
        logger.info(f"\n✅ Result[1] has {len(result1_segments)} segments with:")
        logger.info(f"   - segment_id")
        logger.info(f"   - audio_base64")
    else:
        logger.warning(f"\n⚠️  Result[1] has no segments array")
    
    if result0_segments and result1_segments:
        logger.info(f"\n✅ Matching: Match by segment_id from both arrays")
        logger.info(f"   Common segment IDs: {len(set(segment_ids_0) & set(segment_ids_1))}")
    
    logger.info(f"\n✅ Expected final structure per segment:")
    logger.info(f"   {{")
    logger.info(f"     'segment_id': int,")
    logger.info(f"     'audioBase64': str,  # from result[1].segments[segment_id]")
    logger.info(f"     'imageUrl': str,     # from result[0].segments[segment_id]")
    logger.info(f"     'narration': str,    # from result[0].segments[segment_id]")
    logger.info(f"     'duration': int      # from result[0].segments[segment_id] (optional)")
    logger.info(f"   }}")


if __name__ == "__main__":
    logger.info("Starting segment matching analysis...")
    test_segment_matching()
    logger.info("✅ Done!")

