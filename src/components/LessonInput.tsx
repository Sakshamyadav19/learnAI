import { useState } from "react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Loader2 } from "lucide-react";

interface LessonInputProps {
  onGenerate: (topic: string) => Promise<string | null>; // Returns error message or null on success
}

const LessonInput = ({ onGenerate }: LessonInputProps) => {
  const [topic, setTopic] = useState("");
  const [isGenerating, setIsGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (!topic.trim() || isGenerating) {
      return;
    }

    setIsGenerating(true);
    const topicValue = topic.trim();

    try {
      const errorMessage = await onGenerate(topicValue);
      if (errorMessage) {
        // Error occurred - keep input field populated
        setError(errorMessage);
      } else {
        // Success - clear input
        setTopic("");
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "An unexpected error occurred");
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="flex gap-3">
        <Input
          type="text"
          placeholder="Enter a topic to learn..."
          value={topic}
          onChange={(e) => {
            setTopic(e.target.value);
            setError(null); // Clear error when user types
          }}
          disabled={isGenerating}
          className="flex-1"
        />
        <Button
          type="submit"
          disabled={isGenerating || !topic.trim()}
          className="px-6"
          style={{
            backgroundColor: isGenerating ? "#cccccc" : "#FE5C02",
            color: "#FFFFFF",
            cursor: isGenerating ? "not-allowed" : "pointer",
          }}
          onMouseEnter={(e) => {
            if (!isGenerating) {
              e.currentTarget.style.backgroundColor = "#e54d00";
            }
          }}
          onMouseLeave={(e) => {
            if (!isGenerating) {
              e.currentTarget.style.backgroundColor = "#FE5C02";
            }
          }}
        >
          {isGenerating ? (
            <>
              <Loader2 className="w-4 h-4 mr-2 animate-spin" />
              Generating...
            </>
          ) : (
            "Generate Lesson"
          )}
        </Button>
      </div>
      {error && (
        <p className="text-sm text-red-500 mt-2">{error}</p>
      )}
    </form>
  );
};

export default LessonInput;

