import { useState, useEffect, useReducer, useRef, useCallback } from "react";
import { useParams, useLocation, useNavigate } from "react-router-dom";
import api from "../../api";

import styles from "./Session.module.css";

import TopBar from "../../components/TopBar";
import HomeButton from "../../components/HomeButton";
import LogoutButton from "../../components/LogoutButton";

import TypingText, { Roles } from "../../components/TypingText";

export const GameState = {
  IN_PROGRESS: "In Progress",
  WAITING_FOR_NEXT_FLOOR: "Waiting for Next Floor",
  COMPLETED: "Completed",
};

// Define our state machine states
export const SessionState = {
  TYPING: 'typing',
  AWAIT_CONTINUE: 'awaitContinue',
  AWAIT_INPUT: 'awaitInput',
  COMPLETE: 'complete'
};

// State machine reducer
function sessionReducer(state, action) {
  switch (action.type) {
    case 'START_TYPING':
      return { ...state, currentState: SessionState.TYPING, typingMessage: action.message };

    case 'SKIP_TYPING':
      return { ...state, skipTyping: true };

    case 'TYPING_COMPLETE':
      const nextState = { ...state, typingMessage: null, skipTyping: false };

      // Determine next state based on game state
      if (state.gameState === GameState.WAITING_FOR_NEXT_FLOOR) {
        nextState.currentState = SessionState.AWAIT_CONTINUE;
      } else if (state.gameState === GameState.IN_PROGRESS) {
        nextState.currentState = SessionState.AWAIT_INPUT;
      } else {
        nextState.currentState = SessionState.COMPLETE;
      }
      return nextState;

    case 'CONTINUE_PRESSED':
      return { ...state, currentState: SessionState.AWAIT_INPUT };

    case 'SET_GAME_STATE':
      return { ...state, gameState: action.gameState };

    case 'SET_LOADING':
      return { ...state, isLoading: action.isLoading };

    case 'ADD_MESSAGE':
      return { ...state, oldMessages: [...state.oldMessages, action.message] };

    default:
      return state;
  }
}

// Initial state for our reducer
const initialState = {
  currentState: SessionState.TYPING,
  gameState: null,
  isLoading: true,
  oldMessages: [],
  typingMessage: null,
  skipTyping: false
};

function Session() {
  const { sessionId } = useParams();
  const location = useLocation();
  const navigate = useNavigate();
  const hasInitialized = useRef(false);

  const [message, setMessage] = useState("");
  
  // Use reducer for state management
  const [state, dispatch] = useReducer(sessionReducer, initialState);
  const { currentState, isLoading, oldMessages, typingMessage, skipTyping } = state;
  
  // Memoized handler for typing completion
  const handleTypingComplete = useCallback(() => {
    if (typingMessage) {
      dispatch({ type: 'ADD_MESSAGE', message: typingMessage });
      dispatch({ type: 'TYPING_COMPLETE' });
    }
  }, [typingMessage]);

  const handleSubmit = async (e) => {
    e.preventDefault();

    // If currently typing, skip the typing animation
    if (currentState === SessionState.TYPING) {
      dispatch({ type: 'SKIP_TYPING' });
      return;
    }

    // If not in AWAIT_INPUT state, ignore the submission
    if (currentState !== SessionState.AWAIT_INPUT) return;

    const trimmedMessage = message.trim();
    if (!trimmedMessage) return;

    // Add user message to messages
    const userMessage = { role: Roles.PLAYER, content: trimmedMessage };
    dispatch({ type: 'ADD_MESSAGE', message: userMessage });
    setMessage("");

    // Simulate AI response (replace with actual API call)
    setTimeout(() => {
      const aiResponse = {
        role: Roles.NARRATOR,
        content: "This is a simulated AI response. In a real app, this would come from your backend.",
      };
      dispatch({ type: 'START_TYPING', message: aiResponse });
    }, 500);

    try {
      // TODO: Send message to server
      // const response = await api.post(`/session/${sessionId}/message`, {
      //   message: trimmedMessage
      // });
      // if (response.data.response) {
      //   const aiResponse = {
      //     role: Roles.NARRATOR,
      //     content: response.data.response
      //   };
      //   dispatch({ type: 'START_TYPING', message: aiResponse });
      // }
    } catch (error) {
      console.error("Error sending message:", error);
      // Optionally show error to user
    }
  };

  const handleContinue = () => {
    if (currentState === SessionState.AWAIT_CONTINUE) {
      dispatch({ type: 'CONTINUE_PRESSED' });
      
      // Here you would typically load the next floor/message
      // For now, we'll just simulate it
      setTimeout(() => {
        const nextMessage = {
          role: Roles.NARRATOR,
          content: "The adventure continues..."
        };
        dispatch({ type: 'START_TYPING', message: nextMessage });
      }, 500);
    }
  };

  useEffect(() => {
    const initializeSession = async () => {
      if (hasInitialized.current) return;
      hasInitialized.current = true;

      // If we have initial narrative from navigation state, use it
      if (location.state?.initialNarrative) {
        const initialMessage = {
          role: Roles.NARRATOR,
          content: location.state.initialNarrative,
        };
        dispatch({ type: 'START_TYPING', message: initialMessage });
        dispatch({ type: 'SET_GAME_STATE', gameState: GameState.WAITING_FOR_NEXT_FLOOR });

      } else if (sessionId) {
        // Otherwise, load session data if we have a sessionId
        try {
          const response = await api.get(`/session/${sessionId}/get-events`);
          dispatch({ type: 'ADD_MESSAGE', message: response.data.events });
          dispatch({ type: 'SET_GAME_STATE', gameState: response.data.state });
          
          // If no initial message, go to input state
          if (response.data.events.length === 0) {
            dispatch({ type: 'TYPING_COMPLETE' });
          }
        } catch (error) {
          console.error("Error loading session:", error);
          alert(
            `Failed to load session: ${
              error.response?.data?.message || error.message
            }`
          );
          navigate("/");
          return;
        }
      }

      dispatch({ type: 'SET_LOADING', isLoading: false });
    };

    initializeSession();
  }, [sessionId, location.state, navigate]);

  if (isLoading) {
    return (
      <div className="h-screen bg-gray-900 flex items-center justify-center">
        <div className="text-white text-xl">Loading session...</div>
      </div>
    );
  }

  return (
    <div className="h-screen bg-gray-900 flex flex-col overflow-hidden">
      <TopBar>
        <HomeButton />
        <LogoutButton />
      </TopBar>

      <div className="flex-1 overflow-hidden">
        <div className="container mx-auto h-full p-4 max-w-4xl flex flex-col">
          <div className="bg-gray-800 rounded-lg p-6 flex flex-col h-full">
            {/* Chat history */}
            <div
              className={`${styles.chatHistory} flex-1 overflow-y-auto mb-4`}>
              <div className="w-full">
                {isLoading ? (
                  <div className="text-gray-400 text-center py-4">
                    Loading chat history...
                  </div>
                ) : (
                  <>
                    {/* Messages */}
                    <div className="space-y-2">
                      {oldMessages.map((msg, index) => (
                        <div
                          key={`old-${index}`}
                          className="grid grid-cols-12 gap-2 text-white">
                          <div className="col-span-2 font-medium text-green-400 break-words">
                            {msg.role}
                          </div>
                          <div className="col-span-10 break-words">
                            {msg.content}
                          </div>
                        </div>
                      ))}

                      {/* Typing message */}
                      {currentState === SessionState.TYPING && typingMessage && (
                        <div className="grid grid-cols-12 gap-2 text-white">
                          <div className="col-span-2 font-medium text-green-400 break-words">
                            {typingMessage.role}
                          </div>
                          <div className="col-span-10 break-words">
                            <TypingText
                              text={typingMessage.content}
                              role={typingMessage.role}
                              skipTyping={skipTyping}
                              onTypingComplete={handleTypingComplete}
                            />
                          </div>
                        </div>
                      )}

                      {/* Continue button */}
                      {currentState === SessionState.AWAIT_CONTINUE && (
                        <div className="grid grid-cols-12 gap-2 text-white">
                          <div className="col-span-2 font-medium text-green-400">
                            System
                          </div>
                          <div className="col-span-10">
                            <button
                              onClick={handleContinue}
                              className="text-blue-400 hover:text-blue-300 underline cursor-pointer focus:outline-none">
                              Click here to continue
                            </button>
                          </div>
                        </div>
                      )}
                    </div>
                  </>
                )}
              </div>
            </div>

            {/* Input area */}
            <div className="border-t border-gray-700 pt-4">
              <form onSubmit={handleSubmit} className="flex gap-2">
                <input
                  type="text"
                  value={message}
                  onChange={(e) => setMessage(e.target.value)}
                  disabled={currentState !== SessionState.AWAIT_INPUT}
                  className={`flex-1 bg-gray-700 text-white rounded px-4 py-2 focus:outline-none focus:ring-2 ${
                    currentState !== SessionState.AWAIT_INPUT
                      ? "opacity-50 cursor-not-allowed"
                      : "focus:ring-green-500"
                  }`}
                  placeholder={
                    currentState === SessionState.TYPING 
                      ? "Please wait..." 
                      : currentState === SessionState.AWAIT_INPUT 
                        ? "Type your message..."
                        : currentState === SessionState.AWAIT_CONTINUE
                          ? "Click the continue button above"
                          : "Game complete"
                  }
                />
                <button
                  type="submit"
                  className={`font-bold py-2 px-6 rounded ${
                    currentState === SessionState.TYPING
                      ? "bg-gray-500 hover:bg-gray-600 text-white"
                      : currentState === SessionState.AWAIT_INPUT
                        ? "bg-green-600 hover:bg-green-700 text-white"
                        : "bg-gray-500 cursor-not-allowed"
                  }`}
                  disabled={currentState !== SessionState.TYPING && currentState !== SessionState.AWAIT_INPUT}>
                  {currentState === SessionState.TYPING 
                    ? "Skip" 
                    : currentState === SessionState.AWAIT_INPUT 
                      ? "Send"
                      : "✓"
                  }
                </button>
              </form>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Session;
