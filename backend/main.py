"""
FastAPI Backend for Learn.AI Lesson Generation
Handles API calls to Airia.ai and returns processed lesson data
"""

import os
import json
import base64
import logging
import re
from typing import Optional, List
from dotenv import load_dotenv
import httpx
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from fastino_client import register_user, ingest_lesson as ingest_lesson_fastino, ingest_quiz, query_fastino

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Learn.AI Backend API",
    description="Backend API for lesson generation",
    version="1.0.0"
)

# Configure CORS
# Allow all localhost origins for development
# In production, replace with specific allowed origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development (change to specific list in production)
    allow_credentials=False,  # Set to False when using allow_origins=["*"]
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
    expose_headers=["*"],
    max_age=3600,
)

# Environment variables
AIRIA_API_KEY = os.getenv("AIRIA_API_KEY")
AIRIA_API_URL = os.getenv("AIRIA_API_URL")  # Lesson pipeline URL
AIRIA_QUIZ_API_URL = os.getenv("AIRIA_QUIZ_API_URL", "https://api.airia.ai/v2/PipelineExecution/2fd01fd6-793e-4b54-af51-3c7605fcec41")  # Quiz pipeline URL
AIRIA_USER_ID = os.getenv("AIRIA_USER_ID")


# Request/Response models
class GenerateLessonRequest(BaseModel):
    userInput: str
    user_id: Optional[str] = None  # Fastino user ID for chunks retrieval


class GenerateQuizRequest(BaseModel):
    userInput: str  # User lesson prompt
    user_id: Optional[str] = None  # Fastino user ID for chunks retrieval


class QuizQuestionOption(BaseModel):
    id: int
    question: str
    options: List[str]
    correctAnswer: int  # Index of correct answer in options array


class LessonSegment(BaseModel):
    segment_id: int
    imageUrl: Optional[str] = None
    audioBase64: str
    narration: str


class LessonDataResponse(BaseModel):
    topic: str
    segments: List[LessonSegment]


class ErrorResponse(BaseModel):
    error: str


# Global exception handler to ensure CORS headers are always present
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler to ensure CORS headers on all errors"""
    logger.error(f"❌ Unhandled exception: {type(exc).__name__}: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"error": f"Internal server error: {str(exc)}"},
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "*",
            "Access-Control-Allow-Headers": "*",
        }
    )


# Health check endpoint
@app.get("/")
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok", "service": "Learn.AI Backend API"}


# ===== Fastino AI Endpoints =====

class RegisterUserRequest(BaseModel):
    email: str
    name: str
    age: int
    tone: str


class RegisterUserResponse(BaseModel):
    user_id: str


@app.post("/fastino/register", response_model=RegisterUserResponse)
async def fastino_register(request: RegisterUserRequest):
    """
    Register a user with Fastino AI
    
    Args:
        request: RegisterUserRequest with email, name, age, and tone
        
    Returns:
        RegisterUserResponse with user_id
    """
    logger.info(f"🔐 Registering user with Fastino: {request.email}")
    logger.info(f"📝 User details: name={request.name}, age={request.age}, tone={request.tone}")
    
    try:
        result = await register_user(request.email, request.name, request.age, request.tone)
        
        if result and result.get("user_id"):
            user_id = result["user_id"]
            logger.info(f"✅ User registered successfully: {user_id}")
            return RegisterUserResponse(user_id=user_id)
        else:
            logger.warning(f"⚠️  Fastino registration failed for {request.email}")
            return JSONResponse(
                status_code=500,
                content={"error": "Failed to register user with Fastino"},
                headers={"Access-Control-Allow-Origin": "*"}
            )
    except Exception as e:
        logger.error(f"❌ Error during Fastino registration: {e}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"error": f"Internal server error: {str(e)}"},
            headers={"Access-Control-Allow-Origin": "*"}
        )


class IngestLessonRequest(BaseModel):
    user_id: str
    topic: str


class IngestQuizRequest(BaseModel):
    user_id: str
    topic: str
    question: str
    answer: str  # correct answer
    user_answer: str
    verdict: str  # "correct" or "wrong"


class IngestDataResponse(BaseModel):
    success: bool
    message: str


@app.post("/fastino/ingest/lesson", response_model=IngestDataResponse)
async def fastino_ingest_lesson(request: IngestLessonRequest):
    """
    Ingest lesson data to Fastino AI
    
    Args:
        request: IngestLessonRequest with user_id and topic
        
    Returns:
        IngestDataResponse with success status
    """
    logger.info(f"📤 Ingesting lesson data for user: {request.user_id}, topic: {request.topic}")
    
    try:
        success = await ingest_lesson(request.user_id, request.topic)
        
        if success:
            logger.info(f"✅ Successfully ingested lesson data")
            return IngestDataResponse(success=True, message="Lesson data ingested successfully")
        else:
            logger.warning(f"⚠️  Fastino lesson ingestion failed for user {request.user_id}")
            return IngestDataResponse(success=False, message="Failed to ingest lesson data")
    except Exception as e:
        logger.error(f"❌ Error during Fastino lesson ingestion: {e}", exc_info=True)
        return IngestDataResponse(success=False, message=f"Internal server error: {str(e)}")


@app.post("/fastino/ingest/quiz", response_model=IngestDataResponse)
async def fastino_ingest_quiz(request: IngestQuizRequest):
    """
    Ingest quiz data to Fastino AI
    
    Args:
        request: IngestQuizRequest with user_id, topic, question, answer, user_answer, verdict
        
    Returns:
        IngestDataResponse with success status
    """
    logger.info(f"📤 Ingesting quiz data for user: {request.user_id}")
    
    try:
        success = await ingest_quiz(
            request.user_id,
            request.topic,
            request.question,
            request.answer,
            request.user_answer,
            request.verdict
        )
        
        if success:
            logger.info(f"✅ Successfully ingested quiz data")
            return IngestDataResponse(success=True, message="Quiz data ingested successfully")
        else:
            logger.warning(f"⚠️  Fastino quiz ingestion failed for user {request.user_id}")
            return IngestDataResponse(success=False, message="Failed to ingest quiz data")
    except Exception as e:
        logger.error(f"❌ Error during Fastino quiz ingestion: {e}", exc_info=True)
        return IngestDataResponse(success=False, message=f"Internal server error: {str(e)}")


class ConversationMessage(BaseModel):
    role: str  # "system", "user", or "assistant"
    content: str




@app.post("/generateLesson", response_model=LessonDataResponse)
async def generate_lesson(request: GenerateLessonRequest):
    """
    Generate a lesson by calling Airia.ai API
    
    Args:
        request: GenerateLessonRequest with userInput and optional user_id
        
    Returns:
        LessonDataResponse with topic and segments
        
    Raises:
        HTTPException: If API call fails or response is invalid
    """
    logger.info(f"🚀 Received lesson generation request: {request.userInput}")
    if request.user_id:
        logger.info(f"👤 Fastino user_id from frontend: {request.user_id}")
    else:
        logger.info("👤 No Fastino user_id provided in request")
    
    # ===== STEP 1: First ingest lesson prompt to Fastino if user_id is provided =====
    if request.user_id:
        logger.info(f"📤 Ingesting lesson prompt to Fastino for user: {request.user_id}")
        try:
            ingest_success = await ingest_lesson_fastino(request.user_id, request.userInput)
            if ingest_success:
                logger.info("✅ Lesson prompt ingested to Fastino successfully")
            else:
                logger.warning("⚠️  Lesson prompt ingestion to Fastino failed, continuing with lesson generation")
        except Exception as e:
            logger.warning(f"⚠️  Error ingesting lesson prompt to Fastino: {e}. Continuing with lesson generation.")
    
    # ===== STEP 2: Query Fastino for user context if user_id is provided =====
    enhanced_prompt = request.userInput
    
    if request.user_id:
        logger.info(f"🔍 Querying Fastino for user context for lesson generation for user: {request.user_id}")
        
        # Create a question that helps Fastino understand what context we need about the topic
        # Note: Do not put userInput in quotes as Fastino cannot read it properly
        question = (
            f"What past learning experiences, quiz results, and key observations are related to {request.userInput}? "
            f"Please provide insights about what the user has learned, struggled with, and any patterns "
            f"in their learning performance related to this topic that would help personalize the lesson."
        )
        
        try:
            answer = await query_fastino(request.user_id, question, use_cache=False)
            
            if answer:
                logger.info(f"✅ Retrieved answer from Fastino for lesson generation")
                logger.info(f"📝 Fastino answer: {answer[:300]}...")
                
                # Enhance prompt with Fastino context
                enhanced_prompt = f"{request.userInput}\n\nRelevant past learning context:\n{answer}"
                logger.info(f"📝 Enhanced prompt with Fastino context")
            else:
                logger.info("ℹ️  No answer retrieved from Fastino, using original prompt")
        except Exception as e:
            logger.warning(f"⚠️  Failed to query Fastino for lesson context: {e}. Continuing with original prompt.")
    else:
        logger.info("ℹ️  No user_id provided, skipping Fastino operations")
    
    # Validate environment variables
    if not AIRIA_API_KEY or not AIRIA_API_URL or not AIRIA_USER_ID:
        logger.error("❌ Missing API configuration in environment variables")
        return JSONResponse(
            status_code=500,
            content={"error": "Server configuration error: Missing API credentials"},
            headers={"Access-Control-Allow-Origin": "*"}
        )
    
    # Prepare payload for Airia.ai API (use enhanced prompt with chunks)
    payload = {
        "userId": AIRIA_USER_ID,
        "userInput": enhanced_prompt,
        "asyncOutput": False
    }
    
    headers = {
        "X-API-KEY": AIRIA_API_KEY,
        "Content-Type": "application/json"
    }
    
    logger.info(f"📡 Calling Airia.ai API: {AIRIA_API_URL}")
    logger.info(f"📦 Airia.ai Payload (userId is AIRIA_USER_ID from backend env): {json.dumps(payload)}")
    if request.user_id:
        logger.info(f"👤 Fastino user_id used for personalization: {request.user_id}")
    
    try:
        # Call Airia.ai API
        # Use a longer timeout since the API might take time to process (asyncOutput: false can be slow)
        # Also use data=json.dumps() format to match the example request
        timeout = httpx.Timeout(300.0, connect=30.0)  # 5 minutes total, 30s connect
        
        async with httpx.AsyncClient(timeout=timeout) as client:
            # Convert payload to JSON string (matching the example request format)
            payload_json = json.dumps(payload)
            
            logger.info(f"🚀 Sending request with payload length: {len(payload_json)} bytes")
            
            response = await client.post(
                AIRIA_API_URL,
                headers=headers,
                content=payload_json  # Use content= with JSON string (matches requests.data)
            )
            
            logger.info(f"📡 API Response Status: {response.status_code}")
            logger.info(f"📡 API Response Headers: {dict(response.headers)}")
            
            # Log the raw response for debugging
            raw_response_text = response.text
            logger.info("=" * 80)
            logger.info("📥 Airia.ai Lesson Generation Raw Response:")
            logger.info("=" * 80)
            logger.info(f"Response length: {len(raw_response_text)} chars")
            # Log full response (it might be large, but we need to see it)
            if len(raw_response_text) > 5000:
                logger.info(f"First 2500 chars:\n{raw_response_text[:2500]}")
                logger.info("...")
                logger.info(f"Last 2500 chars:\n{raw_response_text[-2500:]}")
            else:
                logger.info(raw_response_text)
            logger.info("=" * 80)
            
            if not response.is_success:
                error_text = response.text
                logger.error(f"❌ API Error Response: {error_text}")
                return JSONResponse(
                    status_code=response.status_code,
                    content={"error": f"Airia.ai API error: {response.status_code} {response.reason_phrase}. {error_text[:200]}"},
                    headers={"Access-Control-Allow-Origin": "*"}
                )
            
            # Parse response
            try:
                data = response.json()
                logger.info("=" * 80)
                logger.info("📋 Parsed Airia.ai Lesson Generation Response:")
                logger.info("=" * 80)
                # Log full parsed response for debugging
                full_parsed = json.dumps(data, indent=2)
                if len(full_parsed) > 5000:
                    logger.info(f"First 2500 chars:\n{full_parsed[:2500]}")
                    logger.info("...")
                    logger.info(f"Last 2500 chars:\n{full_parsed[-2500:]}")
                else:
                    logger.info(full_parsed)
                logger.info("=" * 80)
                logger.info(f"✅ API Response received. Result count: {len(data.get('result', []))}")
            except json.JSONDecodeError as e:
                logger.error(f"❌ Failed to parse response as JSON: {e}")
                logger.error(f"   Raw response length: {len(raw_response_text)} chars")
                logger.error(f"   Raw response (first 2000 chars): {raw_response_text[:2000]}")
                logger.error(f"   Raw response (last 500 chars): {raw_response_text[-500:] if len(raw_response_text) > 500 else raw_response_text}")
                return JSONResponse(
                    status_code=500,
                    content={"error": f"Failed to parse API response as JSON: {str(e)}"},
                    headers={"Access-Control-Allow-Origin": "*"}
                )
            
            # Validate response structure
            if not data.get("result") or not isinstance(data["result"], list) or len(data["result"]) < 2:
                logger.error("❌ Invalid API response: missing or incomplete result array")
                logger.error(f"   Response keys: {list(data.keys())}")
                logger.error(f"   Result type: {type(data.get('result'))}, Length: {len(data.get('result', []))}")
                return JSONResponse(
                    status_code=500,
                    content={"error": "Invalid API response: missing or incomplete result array"},
                    headers={"Access-Control-Allow-Origin": "*"}
                )
            
            # ===== STEP 1: Parse both result[0] and result[1] outputs =====
            logger.info("🔍 Starting dynamic detection of audio and content results...")
            
            result0 = data["result"][0]
            result1 = data["result"][1]
            
            logger.info(f"📦 Result[0]: stepType={result0.get('stepType')}, output_type={type(result0.get('output'))}")
            logger.info(f"📦 Result[1]: stepType={result1.get('stepType')}, output_type={type(result1.get('output'))}")
            
            # Helper function to parse output (handles both JSON string and dict)
            def parse_output(output_value, result_index):
                if not output_value:
                    raise ValueError(f"Missing output in result[{result_index}]")
                
                if isinstance(output_value, str):
                    try:
                        parsed = json.loads(output_value)
                        logger.info(f"✅ Parsed result[{result_index}].output JSON")
                        logger.info(f"   Keys in parsed result[{result_index}]: {list(parsed.keys())}")
                        return parsed
                    except json.JSONDecodeError as e:
                        logger.error(f"❌ JSON Parse Error for result[{result_index}].output: {e}")
                        logger.error(f"❌ Raw output string (first 500 chars): {output_value[:500]}")
                        raise ValueError(f"Failed to parse result[{result_index}].output as JSON: {str(e)}")
                else:
                    logger.info(f"✅ result[{result_index}].output is already a dict/object")
                    logger.info(f"   Keys in result[{result_index}]: {list(output_value.keys()) if isinstance(output_value, dict) else 'N/A'}")
                    return output_value
            
            # Parse both outputs
            try:
                parsed_result0 = parse_output(result0.get("output"), 0)
                parsed_result1 = parse_output(result1.get("output"), 1)
            except ValueError as e:
                return JSONResponse(
                    status_code=500,
                    content={"error": str(e)},
                    headers={"Access-Control-Allow-Origin": "*"}
                )
            
            # Extract segments from both results
            segments0 = parsed_result0.get("segments", [])
            segments1 = parsed_result1.get("segments", [])
            
            # Validate segments arrays
            for segs, idx in [(segments0, 0), (segments1, 1)]:
                if not isinstance(segs, list):
                    logger.error(f"❌ Invalid API response: result[{idx}].output.segments is not a list")
                    return JSONResponse(
                        status_code=500,
                        content={"error": f"Invalid API response: result[{idx}].output.segments is not a list"},
                        headers={"Access-Control-Allow-Origin": "*"}
                    )
                if len(segs) == 0:
                    logger.error(f"❌ Invalid API response: result[{idx}].output.segments is empty")
                    return JSONResponse(
                        status_code=500,
                        content={"error": f"Invalid API response: result[{idx}].output.segments is empty"},
                        headers={"Access-Control-Allow-Origin": "*"}
                    )
            
            logger.info(f"📊 Found {len(segments0)} segments in result[0].output")
            logger.info(f"📊 Found {len(segments1)} segments in result[1].output")
            
            # ===== STEP 2: Detect which result contains audio_base64 =====
            logger.info("🔍 Detecting which result contains audio_base64...")
            
            def has_audio_base64(segments):
                """Check if segments contain audio_base64 field"""
                for seg in segments[:5]:  # Check first 5 segments for efficiency
                    if seg.get("audio_base64"):
                        return True
                return False
            
            result0_has_audio = has_audio_base64(segments0)
            result1_has_audio = has_audio_base64(segments1)
            
            logger.info(f"   Result[0] has audio_base64: {result0_has_audio}")
            logger.info(f"   Result[1] has audio_base64: {result1_has_audio}")
            
            # Determine which result is audio and which is content
            if result0_has_audio and not result1_has_audio:
                audio_result_index = 0
                content_result_index = 1
                audio_segments = segments0
                content_segments = segments1
                audio_parsed = parsed_result0
                content_parsed = parsed_result1
                logger.info("✅ DETECTED: Result[0] contains audio_base64, Result[1] contains narration/image_url")
            elif result1_has_audio and not result0_has_audio:
                audio_result_index = 1
                content_result_index = 0
                audio_segments = segments1
                content_segments = segments0
                audio_parsed = parsed_result1
                content_parsed = parsed_result0
                logger.info("✅ DETECTED: Result[1] contains audio_base64, Result[0] contains narration/image_url")
            elif result0_has_audio and result1_has_audio:
                # Both have audio - this shouldn't happen, but use first one
                logger.warning("⚠️  Both results contain audio_base64! Using result[0] for audio.")
                audio_result_index = 0
                content_result_index = 1
                audio_segments = segments0
                content_segments = segments1
                audio_parsed = parsed_result0
                content_parsed = parsed_result1
            else:
                # Neither has audio - error
                logger.error("❌ Neither result contains audio_base64!")
                return JSONResponse(
                    status_code=500,
                    content={"error": "Invalid API response: neither result contains audio_base64"},
                    headers={"Access-Control-Allow-Origin": "*"}
                )
            
            # ===== STEP 3: Map segments from audio_result =====
            logger.info(f"📦 Mapping audio segments from result[{audio_result_index}]...")
            audio_segments_map = {}
            
            for seg in audio_segments:
                segment_id = seg.get("segment_id")
                if segment_id is None:
                    logger.warning(f"⚠️  Skipping audio segment with no segment_id")
                    continue
                
                audio_base64 = seg.get("audio_base64")
                if not audio_base64:
                    logger.warning(f"⚠️  Segment {segment_id} in result[{audio_result_index}] has no audio_base64")
                    continue
                
                # Handle both string and list (chunks) formats
                if isinstance(audio_base64, str):
                    audio_len = len(audio_base64)
                    logger.debug(f"   Segment {segment_id}: audio_base64 length={audio_len:,} chars")
                elif isinstance(audio_base64, list):
                    logger.info(f"   📦 Segment {segment_id}: audio_base64 is a list with {len(audio_base64)} chunks - combining")
                    # Combine chunks: decode each, combine binary, re-encode
                    combined_binary = b""
                    for chunk in audio_base64:
                        combined_binary += base64.b64decode(str(chunk))
                    audio_base64 = base64.b64encode(combined_binary).decode("utf-8")
                    audio_len = len(audio_base64)
                else:
                    logger.warning(f"   ⚠️  Segment {segment_id}: audio_base64 has unexpected type: {type(audio_base64)}")
                    continue
                
                audio_segments_map[segment_id] = {
                    "audio_base64": audio_base64,
                    "audio_length": audio_len
                }
            
            logger.info(f"✅ Mapped {len(audio_segments_map)} audio segments from result[{audio_result_index}]")
            audio_segment_ids = sorted(audio_segments_map.keys())
            logger.info(f"🔍 Audio segment IDs: {audio_segment_ids}")
            
            # ===== STEP 4: Map segments from content_result =====
            logger.info(f"📦 Mapping content segments from result[{content_result_index}]...")
            content_segments_map = {}
            
            for seg in content_segments:
                segment_id = seg.get("segment_id")
                if segment_id is None:
                    logger.warning(f"⚠️  Skipping content segment with no segment_id")
                    continue
                
                # Extract narration and image_url from content result
                narration = seg.get("narration", "")
                image_url = seg.get("image_url")
                duration = seg.get("duration")
                
                content_segments_map[segment_id] = {
                    "narration": narration,
                    "image_url": image_url,
                    "duration": duration
                }
            
            logger.info(f"✅ Mapped {len(content_segments_map)} content segments from result[{content_result_index}]")
            content_segment_ids = sorted(content_segments_map.keys())
            logger.info(f"🔍 Content segment IDs: {content_segment_ids}")
            
            # ===== STEP 5: Combine segments by matching segment_id =====
            logger.info("🔗 Combining segments by matching segment_id...")
            
            # Get all unique segment IDs from both results
            all_segment_ids = set(audio_segment_ids + content_segment_ids)
            logger.info(f"   Total unique segment IDs: {sorted(all_segment_ids)}")
            
            combined_segments = []
            
            for segment_id in sorted(all_segment_ids):
                audio_data = audio_segments_map.get(segment_id)
                content_data = content_segments_map.get(segment_id)
                
                if not audio_data:
                    logger.warning(f"⚠️  Segment {segment_id}: missing audio in result[{audio_result_index}], skipping")
                    continue
                
                if not content_data:
                    logger.warning(f"⚠️  Segment {segment_id}: missing narration/image in result[{content_result_index}], skipping")
                    continue
                
                # Extract audio_base64
                audio_base64 = audio_data["audio_base64"]
                audio_len = audio_data["audio_length"]
                
                # Combine data
                combined_segment = {
                    "segment_id": segment_id,
                    "audioBase64": audio_base64,
                    "imageUrl": content_data.get("image_url"),
                    "narration": content_data.get("narration", ""),
                    "duration": content_data.get("duration"),
                }
                
                combined_segments.append(combined_segment)
                
                logger.debug(f"   Segment {segment_id}: "
                           f"narration length={len(combined_segment['narration'])}, "
                           f"has image={bool(combined_segment['imageUrl'])}, "
                           f"audio length={audio_len:,} chars")
            
            # Sort by segment_id
            combined_segments.sort(key=lambda x: x["segment_id"])
            
            logger.info(f"🔗 Combined {len(combined_segments)} segments")
            
            # Validate combined segments
            valid_segments = []
            for seg in combined_segments:
                if seg.get("audioBase64") and seg.get("segment_id") is not None:
                    valid_segments.append(seg)
                else:
                    logger.warning(f"⚠️  Skipping invalid segment: {seg.get('segment_id')}")
            
            if len(valid_segments) == 0:
                logger.error("❌ No valid segments after combining")
                return JSONResponse(
                    status_code=500,
                    content={"error": "No valid segments could be created from API response"},
                    headers={"Access-Control-Allow-Origin": "*"}
                )
            
            # Get topic from either result, or use user input
            topic = (
                audio_parsed.get("topic") 
                or content_parsed.get("topic") 
                or request.userInput
            )
            
            logger.info(f"🎓 Final Lesson Data:")
            logger.info(f"   Topic: {topic}")
            logger.info(f"   Valid segments: {len(valid_segments)}")
            logger.info(f"   Segment IDs: {[s['segment_id'] for s in valid_segments]}")
            
            # Return lesson data as JSON
            lesson_data = {
                "topic": topic,
                "segments": valid_segments
            }
            
            logger.info(f"✅ Returning lesson data with {len(valid_segments)} segments")
            return lesson_data
            
    except httpx.TimeoutException as e:
        logger.error(f"❌ API Request Timeout: {e}")
        return JSONResponse(
            status_code=504,
            content={"error": "Request to Airia.ai API timed out. Please try again."},
            headers={"Access-Control-Allow-Origin": "*"}
        )
    except httpx.RequestError as e:
        logger.error(f"❌ Network Error: {e}")
        return JSONResponse(
            status_code=503,
            content={"error": f"Failed to connect to Airia.ai API: {str(e)}"},
            headers={"Access-Control-Allow-Origin": "*"}
        )
    except HTTPException as e:
        # Return JSONResponse with CORS headers for HTTPExceptions
        return JSONResponse(
            status_code=e.status_code,
            content={"error": e.detail},
            headers={"Access-Control-Allow-Origin": "*"}
        )
    except Exception as e:
        logger.error(f"❌ Unexpected Error: {type(e).__name__}: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"error": f"Internal server error: {str(e)}"},
            headers={"Access-Control-Allow-Origin": "*"}
        )


@app.post("/generateQuiz")
async def generate_quiz(request: GenerateQuizRequest):
    """
    Generate a quiz by calling Airia.ai API
    
    Args:
        request: GenerateQuizRequest with userInput (lesson prompt) and optional user_id
        
    Returns:
        Quiz data with questions
        
    Raises:
        HTTPException: If API call fails or response is invalid
    """
    logger.info(f"🚀 Received quiz generation request for lesson prompt: {request.userInput}")
    if request.user_id:
        logger.info(f"👤 Fastino user_id from frontend: {request.user_id}")
    else:
        logger.info("👤 No Fastino user_id provided in request")
    
    # ===== STEP 1: Query Fastino for user context if user_id is provided =====
    user_pref_context = ""
    
    if request.user_id:
        logger.info(f"🔍 Querying Fastino for user context for quiz generation for user: {request.user_id}")
        
        # Create a question that helps Fastino understand what context we need about the topic
        # Note: Do not put userInput in quotes as Fastino cannot read it properly
        question = (
            f"answer in 4-5 lines : What were the key observations from previous quizzes related to {request.userInput} "
            f"Please provide detailed insights about what the user struggled with, any patterns in their learning performance related to this topic."
        )
        
        try:
            answer = await query_fastino(request.user_id, question, use_cache=False)
            
            if answer:
                logger.info(f"✅ Retrieved answer from Fastino for quiz generation")
                logger.info(f"📝 Fastino answer (first 500 chars): {answer[:500]}...")
                
                # Extract content after "Key Observations & Learning Patterns\n\n###"
                pattern = "Key Observations & Learning Patterns\n\n###"
                pattern_index = answer.find(pattern)
                
                if pattern_index != -1:
                    # Extract everything after the pattern
                    user_pref_context = answer[pattern_index + len(pattern):].strip()
                    logger.info(f"📝 Found pattern, extracted content length: {len(user_pref_context)} chars")
                    logger.info(f"📝 Extracted content (first 300 chars): {user_pref_context[:300]}...")
                else:
                    logger.warning("⚠️  Pattern 'Key Observations & Learning Patterns\\n\\n###' not found in Fastino answer")
                    logger.warning(f"   Answer preview: {answer[:500]}")
                    # Fallback: use the full answer if pattern not found
                    user_pref_context = answer.strip()
                    logger.info("ℹ️  Using full answer as fallback")
            else:
                logger.info("ℹ️  No answer retrieved from Fastino, using empty user context")
        except Exception as e:
            logger.warning(f"⚠️  Failed to query Fastino for quiz context: {e}. Continuing with empty user context.")
    else:
        logger.info("ℹ️  No user_id provided, skipping Fastino query for quiz")
    
    # Validate environment variables
    if not AIRIA_API_KEY or not AIRIA_QUIZ_API_URL or not AIRIA_USER_ID:
        logger.error("❌ Missing Airia.ai API credentials")
        return JSONResponse(
            status_code=500,
            content={"error": "Server configuration error: Missing API credentials"},
            headers={"Access-Control-Allow-Origin": "*"}
        )
    
    # Prepare payload for Airia.ai Quiz API as JSON: {user_pref_context: "...", user_input: "..."}
    quiz_payload_data = {
        "user_pref_context": user_pref_context,
        "user_input": request.userInput
    }
    
    # Convert to JSON string for userInput field
    enhanced_prompt = json.dumps(quiz_payload_data)
    
    payload = {
        "userInput": enhanced_prompt,
        "asyncOutput": False
    }
    
    logger.info(f"📝 Quiz payload format: {enhanced_prompt}")
    
    headers = {
        "X-API-KEY": AIRIA_API_KEY,
        "Content-Type": "application/json"
    }
    
    logger.info(f"📡 Calling Airia.ai Quiz API: {AIRIA_QUIZ_API_URL}")
    logger.info(f"📦 Airia.ai Quiz Payload: {json.dumps(payload)}")
    
    try:
        # Call Airia.ai API
        timeout = httpx.Timeout(300.0, connect=30.0)  # 5 minutes total, 30s connect
        
        async with httpx.AsyncClient(timeout=timeout) as client:
            # Convert payload to JSON string
            payload_json = json.dumps(payload)
            
            logger.info(f"🚀 Sending quiz request with payload length: {len(payload_json)} bytes")
            
            response = await client.post(
                AIRIA_QUIZ_API_URL,
                headers=headers,
                content=payload_json
            )
            
            logger.info(f"📡 Quiz API Response Status: {response.status_code}")
            
            if not response.is_success:
                error_text = response.text
                logger.error(f"❌ Quiz API Error Response: {error_text}")
                return JSONResponse(
                    status_code=response.status_code,
                    content={"error": f"Airia.ai Quiz API error: {response.status_code} {response.reason_phrase}. {error_text[:200]}"},
                    headers={"Access-Control-Allow-Origin": "*"}
                )
            
            # Log the full raw response
            raw_response_text = response.text
            logger.info("=" * 80)
            logger.info("📋 FULL QUIZ API RAW RESPONSE:")
            logger.info("=" * 80)
            logger.info(raw_response_text)
            logger.info("=" * 80)
            
            # Parse response
            try:
                data = response.json()
                logger.info(f"✅ Quiz API Response parsed successfully. Result count: {len(data.get('result', []))}")
                
                # Log the full parsed response structure
                logger.info("=" * 80)
                logger.info("📋 FULL QUIZ API PARSED RESPONSE:")
                logger.info("=" * 80)
                logger.info(json.dumps(data, indent=2))
                logger.info("=" * 80)
                
                # Check if result exists (quiz API returns result as a string)
                result_value = data.get("result")
                
                if not result_value:
                    logger.warning("⚠️  No result found in response")
                    return JSONResponse(
                        status_code=500,
                        content={"error": "No result found in API response"},
                        headers={"Access-Control-Allow-Origin": "*"}
                    )
                
                logger.info(f"📦 Result type: {type(result_value)}")
                
                # Parse result - it's a JSON string wrapped in markdown code blocks
                quiz_json_str = None
                
                if isinstance(result_value, str):
                    logger.info("🔍 Result is a string, extracting JSON from markdown code blocks...")
                    # Extract JSON from markdown code blocks (```json ... ```)
                    json_match = re.search(r'```json\s*\n(.*?)\n```', result_value, re.DOTALL)
                    if json_match:
                        quiz_json_str = json_match.group(1).strip()
                        logger.info("✅ Extracted JSON from markdown code blocks")
                    else:
                        # Try without markdown wrapper - might be plain JSON string
                        quiz_json_str = result_value.strip()
                        logger.info("⚠️  No markdown code blocks found, using result as-is")
                else:
                    # Result might already be a dict
                    quiz_json_str = json.dumps(result_value)
                
                # Parse the JSON string
                try:
                    quiz_data = json.loads(quiz_json_str)
                    logger.info("✅ Successfully parsed quiz JSON")
                    logger.info(f"📋 Quiz data keys: {list(quiz_data.keys()) if isinstance(quiz_data, dict) else 'N/A'}")
                except json.JSONDecodeError as e:
                    logger.error(f"❌ Failed to parse quiz JSON: {e}")
                    logger.error(f"   First 500 chars: {quiz_json_str[:500] if quiz_json_str else 'None'}")
                    return JSONResponse(
                        status_code=500,
                        content={"error": f"Failed to parse quiz JSON: {str(e)}"},
                        headers={"Access-Control-Allow-Origin": "*"}
                    )
                
                # Extract quiz array
                quiz_array = quiz_data.get("quiz")
                if not quiz_array or not isinstance(quiz_array, list):
                    logger.error(f"❌ No 'quiz' array found in parsed data. Keys: {list(quiz_data.keys()) if isinstance(quiz_data, dict) else 'N/A'}")
                    return JSONResponse(
                        status_code=500,
                        content={"error": "No 'quiz' array found in response"},
                        headers={"Access-Control-Allow-Origin": "*"}
                    )
                
                logger.info(f"✅ Found {len(quiz_array)} questions in quiz")
                
                # Convert quiz questions to frontend format
                formatted_questions = []
                for idx, question_data in enumerate(quiz_array):
                    question_text = question_data.get("question", "")
                    options = question_data.get("options", [])
                    correct_answer_text = question_data.get("correct_answer", "")
                    
                    # Find the index of correct answer in options
                    correct_answer_index = -1
                    try:
                        correct_answer_index = options.index(correct_answer_text)
                    except ValueError:
                        logger.warning(f"⚠️  Question {idx + 1}: Correct answer '{correct_answer_text}' not found in options")
                        # Try case-insensitive match
                        for i, opt in enumerate(options):
                            if opt.lower().strip() == correct_answer_text.lower().strip():
                                correct_answer_index = i
                                break
                    
                    if correct_answer_index == -1:
                        logger.error(f"❌ Question {idx + 1}: Could not find correct answer index")
                        continue
                    
                    formatted_questions.append({
                        "id": idx + 1,
                        "question": question_text,
                        "options": options,
                        "correctAnswer": correct_answer_index
                    })
                
                if len(formatted_questions) == 0:
                    logger.error("❌ No valid questions could be formatted")
                    return JSONResponse(
                        status_code=500,
                        content={"error": "No valid questions found in quiz"},
                        headers={"Access-Control-Allow-Origin": "*"}
                    )
                
                logger.info(f"✅ Formatted {len(formatted_questions)} quiz questions")
                
                # Return formatted quiz
                return JSONResponse(
                    status_code=200,
                    content={
                        "questions": formatted_questions
                    },
                    headers={"Access-Control-Allow-Origin": "*"}
                )
                    
            except json.JSONDecodeError as e:
                logger.error(f"❌ Failed to parse response as JSON: {e}")
                logger.error(f"   First 500 chars of response: {raw_response_text[:500]}")
                return JSONResponse(
                    status_code=500,
                    content={"error": f"Failed to parse API response as JSON: {str(e)}", "raw_response_preview": raw_response_text[:500]},
                    headers={"Access-Control-Allow-Origin": "*"}
                )
                
    except httpx.TimeoutException as e:
        logger.error(f"❌ Quiz API Request Timeout: {e}")
        return JSONResponse(
            status_code=504,
            content={"error": "Request to Airia.ai Quiz API timed out. Please try again."},
            headers={"Access-Control-Allow-Origin": "*"}
        )
    except httpx.RequestError as e:
        logger.error(f"❌ Quiz Network Error: {e}")
        return JSONResponse(
            status_code=503,
            content={"error": f"Failed to connect to Airia.ai Quiz API: {str(e)}"},
            headers={"Access-Control-Allow-Origin": "*"}
        )
    except Exception as e:
        logger.error(f"❌ Unexpected Quiz Error: {type(e).__name__}: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"error": f"Internal server error: {str(e)}"},
            headers={"Access-Control-Allow-Origin": "*"}
        )


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("BACKEND_PORT", 8000))
    host = os.getenv("BACKEND_HOST", "0.0.0.0")
    uvicorn.run(app, host=host, port=port, reload=True)

