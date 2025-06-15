import Session from "../../Session/Session";
import { NetworkDelay, PageNotFoundError } from "../utils";

// Create a mock API client
const createMockApi = () => {
  return {
    // Mock for getting session events with simulated network delay
    get: async (url) => {
      await NetworkDelay();
      return PageNotFoundError();
    },

    // Mock for creating a new floor with simulated network delay
    post: async (url) => {
      await NetworkDelay();
      return PageNotFoundError();
    },
  };
};

export default function TestCreateNewSession() {

  const initialNarrative = "Short narrative."

  return <Session initialNarrative={initialNarrative} api={createMockApi()} />;
}
