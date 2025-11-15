// Fastino AI API Client - Frontend
// Calls backend Fastino endpoints

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || "http://localhost:8000";

export interface ConversationMessage {
  role: "system" | "user" | "assistant";
  content: string;
}

export interface Chunk {
  chunk_id: string;
  excerpt: string;
  score: number;
}

export interface QuizIngestData {
  topic: string;
  question: string;
  answer: string; // correct answer
  user_answer: string;
  verdict: "correct" | "wrong";
}

/**
 * Register a user with Fastino AI
 * @param email - User's email address
 * @param name - User's name
 * @param age - User's age
 * @param tone - User's preferred learning tone
 * @returns user_id if successful, null on failure
 */
export async function registerUser(
  email: string,
  name: string,
  age: number,
  tone: string
): Promise<string | null> {
  const url = `${BACKEND_URL}/fastino/register`;
  
  try {
    const response = await fetch(url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        email,
        name,
        age,
        tone,
      }),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ error: "Unknown error" }));
      console.warn("⚠️  Fastino registration failed:", errorData);
      return null;
    }

    const data = await response.json();
    const user_id = data.user_id;
    console.log("✅ User registered with Fastino:", user_id);
    return user_id;
  } catch (error) {
    console.warn("⚠️  Fastino registration error:", error);
    return null;
  }
}

/**
 * Ingest lesson data to Fastino AI
 * @param user_id - Fastino user ID
 * @param topic - Lesson topic
 * @returns true if successful, false on failure
 */
export async function ingestLesson(user_id: string, topic: string): Promise<boolean> {
  const url = `${BACKEND_URL}/fastino/ingest/lesson`;
  
  try {
    const response = await fetch(url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        user_id,
        topic,
      }),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ error: "Unknown error" }));
      console.warn("⚠️  Fastino lesson ingestion failed:", errorData);
      return false;
    }

    const data = await response.json();
    console.log("✅ Lesson ingested to Fastino:", data);
    return data.success === true;
  } catch (error) {
    console.warn("⚠️  Fastino lesson ingestion error:", error);
    return false;
  }
}

/**
 * Ingest quiz data to Fastino AI
 * @param user_id - Fastino user ID
 * @param quizData - Quiz data to ingest
 * @returns true if successful, false on failure
 */
export async function ingestQuiz(user_id: string, quizData: QuizIngestData): Promise<boolean> {
  const url = `${BACKEND_URL}/fastino/ingest/quiz`;
  
  try {
    const response = await fetch(url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        user_id,
        topic: quizData.topic,
        question: quizData.question,
        answer: quizData.answer,
        user_answer: quizData.user_answer,
        verdict: quizData.verdict,
      }),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ error: "Unknown error" }));
      console.warn("⚠️  Fastino quiz ingestion failed:", errorData);
      return false;
    }

    const data = await response.json();
    console.log("✅ Quiz ingested to Fastino:", data);
    return data.success === true;
  } catch (error) {
    console.warn("⚠️  Fastino quiz ingestion error:", error);
    return false;
  }
}

/**
 * Retrieve personalized chunks from Fastino AI
 * @param user_id - Fastino user ID
 * @param history - Conversation history array with role and content
 * @param top_k - Number of chunks to retrieve (default: 5)
 * @returns Array of chunks, empty array on failure
 */
export async function getChunks(
  user_id: string,
  history: ConversationMessage[],
  top_k: number = 5
): Promise<Chunk[]> {
  const url = `${BACKEND_URL}/fastino/chunks`;
  
  try {
    const response = await fetch(url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        user_id,
        history,
        top_k,
      }),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ error: "Unknown error" }));
      console.warn("⚠️  Fastino chunks retrieval failed:", errorData);
      return [];
    }

    const data = await response.json();
    return data.results || [];
  } catch (error) {
    console.warn("⚠️  Fastino chunks retrieval error:", error);
    return [];
  }
}

