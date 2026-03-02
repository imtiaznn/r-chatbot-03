const chatToggle = document.getElementById('chatbot-toggle');
const chatBox = document.getElementById('chatbox');
const closeBtn = document.getElementById('chatbox-close');
const resizeBtn = document.getElementById('chatbox-resize');
const resizeIcon = document.getElementById('resize-btn');
const sendButton = document.querySelector(".chatbox-input button");
const msgContainer = document.getElementById("chat-messages");
const thinking = document.getElementById("thinking-bubble");
const input = document.getElementById("user-input");
const sendBtn = document.querySelector(".send-btn");

// button swap images 
const expandIcon = "./assets/expand.png";
const shrinkIcon = "./assetts/shrink.png";

document.addEventListener('DOMContentLoaded', () => {

    // Toggle chatbox visibility
    chatToggle.addEventListener('click', () => {
        chatBox.classList.toggle('active');
    });

    // Close button
    closeBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        chatBox.classList.remove('active');
    });

    // FAQ button events
    document.querySelectorAll(".faq-screen:not(#main-faq) .faq-btn").forEach(btn => {
      btn.addEventListener("click", () => sendFaqMessage(btn.textContent));
    });

    // Resize button toggle
    let isExpanded = false;
    resizeBtn.addEventListener('click', (e) => {
        e.stopPropagation();

        if (!isExpanded) {
            chatBox.style.minWidth = "600px";
            chatBox.style.minHeight = "500px";
            resizeIcon.src = shrinkIcon;
        } else {
            chatBox.style.minWidth = "400px";
            chatBox.style.minHeight = "450px";
            resizeIcon.src = expandIcon;
        }

        isExpanded = !isExpanded;
    });

    // FAQ Navigation (swipe faq screen) 
    // general
    window.openGeneral = function () {
        slideTo("general-faq");
    };

    // product & services
    window.openP_S = function () {
        slideTo("ps-faq");
    };

    // pricing
    window.openPricing = function () {
        slideTo("pricing-faq");
    };

    // troubleshooting
    window.openTS = function () {
        slideTo("ts-faq");
    };

    // contact us
    window.openContact = function () {
       slideTo("contact-faq");
    };

    function slideTo(id) {
        const main = document.getElementById("main-faq");
        const target = document.getElementById(id);

        main.classList.remove("active");
        main.classList.add("slide-left");

        target.classList.add("active", "slide-in");
    }

    // return to main faq screen
    window.goBack = function () {
        const main = document.getElementById("main-faq");

        // Find the currently active FAQ screen (but not the main screen)
        const current = document.querySelector(".faq-screen.active:not(#main-faq)");

        if (!current) return; // no active sub-screen, nothing to do

        // Slide the current screen OUT to the right
        current.classList.remove("active", "slide-in");
        current.classList.add("slide-right");

        // Reset the main screen
        main.classList.add("active");
        main.classList.remove("slide-left");
    };  

    // mimick send button event
    sendButton.addEventListener("click", () => {
        const input = document.getElementById("user-input");
        const text = input.value.trim();
        if (!text) return;

        // appendUserMessage(text);
        sendMessage();
        input.value = "";
    });
    
    // send when user press enter key
    input.addEventListener("keypress", function (e) {
        if (e.key === "Enter") {
            e.preventDefault();      // prevent newline
            sendBtn.click();         // simulate button click
        }
    });

    // FAQ Resize container
    const updateFaqHeight = () => {
        const container = document.querySelector('.faq-container');
        if (!container) return;

        const active = container.querySelector('.faq-screen.active');
        // if no active slide, collapse to zero or use a sensible default
        container.style.height = active ? `${active.offsetHeight}px` : '0px';
    };

    // initial sizing
    updateFaqHeight();

    // update on window resize (content reflow)
    window.addEventListener('resize', () => {
        // small debounce
        clearTimeout(window.__faqResizeTimer);
        window.__faqResizeTimer = setTimeout(updateFaqHeight, 80);
    });

    // watch for class changes on faq-screen elements (e.g. .active toggles)
    const observer = new MutationObserver(mutations => {
        for (const m of mutations) {
        if (m.type === 'attributes' && m.attributeName === 'class') {
            updateFaqHeight();
            break;
        }
        }
    });
    
    document.querySelectorAll('.faq-screen').forEach(el => observer.observe(el, { attributes: true }));
})

// Websocket connection
const messagesDiv = document.getElementById("chat-messages");

// Connect to Rasa SocketIO endpoint
const sessionId = "session_" + Math.random().toString(36).substr(2, 9);
const socket = io("http://localhost:5005", {
  transports: ["websocket"],
});

// Function declarations
function addMessage(text, sender) {
  const div = document.createElement("div");
  div.className = `${sender}-bubble`;
  div.innerText = text;
  messagesDiv.appendChild(div);
  messagesDiv.scrollTop = messagesDiv.scrollHeight;
  scrollToBottom();
}

function sendMessage() {
  const msg = document.getElementById("user-input").value;
  if (!msg) return;

  addMessage(msg, "user");

  showThinking();

  socket.emit("user_uttered", {
    message: msg,
    session_id: sessionId
  });

  document.getElementById("user-input").value = "";
}

function sendFaqMessage(text) {
    const msg = (text || "").trim();
    if (!msg) return;

    addMessage(msg, "user");

    showThinking();
    socket.emit("user_uttered", {
        message: msg,
        session_id: sessionId
    });
}


function showThinking() {
    if (!thinking) return;
    if (thinking.parentNode === msgContainer) return; // already shown

    thinking.style.display = "inline-flex";
    msgContainer.appendChild(thinking);
    scrollToBottom();
}

function hideThinking() {
  if (!thinking) return;
  thinking.style.display = "none";
  if (thinking.parentNode === msgContainer) {
    msgContainer.removeChild(thinking);
  }
}

function replaceThinkingWithBot(text) {
  // remove the typing indicator and append bot message
  hideThinking();
  if (text) {
    addMessage(text, "chatbot");
  }
}

function scrollToBottom() {
    const chatBody = document.getElementById("chatbox-body");
    chatBody.scrollTop = chatBody.scrollHeight;
}

// Request socket session
socket.emit("session_request", {session_id: sessionId });

// Listen for session confirmation (optional)
socket.on("session_confirm", function(data) {
  console.log("Session started:", data);
});

// Listen for bot responses
socket.on("bot_uttered", function (data) {
    console.log("Bot event received:", data); // debug

    const msg =
        data.text ||                // Standard Rasa responses
        data.message ||             // LiteLLM / rephrased responses
        (data.custom && data.custom.text) ||  // custom payloads
        JSON.stringify(data);        // fallback for debugging

    if (msg) replaceThinkingWithBot(msg, "chatbot");
});
