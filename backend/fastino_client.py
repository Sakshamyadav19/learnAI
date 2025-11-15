"""
Fastino AI API Client
Handles all interactions with Fastino AI API
"""

import os
import json
import logging
import time
from datetime import datetime
from typing import Optional, Dict, List
import httpx
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)

# Fastino API configuration
FASTINO_API_KEY = "pio_sk_ny8hbA7sXh93U4QHr4v3n_17031467-4080-4cca-a7be-0896fec4bad1"
FASTINO_API_URL = os.getenv("FASTINO_API_URL", "https://api.fastino.ai")


async def register_user(email: str, name: str, age: int, tone: str) -> Optional[Dict]:
    """
    Register a user with Fastino AI
    
    Args:
        email: User's email address
        name: User's name
        age: User's age
        tone: User's preferred learning tone
        
    Returns:
        Dict with user_id if successful, None on failure
    """
    if not FASTINO_API_KEY:
        logger.warning("⚠️  FASTINO_API_KEY not configured")
        return None
    
    url = f"{FASTINO_API_URL}/register"
    headers = {
        "x-api-key": FASTINO_API_KEY,
        "Content-Type": "application/json"
    }
    payload = {
        "email": email,
        "traits": {
            "name": name,
            "age": age,
            "tone": tone
        }
    }
    
    # Log the payload being sent
    logger.info(f"📤 Registering user with Fastino")
    logger.info(f"📝 Email: {email}, Name: {name}, Age: {age}, Tone: {tone}")
    logger.info(f"📦 Payload: {json.dumps(payload, indent=2)}")
    
    # Log headers for debugging (mask API key)
    logger.info(f"📡 Fastino Register URL: {url}")
    logger.info(f"🔑 x-api-key header: {FASTINO_API_KEY[:20]}...{FASTINO_API_KEY[-10:] if len(FASTINO_API_KEY) > 30 else '***'}")
    
    try:
        async with httpx.AsyncClient(timeout=100.0) as client:
            response = await client.post(url, headers=headers, json=payload)
            
            if response.is_success:
                data = response.json()
                user_id = data.get("user_id")
                logger.info(f"✅ Successfully registered user with Fastino: {user_id}")
                return data
            else:
                logger.warning(f"⚠️  Fastino registration failed: {response.status_code} - {response.text}")
                return None
                
    except httpx.TimeoutException:
        logger.warning("⚠️  Fastino registration request timed out")
        return None
    except httpx.RequestError as e:
        logger.warning(f"⚠️  Fastino registration request error: {e}")
        return None
    except Exception as e:
        logger.warning(f"⚠️  Unexpected error during Fastino registration: {e}")
        return None


async def ingest_lesson(user_id: str, topic: str) -> bool:
    """
    Ingest lesson data to Fastino AI as a document
    
    Args:
        user_id: Fastino user ID
        topic: Lesson topic/prompt
        
    Returns:
        True if successful, False on failure
    """
    if not FASTINO_API_KEY:
        logger.warning("⚠️  FASTINO_API_KEY not configured")
        return False
    
    url = f"{FASTINO_API_URL}/ingest"
    headers = {
        "x-api-key": FASTINO_API_KEY,
        "Content-Type": "application/json"
    }
    
    # Generate unique doc_id
    doc_id = f"lesson_{int(time.time() * 1000)}"
    
    payload = {
        "user_id": user_id,
        "source": "learnai",
        "documents": [
            {
                "doc_id": doc_id,
                "kind": "lesson",
                "title": f"Lesson: {topic}",
                "created_at": datetime.utcnow().isoformat() + "Z",
                "content": topic,  # user lesson prompt
                "document_type": "lesson"
            }
        ],
        "options": {
            "dedupe": True
        }
    }
    
    # Log the payload and headers being sent (mask API key for security)
    logger.info(f"📤 Ingesting lesson for user {user_id}")
    logger.info(f"📝 Lesson prompt/topic: {topic}")
    logger.info(f"📡 Fastino API URL: {url}")
    logger.info(f"🔑 x-api-key header: {FASTINO_API_KEY[:20]}...{FASTINO_API_KEY[-10:] if len(FASTINO_API_KEY) > 30 else '***'}")
    logger.info(f"📦 Payload: {json.dumps(payload, indent=2)}")
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(url, headers=headers, json=payload)
            
            if response.is_success:
                logger.info(f"✅ Successfully ingested lesson data for user {user_id}")
                return True
            else:
                logger.warning(f"⚠️  Fastino lesson ingestion failed: {response.status_code} - {response.text}")
                return False
                
    except httpx.TimeoutException:
        logger.warning("⚠️  Fastino lesson ingestion request timed out")
        return False
    except httpx.RequestError as e:
        logger.warning(f"⚠️  Fastino lesson ingestion request error: {e}")
        return False
    except Exception as e:
        logger.warning(f"⚠️  Unexpected error during Fastino lesson ingestion: {e}")
        return False


async def ingest_quiz(user_id: str, topic: str, question: str, answer: str, user_answer: str, verdict: str) -> bool:
    """
    Ingest quiz data to Fastino AI as a document
    
    Args:
        user_id: Fastino user ID
        topic: Lesson topic
        question: Quiz question text
        answer: Correct answer text
        user_answer: User's answer text
        verdict: "correct" or "wrong"
        
    Returns:
        True if successful, False on failure
    """
    if not FASTINO_API_KEY:
        logger.warning("⚠️  FASTINO_API_KEY not configured")
        return False
    
    url = f"{FASTINO_API_URL}/ingest"
    headers = {
        "x-api-key": FASTINO_API_KEY,
        "Content-Type": "application/json"
    }
    
    # Generate unique doc_id
    doc_id = f"quiz_{int(time.time() * 1000)}"
    
    # Create content string with quiz information
    content = f"Quiz Question: {question}\nCorrect Answer: {answer}\nUser Answer: {user_answer}\nVerdict: {verdict}"
    
    payload = {
        "user_id": user_id,
        "source": "learnai",
        "documents": [
            {
                "doc_id": doc_id,
                "kind": "quiz",
                "title": f"Quiz: {topic} - {question[:50]}...",
                "created_at": datetime.utcnow().isoformat() + "Z",
                "content": content,
                "document_type": "quiz",
                "metadata": {
                    "topic": topic,
                    "question": question,
                    "correct_answer": answer,
                    "user_answer": user_answer,
                    "verdict": verdict
                }
            }
        ],
        "options": {
            "dedupe": True
        }
    }
    
    # Log the payload and headers being sent
    logger.info(f"📤 Ingesting quiz data for user {user_id}")
    logger.info(f"📝 Quiz topic: {topic}, Question: {question[:50]}...")
    logger.info(f"📡 Fastino API URL: {url}")
    logger.info(f"🔑 x-api-key header: {FASTINO_API_KEY[:20]}...{FASTINO_API_KEY[-10:] if len(FASTINO_API_KEY) > 30 else '***'}")
    logger.info(f"📦 Payload: {json.dumps(payload, indent=2)}")
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(url, headers=headers, json=payload)
            
            if response.is_success:
                logger.info(f"✅ Successfully ingested quiz data for user {user_id}")
                return True
            else:
                logger.warning(f"⚠️  Fastino quiz ingestion failed: {response.status_code} - {response.text}")
                return False
                
    except httpx.TimeoutException:
        logger.warning("⚠️  Fastino quiz ingestion request timed out")
        return False
    except httpx.RequestError as e:
        logger.warning(f"⚠️  Fastino quiz ingestion request error: {e}")
        return False
    except Exception as e:
        logger.warning(f"⚠️  Unexpected error during Fastino quiz ingestion: {e}")
        return False


async def query_fastino(user_id: str, question: str, use_cache: bool = False) -> Optional[str]:
    """
    Query Fastino AI for personalized context
    
    Args:
        user_id: Fastino user ID
        question: Question to ask Fastino about user's learning history/context
        use_cache: Whether to use cached results (default: False)
        
    Returns:
        Answer string from Fastino, None on failure
    """
    if not FASTINO_API_KEY:
        logger.warning("⚠️  FASTINO_API_KEY not configured")
        return None
    
    url = f"{FASTINO_API_URL}/query"
    headers = {
        "x-api-key": FASTINO_API_KEY,
        "Content-Type": "application/json"
    }
    payload = {
        "user_id": user_id,
        "question": question,
        "use_cache": use_cache
    }
    
    # Log the full payload and headers for debugging
    logger.info("=" * 80)
    logger.info("📤 Fastino Query Request:")
    logger.info("=" * 80)
    logger.info(f"📡 URL: {url}")
    logger.info(f"🔑 x-api-key header: {FASTINO_API_KEY[:20]}...{FASTINO_API_KEY[-10:] if len(FASTINO_API_KEY) > 30 else '***'}")
    logger.info(f"📦 Payload:")
    logger.info(json.dumps(payload, indent=2))
    logger.info("=" * 80)
    
    try:
        async with httpx.AsyncClient(timeout=100.0) as client:
            response = await client.post(url, headers=headers, json=payload)
            
            # Log the raw response
            raw_response_text = response.text
            logger.info("=" * 80)
            logger.info(f"📥 Fastino Query Response (Status: {response.status_code}):")
            logger.info("=" * 80)
            logger.info(raw_response_text)
            logger.info("=" * 80)
            
            if response.is_success:
                try:
                    data = response.json()
                    logger.info("=" * 80)
                    logger.info("📋 Parsed Fastino Query Response:")
                    logger.info("=" * 80)
                    logger.info(json.dumps(data, indent=2))
                    logger.info("=" * 80)
                    
                    # Fastino returns answer in "answer" field
                    answer = data.get("answer", "")
                    if answer:
                        logger.info(f"✅ Retrieved answer from Fastino for user {user_id}")
                        logger.info(f"📝 Answer: {answer[:200]}...")
                        return answer
                    else:
                        logger.warning("⚠️  No answer field in Fastino response")
                        return None
                except json.JSONDecodeError as e:
                    logger.error(f"❌ Failed to parse query response as JSON: {e}")
                    logger.error(f"   Raw response: {raw_response_text[:500]}")
                    return None
            else:
                logger.warning(f"⚠️  Fastino query failed: {response.status_code} - {raw_response_text}")
                return None
                
    except httpx.TimeoutException:
        logger.warning("⚠️  Fastino query request timed out")
        return None
    except httpx.RequestError as e:
        logger.warning(f"⚠️  Fastino query request error: {e}")
        return None
    except Exception as e:
        logger.warning(f"⚠️  Unexpected error during Fastino query: {e}")
        return None

