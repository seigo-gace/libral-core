import { createRoot } from "react-dom/client";
import App from "./App";
import "./index.css";

// Force cache bust - Version 2.0.0
console.log('[LIBRAL-CORE] Loading v2.0.0 - Yellow Design');

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
