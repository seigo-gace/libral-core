import { createRoot } from "react-dom/client";
import App from "./App";
import "./index.css";

// Force cache bust - Version 2.1.0 - ALL PAGES YELLOW
console.log('[LIBRAL-CORE] Loading v2.1.0 - ALL PAGES YELLOW DESIGN - C3 IS NOW YELLOW!');

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
