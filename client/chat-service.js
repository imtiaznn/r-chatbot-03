/**
 * CHAT-SERVICE.JS
 * Handles WebSocket connection and networking logic.
 */

const sessionId = "session_" + Math.random().toString(36).substr(2, 9);
const socket = io("http://127.0.0.1:5005", {
  // path: "/socket.io",
  transports: ["websocket"],
});

// Request socket session
socket.emit("session_request", { session_id: sessionId });

// Listen for session confirmation
socket.on("session_confirm", function(data) {
  console.log("Session started:", data);

});

// Listen for bot responses from Rasa
socket.on("bot_uttered", function (data) {
    console.log("Bot event received:", data);

    const msg =
        data.text ||                
        data.message ||             
        (data.custom && data.custom.text) ||  
        JSON.stringify(data);        

    if (msg) {
        // Calls the UI function to update the chat bubble
        if (typeof window.replaceThinkingWithBot === "function") {
            window.replaceThinkingWithBot(msg);
        }
    }
});

/**
 * Global function to emit message to backend
 * Called by ui-controller.js
 */
window.emitUserMessage = function(msg) {
    socket.emit("user_uttered", {
        message: msg,
        session_id: sessionId
    });

    console.log("USER:", msg);
};