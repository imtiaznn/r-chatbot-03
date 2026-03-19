import { useEffect, useRef } from "react";
import Markdown from "../utils/Markdown";

export interface Message {
  id: string;
  text: string;
  sender: "user" | "bot";
  timestamp: Date;
}

interface ChatBoxBodyProps {
  messages: Message[];
  isTyping: boolean;
}

const ChatBoxBody = ({ messages, isTyping }: ChatBoxBodyProps) => {
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isTyping]);

  return (
    <div className="chatbox-body">
      {messages.length === 0 && (
        <p className="chatbox-empty">No messages yet. Say hello!</p>
      )}
      
      {/* Show bubble for each message item */}
      {messages.map((msg) => (
        <div key={msg.id} className={`chatbox-message-row ${msg.sender}`}>
          <div className={`chatbox-bubble ${msg.sender}`}>
            <Markdown content={msg.text} />
          </div>
        </div>
      ))}

      {isTyping && (
        <div className="chatbox-message-row bot">
          <div className="chatbox-bubble bot typing-indicator">
            <span></span>
            <span></span>
            <span></span>
          </div>
        </div>
      )}

      <div ref={bottomRef} />

    </div>
  );
};

export default ChatBoxBody;
