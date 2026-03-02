/**
 * UI-CONTROLLER.JS
 * Handles DOM elements, FAQ navigation, and UI updates.
 */

const chatToggle = document.getElementById('chatbot-toggle');
const chatBox = document.getElementById('chatbox');
const closeBtn = document.getElementById('chatbox-close');
const resizeBtn = document.getElementById('chatbox-resize');
const resizeIcon = document.getElementById('resize-btn');
const msgContainer = document.getElementById("chat-messages");
const thinking = document.getElementById("thinking-bubble");
const input = document.getElementById("user-input");
const sendBtn = document.querySelector(".send-btn");

// Asset paths (Fixed typo: assetts -> assets)
const expandIcon = "./assets/expand.png";
const shrinkIcon = "./assets/shrink.png"; 

document.addEventListener('DOMContentLoaded', () => {
    // Visibility Toggle
    chatToggle.addEventListener('click', (e) => {
        e.stopPropagation();
        chatBox.classList.toggle('active');
    });

    closeBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        chatBox.classList.remove('active');
    });

    // Resize Logic
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

    // FAQ Button listener for sub-menus
    document.querySelectorAll(".faq-screen:not(#main-faq) .faq-btn").forEach(btn => {
      btn.addEventListener("click", () => sendMessage(btn.textContent));
    });

    // Input Events
    sendBtn.addEventListener("click", () => sendMessage());
    
    input.addEventListener("keypress", (e) => {
        if (e.key === "Enter") {
            e.preventDefault();
            sendBtn.click();
        }
    });

    /* --- FAQ Navigation Functions --- */
    window.openGeneral = () => slideTo("general-faq");
    window.openP_S = () => slideTo("ps-faq");
    window.openPricing = () => slideTo("pricing-faq");
    window.openTS = () => slideTo("ts-faq");
    window.openContact = () => slideTo("contact-faq");

    function slideTo(id) {
        const main = document.getElementById("main-faq");
        const target = document.getElementById(id);
        main.classList.remove("active");
        main.classList.add("slide-left");
        target.classList.add("active", "slide-in");
    }

    window.goBack = function () {
        const main = document.getElementById("main-faq");
        const current = document.querySelector(".faq-screen.active:not(#main-faq)");
        if (!current) return;
        current.classList.remove("active", "slide-in");
        main.classList.add("active");
        main.classList.remove("slide-left");
    };

    // FAQ Auto-Height Logic
    const updateFaqHeight = () => {
        const container = document.querySelector('.faq-container');
        const active = container?.querySelector('.faq-screen.active');
        if (container) container.style.height = active ? `${active.offsetHeight}px` : '0px';
    };

    const observer = new MutationObserver(() => updateFaqHeight());
    document.querySelectorAll('.faq-screen').forEach(el => observer.observe(el, { attributes: true }));
    updateFaqHeight();
});

/* --- Global UI Helpers --- */
function addMessage(text, sender) {
    const div = document.createElement("div");
    div.className = `${sender}-bubble`;
    div.innerText = text;
    msgContainer.appendChild(div);
    scrollToBottom();
}

function sendMessage(text) {
    text = text || input.value.trim();
    if (!text) return;
    addMessage(text, "user");
    showThinking();
    window.emitUserMessage(text); // Call networking file
    input.value = "";
}

function showThinking() {
    if (!thinking || thinking.parentNode === msgContainer) return;
    thinking.style.display = "inline-flex";
    msgContainer.appendChild(thinking);
    scrollToBottom();
}

window.replaceThinkingWithBot = function(text) {
    if (thinking && thinking.parentNode === msgContainer) {
        thinking.style.display = "none";
        msgContainer.removeChild(thinking);
    }
    addMessage(text, "chatbot");
};

function scrollToBottom() {
    const chatBody = document.getElementById("chatbox-body");
    chatBody.scrollTop = chatBody.scrollHeight;
}