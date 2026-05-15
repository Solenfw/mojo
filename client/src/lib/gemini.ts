import { GoogleGenAI } from "@google/genai";

const API_KEY = process.env.GEMINI_API_KEY || "";
const genAI = new GoogleGenAI({ apiKey: API_KEY });

export const analyzePronunciation = async (transcript: string, expectedText: string) => {
  const prompt = `Analyze the Japanese pronunciation. 
  Expected: "${expectedText}"
  Transcript: "${transcript}"
  Provide feedback on accuracy, rhythm, and pitch accent (if applicable). 
  Return JSON format: { accuracy: number, feedback: string, tips: string[] }`;

  const result = await genAI.models.generateContent({
    model: "gemini-3-flash-preview",
    contents: prompt
  });
  
  return JSON.parse(result.text || "{}");
};

export const getWritingFeedback = async (canvasDataUrl: string, kanji: string) => {
  // This is a placeholder for Vision-based feedback
  const prompt = `Analyze this Kanji handwriting attempt for "${kanji}". 
  Provide feedback on stroke order, balance, and aesthetics.`;

  const result = await genAI.models.generateContent({
    model: "gemini-3-flash-preview",
    contents: prompt
  });
  
  return result.text;
};
