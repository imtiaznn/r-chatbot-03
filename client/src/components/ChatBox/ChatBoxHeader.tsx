import { MessageSquare, X, Minus } from "lucide-react";

interface ChatBoxHeaderProps {
  onClose: () => void;
  onMinimize: () => void;
}

const ChatBoxHeader = ({ onClose, onMinimize }: ChatBoxHeaderProps) => {
  return (
    <div className="chatbox-header">
      <div className="chatbox-header-title">
        <MessageSquare size={18} />
        <span>Cytobot</span>
      </div>
      <div className="chatbox-header-actions">
        <button onClick={onMinimize} className="chatbox-header-btn" aria-label="Minimize">
          <Minus size={16} />
        </button>
        <button onClick={onClose} className="chatbox-header-btn" aria-label="Close">
          <X size={16} />
        </button>
      </div>
    </div>
  );
};

export default ChatBoxHeader;
