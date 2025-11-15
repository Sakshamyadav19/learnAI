// API Service Module - Calls backend API for lesson generation
import { getFastinoUserId } from "./auth";

export interface LessonSegment {
  segment_id: number;
  imageUrl: string | null;
  audioUrl?: string; // Will be converted from audioBase64
  audioBase64?: string; // Base64 audio data from backend
  narration: string; // Narration text from backend (replaces prompt)
  duration?: number; // Optional duration in seconds from backend
}

export interface LessonData {
  topic: string;
  segments: LessonSegment[];
}

/**
 * Generates a lesson by calling the backend API
 * @param userPrompt - The user's input topic/prompt
 * @returns Promise resolving to parsed lesson data
 * @throws Error if API call fails or response is invalid
 */
export async function generateLesson(userPrompt: string): Promise<LessonData> {
  // Get backend URL from environment or use default
  const backendUrl = import.meta.env.VITE_BACKEND_URL || "http://localhost:8000";
  const apiUrl = `${backendUrl}/generateLesson`;

  // Get Fastino user_id if available
  const user_id = getFastinoUserId();
  
  console.log("🔍 Checking Fastino user_id:", {
    found: !!user_id,
    user_id: user_id || "not found",
    localStorageKey: "learnai_fastino_user_id"
  });

  const payload: {
    userInput: string;
    user_id?: string;
  } = {
    userInput: userPrompt,
  };

  if (user_id) {
    payload.user_id = user_id;
    console.log("✅ Including Fastino user_id in request:", user_id);
  } else {
    console.warn("⚠️  No Fastino user_id found in localStorage");
  }

  try {
    console.log("🚀 Frontend API Request:", {
      url: apiUrl,
      method: "POST",
      payload,
    });

    const response = await fetch(apiUrl, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    });

    console.log("📡 Backend API Response Status:", {
      status: response.status,
      statusText: response.statusText,
      ok: response.ok,
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ error: "Unknown error" }));
      const errorMessage = errorData.error || errorData.detail || `HTTP ${response.status}: ${response.statusText}`;
      console.error("❌ Backend API Error:", errorMessage);
      throw new Error(errorMessage);
    }

    const data: LessonData = await response.json();
    console.log("✅ Backend API Response Data:", {
      topic: data.topic,
      segmentCount: data.segments?.length || 0,
      segments: data.segments?.map((s) => ({
        segment_id: s.segment_id,
        hasImage: !!s.imageUrl,
        hasAudio: !!s.audioBase64,
        audioBase64Length: s.audioBase64?.length || 0,
        narrationPreview: s.narration?.substring(0, 50) || "empty",
      })),
    });

    // Validate response structure
    if (!data.topic || !data.segments || !Array.isArray(data.segments)) {
      console.error("❌ Invalid backend response structure:", data);
      throw new Error("Invalid response from backend: missing topic or segments");
    }

    // Ensure all segments have audioBase64
    const validatedSegments = data.segments.map((segment) => ({
      ...segment,
      audioBase64: segment.audioBase64 || "",
    }));

    console.log("🎓 Final Lesson Data:", {
      topic: data.topic,
      segmentCount: validatedSegments.length,
    });

    return {
      topic: data.topic,
      segments: validatedSegments,
    };
  } catch (error) {
    console.error("❌ Frontend API Call Error:", error);
    if (error instanceof Error) {
      throw error;
    }
    throw new Error(`Unknown error occurred: ${error}`);
  }
}

export interface QuizQuestion {
  id: number;
  question: string;
  options: string[];
  correctAnswer: number; // Index of correct answer in options array
}

export interface QuizData {
  questions: QuizQuestion[];
}

/**
 * Generates a quiz by calling the backend API
 * @param userPrompt - The user's lesson prompt/topic
 * @returns Promise resolving to quiz data with questions
 * @throws Error if API call fails or response is invalid
 */
export async function generateQuiz(userPrompt: string): Promise<QuizData> {
  // Get backend URL from environment or use default
  const backendUrl = import.meta.env.VITE_BACKEND_URL || "http://localhost:8000";
  const apiUrl = `${backendUrl}/generateQuiz`;

  // Get Fastino user_id if available
  const user_id = getFastinoUserId();
  
  console.log("🔍 Checking Fastino user_id for quiz generation:", {
    found: !!user_id,
    user_id: user_id || "not found",
    localStorageKey: "learnai_fastino_user_id"
  });

  const payload: {
    userInput: string;
    user_id?: string;
  } = {
    userInput: userPrompt,
  };

  if (user_id) {
    payload.user_id = user_id;
    console.log("✅ Including Fastino user_id in quiz request:", user_id);
  } else {
    console.warn("⚠️  No Fastino user_id found in localStorage for quiz generation");
  }

  try {
    console.log("🚀 Frontend Quiz API Request:", {
      url: apiUrl,
      method: "POST",
      payload,
    });

    const response = await fetch(apiUrl, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    });

    console.log("📡 Backend Quiz API Response Status:", {
      status: response.status,
      statusText: response.statusText,
      ok: response.ok,
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ error: "Unknown error" }));
      const errorMessage = errorData.error || errorData.detail || `HTTP ${response.status}: ${response.statusText}`;
      console.error("❌ Backend Quiz API Error:", errorMessage);
      throw new Error(errorMessage);
    }

    const data: QuizData = await response.json();
    console.log("✅ Backend Quiz API Response Data:", {
      questionCount: data.questions?.length || 0,
      questions: data.questions?.map(q => ({
        id: q.id,
        question: q.question.substring(0, 50) + "...",
        optionsCount: q.options.length,
        correctAnswer: q.correctAnswer
      }))
    });

    // Validate response structure
    if (!data.questions || !Array.isArray(data.questions) || data.questions.length === 0) {
      console.error("❌ Invalid quiz response structure:", data);
      throw new Error("Invalid response from backend: missing or empty questions array");
    }

    return data;
  } catch (error) {
    console.error("❌ Frontend Quiz API Call Error:", error);
    if (error instanceof Error) {
      throw error;
    }
    throw new Error(`Unknown error occurred: ${error}`);
  }
}
