import { useState } from "react";
import { Lesson } from "@/pages/Home";
import VideoFrame from "./VideoFrame";
import LessonInput from "./LessonInput";
import TakeQuizButton from "./TakeQuizButton";
import QuizPanel, { QuizSubmissionData, QuizQuestion } from "./QuizPanel";
import { getFastinoUserId } from "@/lib/auth";
import { ingestQuiz, queryFastino } from "@/lib/fastino";
import { generateQuiz } from "@/lib/api";
import { toast } from "sonner";

interface MainAreaProps {
  lessons: Lesson[];
  onGenerateLesson: (topic: string) => Promise<string | null>;
  currentLesson: Lesson | null;
  onLessonSelect: (lesson: Lesson | null) => void;
}

const MainArea = ({
  lessons,
  onGenerateLesson,
  currentLesson,
  onLessonSelect,
}: MainAreaProps) => {
  const [showQuiz, setShowQuiz] = useState(false);
  const [currentNarration, setCurrentNarration] = useState<string | null>(null);
  const [isGeneratingQuiz, setIsGeneratingQuiz] = useState(false);
  const [quizQuestions, setQuizQuestions] = useState<QuizQuestion[]>([]);
  const [quizSummary, setQuizSummary] = useState<string | null>(null);
  const [isLoadingSummary, setIsLoadingSummary] = useState(false);

  const handleQuizSubmit = async (quizData: QuizSubmissionData[]) => {
    console.log("Quiz submission data:", quizData);
    
    // Ingest quiz data to Fastino (non-blocking)
    const user_id = getFastinoUserId();
    const topic = currentLesson?.topic || "";
    
    if (user_id && topic) {
      // Ingest each question separately
      for (const questionData of quizData) {
        try {
          const success = await ingestQuiz(user_id, {
            topic,
            ...questionData,
          });
          
          if (!success) {
            console.warn(`⚠️  Fastino quiz ingestion failed for question: ${questionData.question}`);
          }
        } catch (error) {
          console.warn(`⚠️  Fastino quiz ingestion error for question: ${questionData.question}`, error);
        }
      }
      
      // Query Fastino for quiz performance summary
      setIsLoadingSummary(true);
      setQuizSummary(null); // Clear previous summary
      try {
        const question = `In 2-3 lines tell me about the weak points and the topics to focus on from the previous quizes related to ${topic}.`;
        const summary = await queryFastino(user_id, question, false);
        
        if (summary) {
          // Store summary to display in QuizPanel
          setQuizSummary(summary);
        } else {
          console.warn("⚠️  Could not retrieve quiz performance summary from Fastino");
          setQuizSummary(null);
        }
      } catch (error) {
        console.warn("⚠️  Error querying Fastino for quiz summary:", error);
        setQuizSummary(null);
      } finally {
        setIsLoadingSummary(false);
      }
      
      // Show warning if any ingestion failed (non-blocking)
      const failedCount = quizData.filter((_, index) => {
        // We can't easily track which ones failed, so just show a general warning if needed
        return false; // For now, don't show warning unless we track failures
      }).length;
      
      if (failedCount > 0) {
        toast.warning("Some quiz data may not have been saved to Fastino");
      }
    }
  };

  const handleCloseQuiz = () => {
    setShowQuiz(false);
    setQuizQuestions([]);
    setQuizSummary(null);
    setIsLoadingSummary(false);
  };

  const handleTakeQuiz = async () => {
    if (!currentLesson) {
      toast.error("Please select a lesson first");
      return;
    }

    setIsGeneratingQuiz(true);
    try {
      console.log("🎯 Generating quiz for lesson:", currentLesson.topic);
      const quizData = await generateQuiz(currentLesson.topic);
      console.log("✅ Quiz generated successfully:", quizData);
      
      if (quizData.questions && quizData.questions.length > 0) {
        setQuizQuestions(quizData.questions);
        setShowQuiz(true);
      } else {
        toast.error("No questions found in quiz response");
      }
    } catch (error) {
      console.error("❌ Failed to generate quiz:", error);
      const errorMessage = error instanceof Error ? error.message : "Failed to generate quiz";
      toast.error(errorMessage);
    } finally {
      setIsGeneratingQuiz(false);
    }
  };

  return (
    <div className="flex-1 overflow-y-auto bg-gray-50 p-4 md:p-6 lg:p-8">
      <div className="max-w-4xl mx-auto space-y-6">
        <VideoFrame lesson={currentLesson} onNarrationChange={setCurrentNarration} />
        
        {/* Narration - Below frame, above input, black color, full width, centered */}
        {currentNarration && (
          <div className="w-full text-black text-sm md:text-base text-center px-4">
            {currentNarration}
          </div>
        )}
        
        {!showQuiz ? (
          <>
            <LessonInput onGenerate={onGenerateLesson} />
            {currentLesson && (
              <div className="flex justify-center">
                <TakeQuizButton
                  onClick={handleTakeQuiz}
                  disabled={isGeneratingQuiz}
                />
              </div>
            )}
          </>
        ) : (
          currentLesson && quizQuestions.length > 0 && (
            <QuizPanel
              lesson={currentLesson}
              questions={quizQuestions}
              onSubmit={handleQuizSubmit}
              onClose={handleCloseQuiz}
              summary={quizSummary}
              isLoadingSummary={isLoadingSummary}
            />
          )
        )}
      </div>
    </div>
  );
};

export default MainArea;

