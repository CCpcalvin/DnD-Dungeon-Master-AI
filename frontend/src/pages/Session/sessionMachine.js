// Session-specific state machine enums
export const SessionState = {
  TYPING: "TYPING",
  AWAIT_INPUT: "AWAIT_INPUT",
  AWAIT_CONTINUE: "AWAIT_CONTINUE",
  LOADING: "LOADING",
  COMPLETED: "COMPLETED",
};

export const GameState = {
  WAITING_FOR_NEXT_FLOOR: "Waiting for Next Floor",
  IN_PROGRESS: "In Progress",
  COMPLETED: "Completed",
};

export const initialState = {
  currentState: null,
  previousState: null,
  gameState: null,
  isInitializing: true,
  oldMessages: [],
  typingMessage: null,
  typingQueue: [], // Queue of messages to type out next
};

export const ActionTypes = {
  SET_SESSION_STATE: "SET_SESSION_STATE",
  REVERT: "REVERT",
  SET_LOADING: "SET_LOADING",
  SET_GAME_STATE: "SET_GAME_STATE",
  SET_INITIALIZING: "SET_INITIALIZING",
  START_TYPING: "START_TYPING",
  TYPING_COMPLETE: "TYPING_COMPLETE",
  IDENTIFY_STATE: "IDENTIFY_STATE",
  ADD_MESSAGE: "ADD_MESSAGE",
};

export function createAction(type, payload) {
  return { type, ...payload };
}

export function sessionReducer(state, action) {
  switch (action.type) {
    case ActionTypes.SET_SESSION_STATE: {
      return {
        ...state,
        currentState: action.currentState,
        previousState: state.currentState,
      };
    }

    case ActionTypes.REVERT: {
      if (!state.previousState) {
        console.warn("No previous state to revert to");
        return state;
      }
      // Go back to previous state and clear the previousState to prevent double-reverts
      return {
        ...state,
        currentState: state.previousState,
        previousState: null, // Clear previous state to prevent chained reverts
      };
    }

    case ActionTypes.START_TYPING: {
      const newQueue = [...state.typingQueue];
      if (state.currentState === SessionState.TYPING && state.typingMessage) {
        // If we're already typing, add to queue
        newQueue.push(action.message);
        return {
          ...state,
          typingQueue: newQueue,
        };
      }

      return {
        ...state,
        currentState: SessionState.TYPING,
        previousState: state.currentState,
        typingMessage: action.message,
        typingQueue: newQueue,
      };
    }

    case ActionTypes.TYPING_COMPLETE: {
      // If there's an active typing message, add it to oldMessages
      const updatedOldMessages = state.typingMessage
        ? [...state.oldMessages, state.typingMessage]
        : [...state.oldMessages];

      // Check if we have more messages in the queue
      if (state.typingQueue.length > 0) {
        // Process next message in queue
        const [nextMessage, ...remainingQueue] = state.typingQueue;

        return {
          ...state,
          oldMessages: updatedOldMessages,
          typingMessage: nextMessage,
          typingQueue: remainingQueue,
        };
      }

      // No more messages, proceed to next state
      const nextState = {
        ...state,
        oldMessages: updatedOldMessages,
        typingMessage: null,
        typingQueue: [],
      };

      // Determine next state based on game state
      return sessionReducer(nextState, {
        type: ActionTypes.IDENTIFY_STATE,
      });
    }

    case ActionTypes.IDENTIFY_STATE: {
      // Determine next state based on game state
      if (state.gameState === GameState.WAITING_FOR_NEXT_FLOOR) {
        return sessionReducer(state, {
          type: ActionTypes.SET_SESSION_STATE,
          currentState: SessionState.AWAIT_CONTINUE,
        });
      } else if (state.gameState === GameState.IN_PROGRESS) {
        return sessionReducer(state, {
          type: ActionTypes.SET_SESSION_STATE,
          currentState: SessionState.AWAIT_INPUT,
        });
      } else {
        return sessionReducer(state, {
          type: ActionTypes.SET_SESSION_STATE,
          currentState: SessionState.COMPLETED,
        });
      }
    }

    case ActionTypes.SET_LOADING:
      return sessionReducer(state, {
        type: ActionTypes.SET_SESSION_STATE,
        currentState: SessionState.LOADING,
      });

    case ActionTypes.SET_GAME_STATE:
      return { ...state, gameState: action.gameState };

    case ActionTypes.SET_INITIALIZING:
      return { ...state, isInitializing: action.isInitializing };

    case ActionTypes.ADD_MESSAGE:
      return { ...state, oldMessages: [...state.oldMessages, action.message] };

    default:
      return state;
  }
}
