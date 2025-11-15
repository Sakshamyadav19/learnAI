import { useState } from "react";
import { Lesson } from "@/pages/Home";
import { Button } from "@/components/ui/button";
import {
  RadioGroup,
  RadioGroupItem,
} from "@/components/ui/radio-group";
import { Label } from "@/components/ui/label";
import { X } from "lucide-react";

export interface QuizQuestion {
  id: number;
  question: string;
  options: string[];
  correctAnswer: number;
}

export interface QuizSubmissionData {
  question: string;
  answer: string; // correct answer text
  user_answer: string; // user's answer text
  verdict: "correct" | "wrong";
}

interface QuizPanelProps {
  lesson?: Lesson | null;
  questions: QuizQuestion[];
  onSubmit: (quizData: QuizSubmissionData[]) => void;
  onClose: () => void;
}

const QuizPanel = ({ lesson, questions, onSubmit, onClose }: QuizPanelProps) => {
  const [answers, setAnswers] = useState<Record<number, string>>({});
  const [isSubmitted, setIsSubmitted] = useState(false);
  const [score, setScore] = useState<number | null>(null);

  const handleSubmit = () => {
    let correctCount = 0;
    const quizData: QuizSubmissionData[] = [];
    
    questions.forEach((question) => {
      const userAnswerIndex = parseInt(answers[question.id] || "-1");
      const isCorrect = userAnswerIndex === question.correctAnswer;
      
      if (isCorrect) {
        correctCount++;
      }
      
      // Collect complete quiz data for ingestion
      quizData.push({
        question: question.question,
        answer: question.options[question.correctAnswer], // correct answer text
        user_answer: userAnswerIndex >= 0 ? question.options[userAnswerIndex] : "No answer",
        verdict: isCorrect ? "correct" : "wrong",
      });
    });

    const calculatedScore = correctCount;
    setScore(calculatedScore);
    setIsSubmitted(true);
    onSubmit(quizData);
  };

  const handleClose = () => {
    setAnswers({});
    setIsSubmitted(false);
    setScore(null);
    onClose();
  };

  if (!lesson) {
    return null;
  }

  return (
    <div className="bg-white rounded-lg shadow-lg p-6 space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-gray-900">Quiz: {lesson.title}</h2>
        <Button
          variant="ghost"
          size="icon"
          onClick={handleClose}
          className="text-gray-500 hover:text-gray-900"
        >
          <X className="h-5 w-5" />
        </Button>
      </div>

      {!isSubmitted ? (
        <>
          {questions.map((question) => (
            <div key={question.id} className="space-y-3 border-b pb-4 last:border-0">
              <Label className="text-base font-semibold text-gray-900">
                {question.id}. {question.question}
              </Label>
              <RadioGroup
                value={answers[question.id]?.toString() || ""}
                onValueChange={(value) =>
                  setAnswers({ ...answers, [question.id]: value })
                }
              >
                {question.options.map((option, index) => (
                  <div key={index} className="flex items-center space-x-2">
                    <RadioGroupItem value={index.toString()} id={`q${question.id}-${index}`} />
                    <Label
                      htmlFor={`q${question.id}-${index}`}
                      className="text-sm text-gray-700 cursor-pointer"
                    >
                      {option}
                    </Label>
                  </div>
                ))}
              </RadioGroup>
            </div>
          ))}

          <Button
            onClick={handleSubmit}
            disabled={Object.keys(answers).length !== questions.length}
            className="w-full"
            style={{
              backgroundColor:
                Object.keys(answers).length !== questions.length
                  ? "#cccccc"
                  : "#FE5C02",
              color: "#FFFFFF",
            }}
            onMouseEnter={(e) => {
              if (Object.keys(answers).length === questions.length) {
                e.currentTarget.style.backgroundColor = "#e54d00";
              }
            }}
            onMouseLeave={(e) => {
              if (Object.keys(answers).length === questions.length) {
                e.currentTarget.style.backgroundColor = "#FE5C02";
              }
            }}
          >
            Submit Quiz
          </Button>
        </>
      ) : (
        <div className="text-center space-y-4">
          <div className="text-4xl font-bold text-gray-900">
            You scored {score} out of {questions.length}!
          </div>
          <div className="text-lg text-gray-600">
            {score !== null && score === questions.length
              ? "Perfect score! 🎉"
              : score !== null && score >= questions.length / 2
              ? "Good job! Keep practicing."
              : "Don't worry, keep learning and try again!"}
          </div>
          <Button
            onClick={handleClose}
            className="mt-4"
            style={{
              backgroundColor: "#FE5C02",
              color: "#FFFFFF",
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.backgroundColor = "#e54d00";
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.backgroundColor = "#FE5C02";
            }}
          >
            Close Quiz
          </Button>
        </div>
      )}
    </div>
  );
};

export default QuizPanel;

