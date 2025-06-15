import { useState } from "react";
import { TypeAnimation } from "react-type-animation";

export default function TestTypeAnimation() {
  const [isAnimating, setIsAnimating] = useState(true);
  const [messages, setMessages] = useState([
    "We produce food for Mice",
    "We are the best mouse food producers",
  ]);
  const [displayedMessages, setDisplayedMessages] = useState([]);
  const currentMessage = messages[displayedMessages.length];

  const handleAnimationComplete = () => {
    setDisplayedMessages((prev) => [...prev, currentMessage]);
    if (displayedMessages.length < messages.length - 1) {
      // If there are more messages, reset animation for the next one
      setIsAnimating(false);
      setTimeout(() => setIsAnimating(true), 0);
    } else {
      // No more messages, stop animating
      setIsAnimating(false);
    }
  };

  return (
    <>
      {displayedMessages.map((message, index) => (
        <div key={index} style={{ fontSize: "2em" }}>
          {message}
        </div>
      ))}

      {isAnimating && currentMessage && (
        <TypeAnimation
          key={displayedMessages.length}
          sequence={[currentMessage, handleAnimationComplete]}
          wrapper="span"
          style={{ fontSize: "2em" }}
          cursor={true}
        />
      )}

      {!isAnimating && !currentMessage && <div>All messages displayed!</div>}
    </>
  );
}
