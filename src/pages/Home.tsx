import { useState } from "react";
import Navbar from "@/components/Navbar";
import SidebarLessons from "@/components/SidebarLessons";
import MainArea from "@/components/MainArea";
import { generateLesson, LessonSegment } from "@/lib/api";

export interface Lesson {
  id: number;
  title: string;
  topic: string;
  segments: LessonSegment[];
  createdAt: Date;
}

const Home = () => {
  const [lessons, setLessons] = useState<Lesson[]>([]);
  const [currentLesson, setCurrentLesson] = useState<Lesson | null>(null);

  const handleGenerateLesson = async (topic: string): Promise<string | null> => {
    try {
      // Call API to generate lesson
      const lessonData = await generateLesson(topic);

      // Create new lesson object
      const newLesson: Lesson = {
        id: Date.now(),
        title: lessonData.topic,
        topic: lessonData.topic,
        segments: lessonData.segments,
        createdAt: new Date(),
      };

      // Update state
      setLessons((prev) => [...prev, newLesson]);
      setCurrentLesson(newLesson);

      // Note: Lesson ingestion to Fastino is handled in the backend before generation
      // Return null on success (no error)
      return null;
    } catch (error) {
      // Return error message
      const errorMessage =
        error instanceof Error
          ? error.message
          : "Failed to generate lesson. Please try again.";
      return errorMessage;
    }
  };

  const handleLessonClick = (lesson: Lesson) => {
    setCurrentLesson(lesson);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      <div className="pt-16 md:pt-20">
        <div className="flex flex-col md:flex-row h-[calc(100vh-4rem)] md:h-[calc(100vh-5rem)]">
          <div className="hidden md:block">
            <SidebarLessons
              lessons={lessons}
              onLessonClick={handleLessonClick}
              activeLessonId={currentLesson?.id}
            />
          </div>
          <MainArea
            lessons={lessons}
            onGenerateLesson={handleGenerateLesson}
            currentLesson={currentLesson}
            onLessonSelect={setCurrentLesson}
          />
        </div>
      </div>
    </div>
  );
};

export default Home;

