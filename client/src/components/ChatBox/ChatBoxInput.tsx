import { useState } from "react";
import { Send } from "lucide-react";

interface ChatBoxInputProps {
  onSend: (text: string) => void;
}

const ChatBoxInput = ({ onSend }: ChatBoxInputProps) => {
  const [value, setValue] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const trimmed = value.trim();
    if (!trimmed) return;
    onSend(trimmed);
    setValue("");
  };

  return (
    <form onSubmit={handleSubmit} className="chatbox-input-form">
      <input
        type="text"
        value={value}
        onChange={(e) => setValue(e.target.value)}
        placeholder="Type a message..."
        className="chatbox-input"
      />
      <button type="submit" disabled={!value.trim()} className="chatbox-send-btn" aria-label="Send">
        <Send size={16} />
      </button>
    </form>
  );
};

export default ChatBoxInput;
