import React from "react";
import { SessionState } from "./sessionMachine";
import { ActionPromptButton } from "../../components/ActionPromptButton";

export const LoadingIndicator = () => (
  <div className="flex items-center justify-center py-4">
    <div className="flex items-center space-x-2 text-gray-400">
      <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-blue-500"></div>
      <span>Processing...</span>
    </div>
  </div>
);

export const InputArea = ({
  state,
  message,
  onMessageChange,
  onSubmit,
  inputRef,
  error,
}) => {
  const isDisabled = state !== SessionState.AWAIT_INPUT;
  const isLoading = state === SessionState.LOADING;

  const getPlaceholder = () => {
    switch (state) {
      case SessionState.TYPING:
        return "Please wait...";
      case SessionState.AWAIT_INPUT:
        return "Type your action...";
      case SessionState.AWAIT_CONTINUE:
        return "Click the continue button";
      default:
        return "You are defeated.";
    }
  };

  const getButtonConfig = () => {
    switch (state) {
      case SessionState.TYPING:
        return { text: "Skip", className: "bg-gray-500 hover:bg-gray-600" };
      case SessionState.AWAIT_INPUT:
        return { text: "Send", className: "bg-green-600 hover:bg-green-700" };
      case SessionState.AWAIT_CONTINUE:
        return { text: "Continue", className: "bg-blue-600 hover:bg-blue-700" };
      case SessionState.LOADING:
        return {
          text: "Loading...",
          className: "bg-blue-600 cursor-wait opacity-75",
        };
      default:
        return { text: "✓", className: "bg-gray-500 cursor-not-allowed" };
    }
  };

  const buttonConfig = getButtonConfig();
  const isButtonDisabled = [
    SessionState.COMPLETED,
    SessionState.LOADING,
  ].includes(state);

  return (
    <div className="border-t border-gray-700 pt-4">
      {error && (
        <div className="flex items-center text-red-400 text-sm mb-2 px-3 py-2 bg-red-900/50 rounded-lg">
          <svg className="w-5 h-5 mr-2 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.28 7.22a.75.75 0 00-1.06 1.06L8.94 10l-1.72 1.72a.75.75 0 101.06 1.06L10 11.06l1.72 1.72a.75.75 0 101.06-1.06L11.06 10l1.72-1.72a.75.75 0 00-1.06-1.06L10 8.94 8.28 7.22z" clipRule="evenodd" />
          </svg>
          {error}
        </div>
      )}
      <form onSubmit={onSubmit} className="flex gap-2">
        <div className={`flex-1 relative ${error ? 'ring-2 ring-red-500 rounded-lg' : ''}`}>
          <input
            ref={inputRef}
            type="text"
            value={message}
            onChange={(e) => onMessageChange(e.target.value)}
            disabled={isDisabled || isLoading}
            className={`w-full bg-gray-700 text-white px-4 py-2 focus:outline-none focus:ring-2 ${
              isLoading
                ? "cursor-wait"
                : isDisabled
                ? "cursor-not-allowed"
                : error ? "focus:ring-red-500" : "focus:ring-green-500"
            } opacity-${isDisabled || isLoading ? 50 : 100} ${error ? 'border-red-500' : 'border-transparent'} rounded-lg`}
            placeholder={getPlaceholder()}
          />
        </div>
        <button
          type="submit"
          disabled={isButtonDisabled}
          className={`font-bold py-2 px-6 rounded flex items-center justify-center min-w-[100px] text-white ${buttonConfig.className}`}>
          {isLoading && (
            <svg
              className="animate-spin -ml-1 mr-2 h-4 w-4 text-white"
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24">
              <circle
                className="opacity-25"
                cx="12"
                cy="12"
                r="10"
                stroke="currentColor"
                strokeWidth="4"></circle>
              <path
                className="opacity-75"
                fill="currentColor"
                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
          )}
          {buttonConfig.text}
        </button>
      </form>
    </div>
  );
};

export function SuggestedActions({
  actions,
  disabled,
  onActionClick,
  onFocusInput,
}) {
  return (
    <div className="mt-2">
      <div className="text-gray-300 mb-1">What do you want to do?</div>
      <div className="flex flex-col space-y-1">
        {actions.map((action, index) => (
          <ActionPromptButton
            key={`action-${index}`}
            action={action}
            index={index}
            disabled={disabled}
            onClick={() => onActionClick?.(action)}
          />
        ))}
        <ActionPromptButton
          key="next-floor"
          action="Go to the next floor"
          index={actions.length}
          disabled={disabled}
          onClick={() => onActionClick?.("Go to the next floor")}
        />
        <ActionPromptButton
          key="custom-action"
          action="Write your own action"
          index={actions.length + 1}
          disabled={disabled}
          onClick={onFocusInput}
        />
      </div>
    </div>
  );
}

export const ChatMessage = ({
  role,
  content,
  suggested_actions,
  isLastEvent,
  onActionClick,
  onFocusInput,
  isActionPrompt,
  isActionItem,
  children, // Add children to the destructured props
}) => {
  // If this is an action prompt or item, we'll handle it differently
  if (isActionPrompt || isActionItem) {
    return null; // We'll handle these in the parent component
  }

  return (
    <div className="grid grid-cols-12 gap-2 text-white">
      <div className="col-span-2 font-medium text-green-400 break-words">
        {role}
      </div>
      <div className="col-span-10 break-words">
        {content}
        {children}
        {suggested_actions && (
          <div className="mt-2">
            <SuggestedActions
              actions={suggested_actions}
              disabled={!isLastEvent}
              onActionClick={onActionClick}
              onFocusInput={onFocusInput}
            />
          </div>
        )}
      </div>
    </div>
  );
};

export const ContinuePrompt = ({ onClick }) => (
  <ChatMessage role="System">
    <button
      onClick={onClick}
      className="text-blue-400 hover:text-blue-300 underline cursor-pointer focus:outline-none">
      Click here to continue
    </button>
  </ChatMessage>
);
