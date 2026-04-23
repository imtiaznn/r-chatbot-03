import { useState } from "react";
import Markdown from "../utils/Markdown"

const faqData: Record<string, string[]> = {
  "General": [
    "What is Cytovision?",
    "How do I create an account?",
    "Is my data secure?",
    "What languages are supported?",
    "How do I reset my password?",
  ],
  "Products and Services": [
    "What products does Cytovision offer?",
    "How do I upgrade my plan?",
    "Is there a free trial?",
    "What integrations are available?",
    "How do I cancel my subscription?",
  ],
  "Contact Us": [
    "How do I reach support?",
    "What are your support hours?",
    "Where is Cytovision located?",
    "Can I request a demo?",
    "How do I submit feedback?",
  ],
};

function FaqTemplate({ onSelect }: { onSelect?: (q: string) => void }) {
  const [active, setActive] = useState<string | null>(null);

  return (
    <div className="chatbox-bubble bot">
      <Markdown content={`
## Welcome to **Cytovision**!

I'm **Cytobot**, your virtual assistant for all things Cytovision.

Ask me about our services, solutions, or support — or pick a topic below:
      `} />

    <div className="faq-panels">
        <div className={`faq-panels-inner ${active ? "slid" : ""}`}>
            <div className="faq-panel">
            <div className="faq-list">
                {Object.keys(faqData).map((cat) => (
                <button key={cat} className="faq-btn" onClick={() => setActive(cat)}>
                    {cat}
                </button>
                ))}
            </div>
            </div>

            <div className="faq-panel">
            <div className="faq-list">
              <button className="faq-btn" onClick={() => setActive(null)}>
                  ← Back
              </button>
                {active && faqData[active].map((q) => (
                <button key={q} className="faq-btn" onClick={() => onSelect?.(q)}>
                    {q}
                </button>
                ))}
            </div>
            </div>
        </div>
    </div>
    </div>
  )
}

export default FaqTemplate