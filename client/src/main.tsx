import { createRoot } from "react-dom/client";
import App from "./App";
import "./index.css";

// LIBRAL CORE - Black Background, White Text, Minimal Yellow Accents
console.log('[LIBRAL-CORE v3.0.0] Correct Design Loaded - Black BG, White Text, Yellow Accents');

// グローバルエラーハンドラーを追加
window.addEventListener('unhandledrejection', (event) => {
  console.error('Unhandled promise rejection:', event.reason);
  // エラーを防ぐために preventDefault() を呼び出す
  event.preventDefault();
});

window.addEventListener('error', (event) => {
  console.error('Unhandled error:', event.error);
});

createRoot(document.getElementById("root")!).render(<App />);
