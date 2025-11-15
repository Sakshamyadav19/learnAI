"""
Debug script to dump raw API response from Airia.ai to a temp file
This helps analyze the actual response structure before parsing
"""

import os
import json
import logging
from dotenv import load_dotenv
import httpx

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Environment variables
AIRIA_API_KEY = os.getenv("AIRIA_API_KEY")
AIRIA_API_URL = os.getenv("AIRIA_API_URL")
AIRIA_USER_ID = os.getenv("AIRIA_USER_ID")

TEMP_RESPONSE_FILE = "temp_response.json"

async def dump_api_response(user_input: str = "How are clouds formed"):
    """
    Make API call and dump raw response to temp file
    """
    if not AIRIA_API_KEY or not AIRIA_API_URL or not AIRIA_USER_ID:
        logger.error("Missing API configuration in environment variables")
        return
    
    payload = {
        "userId": AIRIA_USER_ID,
        "userInput": user_input,
        "asyncOutput": False
    }
    
    headers = {
        "X-API-KEY": AIRIA_API_KEY,
        "Content-Type": "application/json"
    }
    
    logger.info(f"🚀 Calling Airia.ai API with input: {user_input}")
    logger.info(f"📡 API URL: {AIRIA_API_URL}")
    
    try:
        timeout = httpx.Timeout(300.0, connect=30.0)
        
        async with httpx.AsyncClient(timeout=timeout) as client:
            payload_json = json.dumps(payload)
            
            logger.info(f"📤 Sending request...")
            response = await client.post(
                AIRIA_API_URL,
                headers=headers,
                content=payload_json
            )
            
            logger.info(f"📥 Response received: {response.status_code}")
            
            if not response.is_success:
                logger.error(f"❌ API Error: {response.status_code} - {response.text[:200]}")
                return
            
            # Get full response
            data = response.json()
            
            # Calculate response size
            response_str = json.dumps(data)
            response_size = len(response_str)
            response_size_mb = response_size / (1024 * 1024)
            
            logger.info(f"📊 Response size: {response_size:,} bytes ({response_size_mb:.2f} MB)")
            
            # Count segments/audio if present
            result0 = data.get("result", [{}])[0] if data.get("result") else {}
            result1 = data.get("result", [{}])[1] if len(data.get("result", [])) > 1 else {}
            
            logger.info(f"📦 Result[0] type: {type(result0.get('output'))}")
            logger.info(f"📦 Result[1] type: {type(result1.get('output'))}")
            
            # Check if result[0].output has audio_base64
            result0_output = result0.get("output")
            if result0_output:
                if isinstance(result0_output, str):
                    try:
                        parsed = json.loads(result0_output)
                        has_audio = "audio_base64" in parsed
                        audio_size = len(parsed.get("audio_base64", "")) if has_audio else 0
                        logger.info(f"📦 Result[0].output (parsed) - has audio_base64: {has_audio}, size: {audio_size:,} chars")
                    except:
                        logger.info(f"📦 Result[0].output - cannot parse as JSON")
                else:
                    has_audio = "audio_base64" in result0_output
                    audio_size = len(result0_output.get("audio_base64", "")) if has_audio else 0
                    logger.info(f"📦 Result[0].output (dict) - has audio_base64: {has_audio}, size: {audio_size:,} chars")
            
            # Check result[1].output for segments
            result1_output = result1.get("output")
            if result1_output and isinstance(result1_output, str):
                try:
                    parsed1 = json.loads(result1_output)
                    segments = parsed1.get("segments", [])
                    logger.info(f"📦 Result[1].output - segments count: {len(segments)}")
                    if segments:
                        logger.info(f"📦 Sample segment fields: {list(segments[0].keys()) if segments[0] else []}")
                except Exception as e:
                    logger.error(f"❌ Cannot parse result[1].output: {e}")
            
            # Write to temp file
            logger.info(f"💾 Writing response to {TEMP_RESPONSE_FILE}...")
            with open(TEMP_RESPONSE_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"✅ Response dumped to {TEMP_RESPONSE_FILE}")
            logger.info(f"📁 File size: {os.path.getsize(TEMP_RESPONSE_FILE):,} bytes ({os.path.getsize(TEMP_RESPONSE_FILE) / (1024*1024):.2f} MB)")
            
            return data
            
    except httpx.TimeoutException:
        logger.error("❌ API Request Timeout")
    except httpx.RequestError as e:
        logger.error(f"❌ Network Error: {e}")
    except Exception as e:
        logger.error(f"❌ Unexpected Error: {type(e).__name__}: {str(e)}", exc_info=True)


if __name__ == "__main__":
    import asyncio
    
    # You can change the test input here
    test_input = os.getenv("TEST_INPUT", "How are clouds formed")
    
    logger.info(f"Starting debug response dump...")
    logger.info(f"Test input: {test_input}")
    
    asyncio.run(dump_api_response(test_input))
    
    logger.info(f"✅ Done! Check {TEMP_RESPONSE_FILE} for the raw response")

