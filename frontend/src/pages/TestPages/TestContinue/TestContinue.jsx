import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";

import Session from "../../Session/Session";
import { GameState } from "../../Session/sessionMachine";

// Simulate network delay between 300-800ms
async function NetworkDelay() {
  const delay = 300 + Math.random() * 500;
  return new Promise((resolve) => setTimeout(resolve, delay));
}

// Generate a 404 error response
function PageNotFoundError(message = "Page not found") {
  return {
    response: {
      status: 404,
      data: {
        status: "error",
        message: message,
        code: 404,
        timestamp: new Date().toISOString(),
      },
    },
    isAxiosError: true,
  };
}

// Create a mock API client
const createMockApi = (sessionId) => {
  return {
    // Mock for getting session events with simulated network delay
    get: async (url) => {
      if (url === `/session/${sessionId}/get-events`) {
        await NetworkDelay();

        const initialMessage = {
          role: "Narrator",
          content:
            "The ancient Spire of Eternity looms over the forsaken village, its black stone walls shrouded in an aura of malevolent energy. Shadows writhe across the tower's crumbling facade like living darkness, as if the very fabric of reality has been twisted within its depths. You are a scholar of the obscure and forgotten arts, driven by a morbid fascination with the forbidden knowledge that whispers through the Spire. Your own family was destroyed in the village's great tragedy, for which you have sworn to exact revenge on those responsible. With every failed expedition to the Spire, the nightmares grow more vivid and the silence of your late mother's cryptic journals has grown deafeningly loud: she had discovered a way into the heart of Eternity, but it cost her everything. You have come to claim what she found, to unravel the dark threads that bound your family's fate to the tower's cursed power.",
        };

        return {
          data: {
            events: [initialMessage],
            state: GameState.WAITING_FOR_NEXT_FLOOR,
          },
        };
      }

      return PageNotFoundError();
    },

    // Mock for creating a new floor with simulated network delay
    post: async (url) => {
      await NetworkDelay();

      if (url === `/session/${sessionId}/new-floor`) {
        const newMessage = {
          role: "Narrator",
          content:
            "Dust-coated tapestries adorn crumbling stone walls, as faint echoes whisper secrets in this forgotten keep. A fragment of parchment catches your eye, bearing a cryptic message scrawled in haste: 'Where shadows dance, the truth awaits...'",
        };

        return {
          data: {
            narrative: newMessage.content,
            suggested_actions: [
              "Investigate the tapestries for hidden symbols or patterns",
              "Examine the floor for any inconsistencies in the stone",
            ],
            state: GameState.IN_PROGRESS,
          },
        };
      }

      return PageNotFoundError();
    },
  };
};

export default function TestContinue() {
  const { sessionId = "test-session" } = useParams();
  const [mockApi, setMockApi] = useState(null);

  useEffect(() => {
    // Create a new mock API instance when the component mounts or sessionId changes
    setMockApi(createMockApi(sessionId));
  }, [sessionId]);

  if (!mockApi) {
    return <div>Initializing test environment...</div>;
  }

  return <Session api={mockApi} params={{ sessionId }} />;
}
