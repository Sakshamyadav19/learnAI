import { Lesson } from "@/pages/Home";
import { cn } from "@/lib/utils";

interface SidebarLessonsProps {
  lessons: Lesson[];
  onLessonClick?: (lesson: Lesson) => void;
  activeLessonId?: number;
}

const SidebarLessons = ({
  lessons,
  onLessonClick,
  activeLessonId,
}: SidebarLessonsProps) => {
  return (
    <div className="w-64 h-full bg-white border-r border-gray-200 overflow-y-auto">
      <div className="p-4 border-b border-gray-200">
        <h2 className="text-lg font-semibold text-gray-900">Lessons</h2>
      </div>
      {lessons.length === 0 ? (
        <div className="p-4 text-center text-gray-500 text-sm">
          <p>No lessons yet. Generate one to get started!</p>
        </div>
      ) : (
        <div className="p-2">
          {lessons.map((lesson) => (
            <button
              key={lesson.id}
              onClick={() => onLessonClick?.(lesson)}
              className={cn(
                "w-full text-left p-3 rounded-lg mb-2 transition-colors",
                "hover:bg-gray-100",
                activeLessonId === lesson.id
                  ? "bg-orange-50 border border-orange-200"
                  : "bg-white"
              )}
            >
              <div className="font-medium text-gray-900 text-sm mb-1 truncate">
                {lesson.title}
              </div>
              <div className="text-xs text-gray-500 truncate">
                {lesson.topic}
              </div>
            </button>
          ))}
        </div>
      )}
    </div>
  );
};

export default SidebarLessons;

