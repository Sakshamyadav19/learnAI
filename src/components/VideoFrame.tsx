import { useState, useEffect, useRef } from "react";
import { Play, Pause, AlertCircle } from "lucide-react";
import { Lesson } from "@/pages/Home";
import { convertBase64ToAudioUrl, revokeAudioUrl } from "@/lib/audio";

interface VideoFrameProps {
  lesson?: Lesson | null;
  onNarrationChange?: (narration: string | null) => void;
}

const VideoFrame = ({ lesson, onNarrationChange }: VideoFrameProps) => {
  const [currentSegmentIndex, setCurrentSegmentIndex] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);
  const [audioUrls, setAudioUrls] = useState<string[]>([]);
  const [imagesLoaded, setImagesLoaded] = useState<Set<number>>(new Set());
  const [imageErrors, setImageErrors] = useState<Set<number>>(new Set());
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const currentAudioUrlRef = useRef<string | null>(null);
  const imageRefs = useRef<Map<number, HTMLImageElement>>(new Map());

  // Pre-convert all audio and pre-load all images when lesson changes
  useEffect(() => {
    if (!lesson || !lesson.segments || lesson.segments.length === 0) {
      // Clear narration when no lesson
      if (onNarrationChange) {
        onNarrationChange(null);
      }
      return;
    }

    console.log("🎬 Setting up lesson with", lesson.segments.length, "segments");

    // Clean up previous audio URLs
    audioUrls.forEach((url) => {
      if (url) revokeAudioUrl(url);
    });

    const urls: string[] = [];
    const imageLoadPromises: Promise<void>[] = [];

    try {
      // Pre-convert all audio base64 to URLs
      lesson.segments.forEach((segment) => {
        // Convert audio
        if (segment.audioBase64) {
          try {
            const audioUrl = convertBase64ToAudioUrl(segment.audioBase64);
            urls.push(audioUrl);
            console.log(`✅ Converted audio for segment ${segment.segment_id}`);
          } catch (error) {
            console.error(`❌ Failed to convert audio for segment ${segment.segment_id}:`, error);
            urls.push(""); // Empty URL for failed conversion
          }
        } else {
          urls.push("");
        }

        // Pre-load images
        if (segment.imageUrl) {
          const img = new Image();
          img.src = segment.imageUrl;
          
          const loadPromise = new Promise<void>((resolve) => {
            img.onload = () => {
              console.log(`✅ Loaded image for segment ${segment.segment_id}`);
              setImagesLoaded((prev) => new Set(prev).add(segment.segment_id));
              imageRefs.current.set(segment.segment_id, img);
              resolve();
            };
            
            img.onerror = () => {
              console.error(`❌ Failed to load image for segment ${segment.segment_id}:`, segment.imageUrl);
              setImageErrors((prev) => new Set(prev).add(segment.segment_id));
              resolve(); // Resolve anyway to not block
            };
          });
          
          imageLoadPromises.push(loadPromise);
        }
      });

      setAudioUrls(urls);
      setCurrentSegmentIndex(0);
      setIsPlaying(false);
      setImageErrors(new Set());
      
      // Notify parent of initial narration
      if (lesson.segments[0]?.narration && onNarrationChange) {
        onNarrationChange(lesson.segments[0].narration);
      }
      
      console.log(`📊 Pre-loaded ${urls.filter(u => u).length} audio URLs`);
      console.log(`📊 Pre-loading ${imageLoadPromises.length} images...`);

      // Wait for all images to load (or fail)
      Promise.all(imageLoadPromises).then(() => {
        console.log("✅ All images pre-loading initiated");
      });

    } catch (error) {
      console.error("❌ Error setting up lesson:", error);
      setAudioUrls([]);
    }

    // Cleanup function
    return () => {
      urls.forEach((url) => {
        if (url) revokeAudioUrl(url);
      });
      imageRefs.current.clear();
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [lesson]);

  // Auto-play when lesson is loaded and audio URLs are ready
  useEffect(() => {
    if (
      lesson &&
      lesson.segments &&
      lesson.segments.length > 0 &&
      audioUrls.length === lesson.segments.length &&
      audioUrls[0] // First audio URL is ready
    ) {
      console.log("🎬 Auto-playing lesson...");
      // Reset to first segment
      setCurrentSegmentIndex(0);
      
      // Small delay to ensure everything is ready
      const timer = setTimeout(() => {
        handlePlay();
      }, 800);

      return () => clearTimeout(timer);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [lesson, audioUrls.length]);

  // Handle audio ended event - seamlessly transition to next segment
  useEffect(() => {
    const audio = audioRef.current;
    if (!audio || !lesson?.segments) return;

    const handleEnded = () => {
      console.log(`🎵 Audio ended for segment ${currentSegmentIndex}`);
      
      if (currentSegmentIndex < lesson.segments.length - 1) {
        // Move to next segment seamlessly (no pause)
        const nextIndex = currentSegmentIndex + 1;
        
        setCurrentSegmentIndex(nextIndex);
        setImageErrors(new Set()); // Reset errors for new segment
        
        // Pre-load next image if not already loaded
        const nextSegment = lesson.segments[nextIndex];
        
        // Update narration for next segment
        if (onNarrationChange) {
          onNarrationChange(nextSegment?.narration || null);
        }
        if (nextSegment?.imageUrl && !imagesLoaded.has(nextSegment.segment_id)) {
          const img = new Image();
          img.src = nextSegment.imageUrl;
          img.onload = () => {
            console.log(`✅ Loaded image for next segment ${nextSegment.segment_id}`);
            setImagesLoaded((prev) => new Set(prev).add(nextSegment.segment_id));
          };
        }
        
        // Play next segment audio immediately (seamless transition)
        // The audio source will be updated in the next useEffect
        setTimeout(() => {
          if (audioRef.current && audioUrls[nextIndex]) {
            console.log(`🎵 Playing segment ${nextIndex}`);
            audioRef.current.play().catch((error) => {
              console.error(`❌ Error playing next segment:`, error);
              setIsPlaying(false);
            });
          }
        }, 50); // Very short delay for smooth transition
      } else {
        // Reached end - stop playing
        console.log("🏁 Reached end of lesson");
        setIsPlaying(false);
        // Keep showing last segment's narration
      }
    };

    audio.addEventListener("ended", handleEnded);
    return () => audio.removeEventListener("ended", handleEnded);
  }, [currentSegmentIndex, lesson, audioUrls, imagesLoaded]);

  // Update narration when segment changes
  useEffect(() => {
    if (lesson?.segments && onNarrationChange) {
      const currentSegment = lesson.segments[currentSegmentIndex];
      onNarrationChange(currentSegment?.narration || null);
    }
  }, [currentSegmentIndex, lesson, onNarrationChange]);

  // Update audio source when segment changes
  useEffect(() => {
    if (!audioRef.current || !lesson?.segments || audioUrls.length === 0) return;

    const currentSegment = lesson.segments[currentSegmentIndex];
    const currentUrl = audioUrls[currentSegmentIndex];
    
    if (!currentUrl || !currentSegment) return;

    console.log(`🎵 Setting audio source for segment ${currentSegment.segment_id}`);
    audioRef.current.src = currentUrl;
    currentAudioUrlRef.current = currentUrl;

    // Pre-load the audio
    audioRef.current.load();

    // If playing, start immediately (for seamless transitions)
    if (isPlaying) {
      audioRef.current
        .play()
        .then(() => {
          console.log(`▶️  Playing segment ${currentSegment.segment_id}`);
        })
        .catch((error) => {
          console.error(`❌ Error playing audio for segment ${currentSegment.segment_id}:`, error);
          setIsPlaying(false);
        });
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [currentSegmentIndex, audioUrls, lesson, isPlaying]);

  const handlePlay = () => {
    if (!audioRef.current || !lesson?.segments || audioUrls.length === 0) return;

    const audio = audioRef.current;
    
    // Check if we're at the end (last segment finished playing)
    // If we're on the last segment AND audio has ended, restart from beginning
    const isAtEnd = currentSegmentIndex >= lesson.segments.length - 1 && audio.ended;
    
    if (isAtEnd) {
      // Restart from beginning
      console.log("🔄 Restarting from beginning (video ended)");
      setCurrentSegmentIndex(0);
      // Update narration to first segment
      if (onNarrationChange && lesson.segments[0]?.narration) {
        onNarrationChange(lesson.segments[0].narration);
      }
      // Wait for segment to change, then play
      setTimeout(() => {
        if (audioRef.current && audioUrls[0]) {
          audioRef.current.src = audioUrls[0];
          audioRef.current.load();
          audioRef.current.play().then(() => {
            setIsPlaying(true);
            console.log("▶️  Restarted from beginning");
          }).catch((error) => {
            console.error("❌ Error restarting playback:", error);
            setIsPlaying(false);
          });
        }
      }, 100);
      return;
    }

    // Global play/pause: Resume from current position
    // This works whether we're in the middle of a segment or between segments
    const currentUrl = audioUrls[currentSegmentIndex];
    if (!currentUrl) {
      console.error("❌ No audio URL for current segment");
      return;
    }

    // Check if audio source needs to be updated
    // Compare by checking if the current URL matches what's loaded
    const currentSrc = audio.src;
    const urlFilename = currentUrl.split('/').pop() || '';
    const srcFilename = currentSrc.split('/').pop() || '';
    
    const needsNewSource = !currentSrc || 
      (!currentSrc.includes(urlFilename) && urlFilename !== '') ||
      (audio.ended && currentSegmentIndex < lesson.segments.length - 1);
    
    if (needsNewSource) {
      // Set new source and play
      console.log(`🎵 Loading new audio source for segment ${currentSegmentIndex}`);
      audio.src = currentUrl;
      audio.load();
      audio.play()
        .then(() => {
          console.log(`▶️  Started playing segment ${currentSegmentIndex}`);
          setIsPlaying(true);
        })
        .catch((error) => {
          console.error("❌ Error playing audio:", error);
          setIsPlaying(false);
        });
    } else {
      // Resume from current position (audio is already loaded)
      // This allows pausing and resuming at any point
      audio.play()
        .then(() => {
          console.log(`▶️  Resumed playing from current position (segment ${currentSegmentIndex})`);
          setIsPlaying(true);
        })
        .catch((error) => {
          console.error("❌ Error resuming audio:", error);
          setIsPlaying(false);
        });
    }
  };

  const handlePause = () => {
    if (audioRef.current) {
      audioRef.current.pause();
      setIsPlaying(false);
      console.log("⏸️  Paused playback");
    }
  };

  const handleImageLoad = (segmentId: number) => {
    setImagesLoaded((prev) => new Set(prev).add(segmentId));
  };

  const handleImageError = (segmentId: number) => {
    console.error(`❌ Image failed to load for segment ${segmentId}`);
    setImageErrors((prev) => new Set(prev).add(segmentId));
  };

  if (!lesson || !lesson.segments || lesson.segments.length === 0) {
    return (
      <div className="w-full h-64 md:h-96 bg-gray-100 rounded-lg shadow-md flex items-center justify-center">
        <div className="text-center">
          <Play className="w-12 h-12 md:w-16 md:h-16 text-gray-400 mx-auto mb-3" />
          <p className="text-gray-600 text-sm md:text-base">
            Video will appear here
          </p>
        </div>
      </div>
    );
  }

  const currentSegment = lesson.segments[currentSegmentIndex];
  const hasImage = currentSegment?.imageUrl && !imageErrors.has(currentSegment.segment_id);
  const imageLoaded = currentSegment?.imageUrl && imagesLoaded.has(currentSegment.segment_id);

  return (
    <div className="w-full h-64 md:h-96 bg-gray-100 rounded-lg shadow-md relative overflow-hidden">
      <audio ref={audioRef} preload="auto" />
      
      {/* Image Display with smooth transitions */}
      <div className="w-full h-full flex items-center justify-center relative">
        {/* Loading overlay - only show if image hasn't loaded yet */}
        {!imageLoaded && hasImage && (
          <div className="absolute inset-0 flex items-center justify-center bg-gray-100 z-10">
            <div className="text-gray-500">Loading image...</div>
          </div>
        )}
        
        {/* Image with fade transition */}
        {hasImage && (
          <img
            key={currentSegment.segment_id}
            src={currentSegment.imageUrl!}
            alt={`Segment ${currentSegment.segment_id}`}
            onLoad={() => handleImageLoad(currentSegment.segment_id)}
            onError={() => handleImageError(currentSegment.segment_id)}
            className={`w-full h-full object-contain transition-opacity duration-500 ${
              imageLoaded ? "opacity-100" : "opacity-0"
            }`}
            style={{
              transition: "opacity 0.5s ease-in-out",
            }}
          />
        )}
        
        {/* Error/placeholder for missing image */}
        {(!hasImage || imageErrors.has(currentSegment.segment_id)) && (
          <div className="text-center p-8">
            <AlertCircle className="w-12 h-12 md:w-16 md:h-16 text-gray-400 mx-auto mb-3" />
            <p className="text-gray-600 text-sm md:text-base">
              {currentSegment?.imageUrl
                ? "Failed to load image"
                : "No image available for this segment"}
            </p>
          </div>
        )}
      </div>

      {/* Controls Overlay - Play/Pause button at bottom left */}
      <div className="absolute bottom-0 left-0 p-4">
        <button
          onClick={isPlaying ? handlePause : handlePlay}
          className="bg-white/90 hover:bg-white text-gray-900 rounded-full p-3 transition-colors shadow-lg"
          aria-label={isPlaying ? "Pause" : "Play"}
        >
          {isPlaying ? (
            <Pause className="w-6 h-6" />
          ) : (
            <Play className="w-6 h-6" />
          )}
        </button>
      </div>
    </div>
  );
};

export default VideoFrame;
