
import React from "react";
import learningShowcase from "@/assets/learning-showcase.jpg";

const ImageShowcaseSection = () => {
  return (
    <section className="w-full pt-0 pb-8 sm:pb-12 bg-white" id="showcase">
      <div className="container px-4 sm:px-6 lg:px-8 mx-auto">
        <div className="max-w-3xl mx-auto text-center mb-8 sm:mb-12 animate-on-scroll">
          <h2 className="text-3xl sm:text-4xl font-display font-bold tracking-tight text-gray-900 mb-3 sm:mb-4">
            Learning That Adapts to You
          </h2>
          <p className="text-base sm:text-lg text-gray-600">
            Our AI-powered platform delivers personalized lessons in 30-60 seconds, 
            fitting seamlessly into your daily routine.
          </p>
        </div>
        
        <div className="rounded-2xl sm:rounded-3xl overflow-hidden shadow-elegant mx-auto max-w-4xl animate-on-scroll">
          <div className="w-full bg-gradient-to-br from-purple-900 to-blue-900">
            <img 
              src={learningShowcase} 
              alt="Person learning with AI-powered holographic interface" 
              className="w-full h-auto object-cover"
            />
          </div>
          <div className="bg-white p-4 sm:p-8">
            <h3 className="text-xl sm:text-2xl font-display font-semibold mb-3 sm:mb-4">Smart Learning Technology</h3>
            <p className="text-gray-700 text-sm sm:text-base">
              Powered by advanced AI algorithms, Learn.AI analyzes your progress and adapts 
              content in real-time. From languages to professional skills, master anything 
              with personalized micro-lessons that fit your life.
            </p>
          </div>
        </div>
      </div>
    </section>
  );
};

export default ImageShowcaseSection;
