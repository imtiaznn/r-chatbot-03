import { useEffect, useRef } from "react";

export interface Message {
  id: string;
  text: string;
  sender: "user" | "bot";
  timestamp: Date;
}

interface ChatBoxBodyProps {
  messages: Message[];
}

const ChatBoxBody = ({ messages }: ChatBoxBodyProps) => {
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  return (
    <div className="chatbox-body">
      {messages.length === 0 && (
        <p className="chatbox-empty">No messages yet. Say hello!</p>
      )}
      
      {/* Show bubble for each message item */}
      {messages.map((msg) => (
        <div key={msg.id} className={`chatbox-message-row ${msg.sender}`}>
          <div className={`chatbox-bubble ${msg.sender}`}>{msg.text}</div>
        </div>
      ))}

    <div ref={bottomRef} />

    </div>
  );
};

export default ChatBoxBody;
