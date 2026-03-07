import { useState } from "react";

interface ChatBoxOverlayProps {
  onSubmit: (info: { name: string; email: string }) => void;
}

const ChatBoxOverlay = ({ onSubmit }: ChatBoxOverlayProps) => {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (name.trim() && email.trim()) {
      onSubmit({ name: name.trim(), email: email.trim() });
    }
  };

  return (
    <div className="chatbox-overlay">
      <form className="chatbox-overlay-form" onSubmit={handleSubmit}>
        <p className="chatbox-overlay-hello">Hello! 👋</p>
        <p className="chatbox-overlay-subtitle">Please introduce yourself to start chatting.</p>
        <input
          type="text"
          placeholder="Your name"
          value={name}
          onChange={(e) => setName(e.target.value)}
          className="chatbox-overlay-input"
          required
          maxLength={100}
        />
        <input
          type="email"
          placeholder="Your email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          className="chatbox-overlay-input"
          required
          maxLength={255}
        />
        <button type="submit" className="chatbox-overlay-btn" disabled={!name.trim() || !email.trim()}>
          Start Chat
        </button>
      </form>
    </div>
  );
};

export default ChatBoxOverlay;