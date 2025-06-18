import { useState, useEffect, useReducer, useRef, useCallback } from "react";
import { useParams, useLocation, useNavigate } from "react-router-dom";

import styles from "./Session.module.css";

import TopBar from "../../components/TopBar";
import HomeButton from "../../components/HomeButton";
import LogoutButton from "../../components/LogoutButton";
import { TypeAnimation } from "react-type-animation";

import { Roles } from "../../constants";
import SidePanel from "../../components/SidePanel";

import {
  LoadingIndicator,
  InputArea,
  ChatMessage,
  ContinuePrompt,
} from "./SessionUI";

import {
  sessionReducer,
  initialState,
  ActionTypes,
  SessionState,
  GameState,
} from "./sessionMachine";

const MessageDelay = 500;
const TypingSpeed = 65;

function Session({ api, params = {}, ...props }) {
  // State for sidebar
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);

  // Get the session ID from the params or props
  const paramsFromRoute = useParams();
  const sessionId = params.sessionId || paramsFromRoute.sessionId;

  // Get the initial narrative from the props or location
  const location = useLocation();
  const initialNarrative =
    props.initialNarrative || location.state?.initialNarrative;

  const navigate = useNavigate();
  const hasInitialized = useRef(false);
  const inputRef = useRef(null);

  // For player input
  const [message, setMessage] = useState("");

  // For suggested_action submission
  const [lastSuggestedActions, setLastSuggestedActions] = useState([]);

  // Error state and tracking
  const [error, setError] = useState(null);
  const [isResetting, setIsResetting] = useState(false);

  // Clear error when message changes, unless we're in the middle of resetting it
  useEffect(() => {
    if (isResetting) {
      setIsResetting(false);
      return;
    }
    if (error) {
      setError(null);
    }
  }, [message]);

  // Use reducer for state management
  const [state, dispatch] = useReducer(sessionReducer, initialState);
  const {
    currentState,
    gameState,
    isInitializing,
    oldMessages,
    typingMessage,
  } = state;
  const messagesEndRef = useRef(null);

  // Auto-scroll to bottom when messages or state changes
  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [oldMessages, currentState]);

  // Handle typing completion
  const handleTypingComplete = useCallback(() => {
    if (state.typingMessage) {
      dispatch({ type: ActionTypes.TYPING_COMPLETE });
    }
  }, [state.typingMessage]);

  const handleContinue = async () => {
    if (currentState !== SessionState.AWAIT_CONTINUE) {
      return;
    }

    // Enter the loading state
    dispatch({ type: ActionTypes.SET_LOADING });

    // API call to get the next floor
    try {
      const response = await api.post(`/session/${sessionId}/new-floor`);
      const { narrative, suggested_actions } = response.data;

      dispatch({
        type: ActionTypes.START_TYPING,
        message: {
          role: Roles.NARRATOR,
          content: narrative,
          suggested_actions: suggested_actions,
        },
      });

      dispatch({
        type: ActionTypes.SET_GAME_STATE,
        gameState: GameState.IN_PROGRESS,
      });

      setLastSuggestedActions(suggested_actions);
    } catch (error) {
      console.error("Error getting next floor:", error);
      alert(
        `Failed to get next floor: ${
          error.response?.data?.message || error.message
        }`
      );
      navigate("/");
      return;
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    // If currently typing, skip the typing animation
    if (currentState === SessionState.TYPING) {
      handleTypingComplete();
      return;
    }

    // If currently in AWAIT_CONTINUE state, behavior like clicking the continue button
    if (currentState === SessionState.AWAIT_CONTINUE) {
      handleContinue();
      return;
    }

    // If not in AWAIT_INPUT state, ignore the submission
    if (currentState !== SessionState.AWAIT_INPUT) {
      console.error("Invalid state for submission");
      return;
    }

    // Simple client side validation
    const trimmedMessage = message.trim();
    if (!trimmedMessage) {
      setError("Please enter a message.");
      setIsResetting(true);
      setMessage(trimmedMessage);
      return;
    }

    try {
      // Set to loading state
      dispatch({ type: ActionTypes.SET_LOADING });

      // Submit POST request to server
      const response = await api.post(`/session/${sessionId}/player-input`, {
        action: trimmedMessage,
        suggested_actions: lastSuggestedActions,
      });

      const { state, events } = response.data;
      if (state === GameState.IN_PROGRESS) {
        events.at(-1).suggested_actions = response.data.suggested_actions;
      }

      events.forEach((event) => {
        dispatch({ type: ActionTypes.START_TYPING, message: event });
      });

      // Lastly, set the game state
      dispatch({ type: ActionTypes.SET_GAME_STATE, gameState: state });

      // If the last response has suggested actions, set them
      if (events.at(-1)?.suggested_actions) {
        setLastSuggestedActions(events.at(-1).suggested_actions);
      }

      // Clear TextBox
      setMessage("");
    } catch (error) {
      console.error("API Error:", error);

      // Extract status and initialize error message
      const status = error.response?.status; // Will be undefined if error.response is undefined
      let errorMessage = "An error occurred while processing your request";

      // Handle 400 Bad Request specifically
      if (status === 400 && error.response?.data?.error) {
        errorMessage = error.response.data.error;
        setError(errorMessage);
        dispatch({ type: ActionTypes.REVERT });
        return;
      }

      // For other errors, try to get the error message from the response data
      if (error.response?.data?.error) {
        errorMessage = error.response.data.error;
      } else if (error.message) {
        errorMessage = error.message;
      }

      // Set the error in the UI
      setError(errorMessage);

      // Handle different status codes
      if (status) {
        if (status === 401 || status === 403) {
          // Unauthorized or Forbidden - redirect to login
          navigate("/login");
          return;
        } else if (status >= 500) {
          // Server errors - show alert
          alert(`Server Error: ${errorMessage}`);
        }
      } else {
        // Network errors or other non-HTTP errors
        console.error("Network/Request Error:", errorMessage);
      }

      // Revert to the previous state
      dispatch({ type: ActionTypes.REVERT });
    }
  };

  // Handler for when a suggested action is clicked
  const handleActionClick = (action) => {
    setMessage(action);
    inputRef.current?.focus();
  };

  // Focus the input field and clear the message
  const focusInput = useCallback(() => {
    setMessage("");
    inputRef.current?.focus();
  }, []);

  useEffect(() => {
    const initializeSession = async () => {
      if (hasInitialized.current) return;
      hasInitialized.current = true;

      if (!api) {
        // TODO: Better Error Handling
        console.error("API client is not available");
        return;
      }

      try {
        // If we have initial narrative from navigation state (coming from PlayerCreation)
        if (initialNarrative) {
          const initialMessage = {
            role: Roles.NARRATOR,
            content: initialNarrative,
          };

          // Set initial state for new session
          dispatch({
            type: ActionTypes.SET_GAME_STATE,
            gameState: GameState.WAITING_FOR_NEXT_FLOOR,
          });

          dispatch({ type: ActionTypes.START_TYPING, message: initialMessage });
        }

        // Load existing session
        else if (sessionId) {
          const response = await api.get(`/session/${sessionId}/get-events`);

          // Add any existing messages to the chat
          if (response.data.events?.length > 0) {
            response.data.events.forEach((event) => {
              dispatch({ type: ActionTypes.ADD_MESSAGE, message: event });
            });

            // If the last response has suggested actions, set them
            if (response.data.events.at(-1)?.suggested_actions) {
              setLastSuggestedActions(
                response.data.events.at(-1).suggested_actions
              );
            }
          }

          // Set game state and determine initial session state
          const gameState = response.data.state;
          dispatch({ type: ActionTypes.SET_GAME_STATE, gameState });
          dispatch({ type: ActionTypes.IDENTIFY_STATE });
        } else {
          // TODO: Better Error Handling
          console.error("No session ID provided");
        }
      } catch (error) {
        console.error("Error initializing session:", error);
        alert(
          `Failed to initialize session: ${
            error.response?.data?.message || error.message
          }`
        );
        navigate("/");
        return;
      }

      dispatch({
        type: ActionTypes.SET_INITIALIZING,
        isInitializing: false,
      });
    };

    initializeSession();
  }, [sessionId, initialNarrative, navigate, api]);

  if (isInitializing) {
    return (
      <div className="h-screen bg-gray-900 flex items-center justify-center">
        <div className="text-white text-xl">Loading session...</div>
      </div>
    );
  }

  // Render the chat messages
  const renderMessages = () => {
    return (
      <div className="space-y-2">
        {oldMessages.map((msg, index) => {
          return (
            <ChatMessage
              key={`msg-${index}`}
              role={msg.role}
              content={msg.content}
              suggested_actions={msg.suggested_actions}
              isLastEvent={index === oldMessages.length - 1}
              onActionClick={handleActionClick}
              onFocusInput={focusInput}
            />
          );
        })}

        {currentState === SessionState.TYPING && (
          <ChatMessage
            role={typingMessage.role}
            content={
              <TypeAnimation
                key={typingMessage.content} // Force re-render when content changes
                sequence={[
                  typingMessage.content,
                  MessageDelay,
                  handleTypingComplete,
                ]}
                wrapper="span"
                speed={TypingSpeed}
                cursor={true}
              />
            }
          />
        )}

        {currentState === SessionState.AWAIT_CONTINUE && (
          <ContinuePrompt onClick={handleContinue} />
        )}

        {currentState === SessionState.LOADING && <LoadingIndicator />}

        {gameState === GameState.COMPLETED &&
          currentState === SessionState.COMPLETED && (
            <ChatMessage
              role={Roles.NARRATOR}
              content="You are defeated. The game is over. Good luck next time!"
            />
          )}

        <div ref={messagesEndRef} />
      </div>
    );
  };

  // Render loading state
  if (isInitializing) {
    return (
      <div className="h-screen bg-gray-900 flex items-center justify-center">
        <div className="text-white text-xl">Loading session...</div>
      </div>
    );
  }

  return (
    <div className="h-screen bg-gray-900 flex flex-col overflow-hidden">
      <TopBar>
        <HomeButton size="sm" />
        <LogoutButton size="sm" />
      </TopBar>

      <SidePanel
        isOpen={isSidebarOpen}
        onToggle={setIsSidebarOpen}
        sessionId={sessionId}
        api={api}
      />

      <div className="flex-1 overflow-hidden">
        <div className="container mx-auto h-full p-4 max-w-4xl flex flex-col">
          <div className="bg-gray-800 rounded-lg p-6 flex flex-col h-full">
            {/* Chat history */}
            <div
              className={`${styles.chatHistory} flex-1 overflow-y-auto mb-4`}>
              <div className="w-full">
                {oldMessages.length === 0 && !typingMessage ? (
                  <div className="text-gray-400 text-center py-8">
                    No messages yet. Start the conversation!
                  </div>
                ) : (
                  renderMessages()
                )}
              </div>
            </div>

            {/* Input area */}
            <div className="mt-4">
              <InputArea
                state={currentState}
                message={message}
                onMessageChange={setMessage}
                onSubmit={handleSubmit}
                onContinue={handleContinue}
                inputRef={inputRef}
                error={error}
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Session;
