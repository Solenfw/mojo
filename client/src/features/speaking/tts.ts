/**
 * Japanese text-to-speech through the browser's speechSynthesis. Works around the usual browser quirks:
 * the voice list loads asynchronously, Safari only speaks inside a user gesture until unlocked, and
 * Chrome drops an utterance spoken right after cancel() or one that gets garbage-collected mid-speech.
 */

// Best-sounding voices first: Chrome's network voice, then macOS / Windows system voices.
const PREFERRED_VOICES = ['Google 日本語', 'Kyoko', 'O-ren', 'Otoya', 'Microsoft Nanami', 'Microsoft Ayumi', 'Microsoft Haruka'];

let voicesPromise: Promise<SpeechSynthesisVoice[]> | null = null;
// Holding a reference keeps Chrome from garbage-collecting the utterance (which silently cuts it off).
let currentUtterance: SpeechSynthesisUtterance | null = null;

const isSupported = () => typeof window !== 'undefined' && 'speechSynthesis' in window;

const loadVoices = (): Promise<SpeechSynthesisVoice[]> => {
  if (!isSupported()) return Promise.resolve([]);
  const voices = window.speechSynthesis.getVoices();
  if (voices.length) return Promise.resolve(voices);
  voicesPromise ??= new Promise((resolve) => {
    const done = () => resolve(window.speechSynthesis.getVoices());
    window.speechSynthesis.addEventListener('voiceschanged', done, { once: true });
    setTimeout(done, 1500); // some browsers never fire voiceschanged
  });
  return voicesPromise;
};

export const getJapaneseVoice = async (): Promise<SpeechSynthesisVoice | null> => {
  const japanese = (await loadVoices()).filter((voice) => voice.lang.replace('_', '-').startsWith('ja'));
  for (const name of PREFERRED_VOICES) {
    const match = japanese.find((voice) => voice.name.includes(name));
    if (match) return match;
  }
  return japanese[0] ?? null;
};

/** Call from a click handler: Safari refuses later, non-gesture speech until something was spoken in one. */
export const unlockSpeech = () => {
  if (!isSupported()) return;
  const silent = new SpeechSynthesisUtterance('');
  silent.volume = 0;
  window.speechSynthesis.speak(silent);
  void loadVoices();
};

export const stopSpeech = () => {
  if (isSupported()) window.speechSynthesis.cancel();
  currentUtterance = null;
};

/** Speaks `text` in Japanese; `onEnd` runs when it finishes or fails. Resolves false if it can't speak. */
export const speakJapanese = async (text: string, onEnd?: () => void): Promise<boolean> => {
  if (!isSupported()) {
    onEnd?.();
    return false;
  }
  const synth = window.speechSynthesis;
  const voice = await getJapaneseVoice();

  if (synth.speaking || synth.pending) {
    synth.cancel();
    await new Promise((resolve) => setTimeout(resolve, 60)); // Chrome drops a speak() issued right after cancel()
  }

  const utterance = new SpeechSynthesisUtterance(text);
  utterance.lang = 'ja-JP';
  utterance.rate = 0.9;
  if (voice) utterance.voice = voice;
  const finish = () => {
    if (currentUtterance === utterance) currentUtterance = null;
    onEnd?.();
  };
  utterance.onend = finish;
  utterance.onerror = finish;

  currentUtterance = utterance;
  synth.resume(); // Chrome can get stuck paused after a tab switch
  synth.speak(utterance);
  return voice !== null;
};
