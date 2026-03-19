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
  const [isTyping, setIsTyping] = useState(false);
  const [messages, setMessages] = useState<Message[]>([]);
  const [userInfo, setUserInfo] = useState<{ name: string; email: string } | null>(null);

  const socket = useRef<Socket | null>(null)

  // Minimum typing indicator display (ms)
  const MIN_TYPING_DURATION = 500;
  const typingStartRef = useRef<number | null>(null);
  const typingTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

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

      // Start message sending to user
      const start = typingStartRef.current;
      if (!start) {
        setIsTyping(false);
        setMessages((prev) => [...prev, botMsg]);
        return;
      }

      const elapsed = Date.now() - start;
      const remaining = MIN_TYPING_DURATION - elapsed;

      // Finish message sending to user
      const finish = () => {
        setIsTyping(false);
        setMessages((prev) => [...prev, botMsg]);
        typingTimerRef.current = null;
      };

      if (remaining <= 0) {
        finish();
      } else {
        if (typingTimerRef.current) {
          clearTimeout(typingTimerRef.current);
        }
        typingTimerRef.current = setTimeout(finish, remaining);
      }

    });

    return () => {
      socket.current?.disconnect();
      if (typingTimerRef.current) {
        clearTimeout(typingTimerRef.current);
        typingTimerRef.current = null;
      }
    };
  }, []);

  // Message handling
  const handleMessageSend = useCallback((text: string) => {

    // mark typing started and show indicator
    setIsTyping(true)
    typingStartRef.current = Date.now();
    if (typingTimerRef.current) {
      clearTimeout(typingTimerRef.current);
      typingTimerRef.current = null;
    }

    const userMsg: Message = {
      id: crypto.randomUUID(),
      text,
      sender: "user",
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev,userMsg]);

    // If the socket isn't connected
    if (!socket.current || !socket.current.connected) {
      const botMsg: Message = {
        id: crypto.randomUUID(),
        text: `Error retrieving response ☹️`,
        sender: "bot",
        timestamp: new Date(),
      };

      // // Simulate the typing indicator for at least MIN_TYPING_DURATION
      // const start = typingStartRef.current;
      // if (!start) {
      //   setIsTyping(false);
      //   setMessages((prev) => [...prev, botMsg]);
      // } else {
      //   const elapsed = Date.now() - start;
      //   const remaining = MIN_TYPING_DURATION - elapsed;

      //   const finish = () => {
      //     setIsTyping(false);
      //     setMessages((prev) => [...prev, botMsg]);
      //     typingTimerRef.current = null;
      //   };

      //   if (remaining <= 0) {
      //     finish();
      //   } else {
      //     if (typingTimerRef.current) {
      //       clearTimeout(typingTimerRef.current);
      //     }
      //     typingTimerRef.current = setTimeout(finish, remaining);
      //   }
      // }

      return;
    }

    try {
      socket.current.emit("user_uttered", { message: text });
    } catch (err) {
      console.error("Error emitting user message:", err);
    }
  }, []);

  // Access Form handling
  const handleFormSend = async (info) => {
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

          <ChatBoxBody messages={messages} isTyping={isTyping}/>

          {!userInfo && (
            <ChatBoxOverlay onSubmit={handleFormSend}/>
          )}
          
        </div>

      <ChatBoxInput onSend={handleMessageSend} disabled={!userInfo}/>
    </div>
  );
};

export default ChatBox;
