import { useState, useEffect, useRef, useCallback } from "react";
import { Roles } from "../constants";

const TypingText = ({
  text,
  interval = 30,
  role,
  onTypingComplete,
  skipTyping = false,
}) => {
  const [displayText, setDisplayText] = useState("");
  const [isTyping, setIsTyping] = useState(true);
  const textRef = useRef("");
  const intervalRef = useRef();

  const completeTyping = useCallback(() => {
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }
    setDisplayText(text);
    textRef.current = text;
    setIsTyping(false);
    onTypingComplete?.();
  }, [text, onTypingComplete]);

  useEffect(() => {
    if (role === Roles.PLAYER) {
      setDisplayText(text);
      setIsTyping(false);
      return;
    }

    setDisplayText("");
    textRef.current = "";
    setIsTyping(true);

    if (text) {
      let i = 0;
      intervalRef.current = setInterval(() => {
        if (i < text.length) {
          textRef.current = text.substring(0, i + 1);
          setDisplayText(textRef.current);
          i++;
        } else {
          completeTyping();
        }
      }, interval);
    }

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, [text, interval, role, completeTyping]);

  useEffect(() => {
    if (skipTyping && isTyping) {
      completeTyping();
    }
  }, [skipTyping, isTyping, completeTyping]);

  return <span>{displayText}</span>;
};

export default TypingText;
