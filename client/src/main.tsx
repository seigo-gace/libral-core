import { createRoot } from "react-dom/client";
import App from "./App";
import "./index.css";

// Force cache bust - Version 2.1.1 - DIRECT HTML INJECTION + SW CLEANUP
console.log('🟡🟡🟡 [LIBRAL-CORE v2.1.1] YELLOW DESIGN LOADED - HTML INJECTED - SW CLEARED 🟡🟡🟡');
console.log('Title:', document.title);
console.log('Body background:', window.getComputedStyle(document.body).background);

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
