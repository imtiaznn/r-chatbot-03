import { useState, useCallback, useEffect, useRef } from "react";
import { io, type Socket } from "socket.io-client"

import logo from "../../assets/cytovision-logo-white.png"
import ChatBoxHeader from "./ChatBoxHeader";
import ChatBoxBody, { type Message } from "./ChatBoxBody";
import ChatBoxInput from "./ChatBoxInput";
import ChatBoxOverlay from "./ChatBoxOverlay";

import "./ChatBox.css";
import FaqTemplate from "./FaqTemplate";

const ChatBox = () => {
  
  const [isOpen, setIsOpen] = useState(false);
  const [isTyping, setIsTyping] = useState(false);
  const [messages, setMessages] = useState<Message[]>([]);
  const [userInfo, setUserInfo] = useState<{ name: string; email: string } | null>(null);

  const socket = useRef<Socket | null>(null)

  // Minimum typing indicator display (ms)
  const MIN_TYPING_DURATION = 500;
  const typingStartRef = useRef<number | null>(null);
  const typingTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

// Centralized socket event emitter
  const emitSocketEvent = useCallback((event: string, data: unknown) => {
    if (!socket.current?.connected) {
      console.warn(`Socket not connected. Cannot emit "${event}".`);
      return false;
    }

    try {
      socket.current.emit(event, data);
      return true;
    } catch (err) {
      console.error(`Error emitting "${event}":`, err);
      return false;
    }
  }, []);

  useEffect(() => {
    // Socket connection handling
    socket.current = io("http://localhost:5005", { transports: ["websocket"] });

    socket.current.on("connect", () => {
      emitSocketEvent("session_request", { session_id: crypto.randomUUID() });
    });

    socket.current.on("bot_uttered", (data) => {
      const botMsg: Message = {
        id: crypto.randomUUID(),
        text: data.text,
        sender: "bot",
        timestamp: new Date(),
      };

      // Message handling, typing indicator timer
      const start = typingStartRef.current;
      if (!start) {
        setIsTyping(false);
        setMessages((prev) => [...prev, botMsg]);
        return;
      }

      const elapsed = Date.now() - start;
      const remaining = MIN_TYPING_DURATION - elapsed;

      const finish = () => {
        setIsTyping(false);
        setMessages((prev) => [...prev, botMsg]);
        typingTimerRef.current = null;
      };

      if (remaining <= 0) {
        finish();
      } else {
        if (typingTimerRef.current) clearTimeout(typingTimerRef.current);
        typingTimerRef.current = setTimeout(finish, remaining);
      }

    });

    // Socket disconnect
    return () => {
      socket.current?.disconnect();
      if (typingTimerRef.current) {
        clearTimeout(typingTimerRef.current);
        typingTimerRef.current = null;
      }
    };
  }, [emitSocketEvent]);

  // Message handling
  const handleMessageSend = useCallback((text: string) => {
    const userMsg: Message = {
      id: crypto.randomUUID(),
      text: text,
      sender: "user",
      timestamp: new Date(),
    };
    setMessages((prev) => [...prev, userMsg]);

    const sent = emitSocketEvent("user_uttered", { text: text });

    if (!sent) {
      emitSocketEvent("error", { type: "Could not send message to server" })
      console.error("Could not send message to server")
      return;
    }

    // Mark typing started and show indicator
    setIsTyping(true);
    typingStartRef.current = Date.now();
    if (typingTimerRef.current) {
      clearTimeout(typingTimerRef.current);
      typingTimerRef.current = null;
    }
  }, [emitSocketEvent]);

  // Access Form handling
  const handleFormSend = async (info: any) => {
    setUserInfo(info); // local state
    socket.current.emit("access_form_submit", info)
  };
  
  // Chatbox Open Toggle
  if (!isOpen) {
    return (
      <button onClick={() => setIsOpen(true)} className="chatbox-toggle" aria-label="Open chat">
        <img src={logo} alt="Cytovision logo" className="chatbox-toggle-logo"/>
      </button>
    );
  }

  return (
    <div className="chatbox-container">
      <ChatBoxHeader onClose={() => setIsOpen(false)} onMinimize={() => setIsOpen(false)} />
        
        <div className="chatbox-body-wrapper">

          <ChatBoxBody messages={messages} isTyping={isTyping} onFaqSelect={handleMessageSend}/>

          {!userInfo && (
            <ChatBoxOverlay onSubmit={handleFormSend}/>
          )}
          
        </div>

      <ChatBoxInput onSend={handleMessageSend} disabled={!userInfo}/>
    </div>
  );
};

export default ChatBox;
