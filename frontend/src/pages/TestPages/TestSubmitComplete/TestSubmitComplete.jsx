import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";

import Session from "../../Session/Session";
import { GameState } from "../../Session/sessionMachine";
import { NetworkDelay, PageNotFoundError } from "../utils";

// Create a mock API client
const createMockApi = (sessionId) => {
  return {
    // Mock for getting session events with simulated network delay
    get: async (url) => {
      if (url === `/session/${sessionId}/get-events`) {
        await NetworkDelay();

        return {
          data: {
            events: [
              {
                role: "Narrator",
                content:
                  "The ancient Spire of Eternity looms over the forsaken village, its black stone walls shrouded in an aura of malevolent energy. Shadows writhe across the tower's crumbling facade like living darkness, as if the very fabric of reality has been twisted within its depths. You are a scholar of the obscure and forgotten arts, driven by a morbid fascination with the forbidden knowledge that whispers through the Spire. Your own family was destroyed in the village's great tragedy, for which you have sworn to exact revenge on those responsible. With every failed expedition to the Spire, the nightmares grow more vivid and the silence of your late mother's cryptic journals has grown deafeningly loud: she had discovered a way into the heart of Eternity, but it cost her everything. You have come to claim what she found, to unravel the dark threads that bound your family's fate to the tower's cursed power.",
              },
              {
                role: "Narrator",
                content:
                  "Dust-coated tapestries adorn crumbling stone walls, as faint echoes whisper secrets in this forgotten keep. A fragment of parchment catches your eye, bearing a cryptic message scrawled in haste: 'Where shadows dance, the truth awaits...'",
                suggested_actions: [
                  "Investigate the tapestries for hidden symbols or patterns",
                  "Examine the floor for any inconsistencies in the stone",
                ],
              },
            ],
            state: GameState.IN_PROGRESS,
          },
          status: 200,
        };
      }

      return PageNotFoundError();
    },

    // Mock for creating a new floor with simulated network delay
    post: async (url) => {
      await NetworkDelay();

      if (url === `/session/${sessionId}/player-input`) {
        return {
          data: {
            state: GameState.COMPLETED,
            events: [
              {
                role: "Player",
                content: "Long long long long long text by player.",
              },
              {
                role: "System",
                content: "Long long long long long text by system.",
              },
              {
                role: "Narrator",
                content: "Long long long long long text by narrator.",
              },
            ],
          },
          status: 200,
        };
      }

      return PageNotFoundError();
    },
  };
};

export default function TestSubmitComplete() {
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
