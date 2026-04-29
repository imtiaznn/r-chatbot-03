// Written by Group 09
import { useState } from "react";
import Markdown from "../utils/Markdown"

const faqData: Record<string, string[]> = {
  "General": [
    "What is Cytovision?",
    "What is digital pathology?",
    "What is Whole Slide Imaging (WSI)?"
  ],
  "Products and Services": [
    "What products does Cytovision offer?",
    "What is EnvisionPath?",
    "Do I need to buy hardware to use Cytovision's services?",
  ],
  "Privacy": [
    "Is my data safe with Cytovision?",
    "Who owns the slides and data I submit?",
    "Can I delete my data after the service?",
  ],
  "Support": [
    "How do I contact Cytovision?",
    "Can I request a product demo?",
    "How do I start using Cytovision's services?"
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