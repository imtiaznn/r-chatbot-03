import { useState, useCallback, useEffect, useRef } from "react";
import { io, type Socket } from "socket.io-client"

import logo from "../../assets/cytovision-logo-white.png"
import ChatBoxHeader from "./ChatBoxHeader";
import ChatBoxBody, { type Message } from "./ChatBoxBody";
import ChatBoxInput from "./ChatBoxInput";
import ChatBoxOverlay from "./ChatBoxOverlay";

import "./ChatBox.css";


const ChatBox = () => {
  
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<Message[]>([]);
  const [userInfo, setUserInfo] = useState<{ name: string; email: string } | null>(null);

  const socket = useRef<Socket | null>(null)

  // socket.io connection
  useEffect(() => {
    socket.current = io("http://localhost:5005", { transports: ["websocket"] });

    socket.current.on("connect", () => {
      socket.current?.emit("session_request", {
        session_id: crypto.randomUUID(),
      });
    });

    socket.current.on("bot_uttered", (data) => {
      const botMsg: Message = {
        id: crypto.randomUUID(),
        text: data.text,
        sender: "bot",
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, botMsg]);
    });

    return () => {
      socket.current?.disconnect();
    };
  }, []);

  // Message handling
  const handleMessageSend = useCallback((text: string) => {

    const userMsg: Message = {
      id: crypto.randomUUID(),
      text,
      sender: "user",
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev,userMsg]);

    if (!socket.current) {
      return;
    }

    try {
      socket.current.emit("user_uttered", { message: text });
    } catch (err) {
      // swallow emit errors
      console.error("Error emitting user message:", err);
    }
  }, []);

  // CRM Form handling
  const handleFormSend = async (info) => {
    setUserInfo(info); // local state
    socket.current.emit("crm_submit", info)
  };
  
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
          <ChatBoxBody messages={messages} />
          {!userInfo && (
            <ChatBoxOverlay onSubmit={handleFormSend}/>
          )}
        </div>
      <ChatBoxInput onSend={handleMessageSend} disabled={!userInfo}/>
    </div>
  );
};

export default ChatBox;
