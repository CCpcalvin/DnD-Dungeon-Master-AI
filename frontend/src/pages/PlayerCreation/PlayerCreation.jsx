import { useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../../utils/api";

import TopBar from "../../components/TopBar";
import HomeButton from "../../components/HomeButton";
import LogoutButton from "../../components/LogoutButton";
import Container from "../../components/Container";

import styles from "./PlayerCreation.module.css";

function PlayerCreation() {
  const MIN_ATTRIBUTE = 1;
  const MAX_ATTRIBUTE = 9;
  const BASE_ATTRIBUTES = 3; // 6 attributes * min value
  const TOTAL_POINTS = 30; // Points to distribute

  const [playerName, setPlayerName] = useState("");
  const [attributes, setAttributes] = useState({
    strength: BASE_ATTRIBUTES,
    dexterity: BASE_ATTRIBUTES,
    constitution: BASE_ATTRIBUTES,
    intelligence: BASE_ATTRIBUTES,
    wisdom: BASE_ATTRIBUTES,
    charisma: BASE_ATTRIBUTES,
  });
  const [messages, setMessages] = useState([
    {
      role: "Narrator",
      text: "Welcome, adventurer! Before we begin, tell me about yourself...",
    },
  ]);

  const totalPoints = Object.values(attributes).reduce((a, b) => a + b, 0);
  const pointsRemaining = TOTAL_POINTS - totalPoints;

  const handleAttributeChange = (attr, value) => {
    const newValue = Math.max(MIN_ATTRIBUTE, Math.min(MAX_ATTRIBUTE, value));
    setAttributes((prev) => ({ ...prev, [attr]: newValue }));
  };

  const navigate = useNavigate();
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (pointsRemaining !== 0 || !playerName.trim()) return;

    setIsSubmitting(true);
    try {
      const response = await api.post("/session/create-game", {
        player_name: playerName,
        strength: attributes.strength,
        dexterity: attributes.dexterity,
        constitution: attributes.constitution,
        intelligence: attributes.intelligence,
        wisdom: attributes.wisdom,
        charisma: attributes.charisma,
      });

      const { session_id, narrative } = response.data;
      navigate(`/session/${session_id}`, {
        state: { initialNarrative: narrative },
      });
    } catch (error) {
      console.error("Error creating game:", error);
      // Handle error (e.g., show error message to user)
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-900">
      <TopBar>
        <HomeButton />
        <LogoutButton />
      </TopBar>

      <Container>
        {/* Chat Region */}
        <div className="bg-gray-800 rounded-lg p-6 mb-6 max-h-64 overflow-y-auto">
          {messages.map((msg, index) => (
            <div key={index} className="text-white mb-2">
              <span className="font-bold text-green-400">{msg.role}: </span>
              <span>{msg.text}</span>
            </div>
          ))}
        </div>

        {/* Player Creation Card */}
        <div className="bg-gray-800 rounded-lg p-6">
          <h2 className="text-xl font-bold text-white mb-4">
            Create Your Character
          </h2>

          <form onSubmit={handleSubmit}>
            {/* Player Name */}
            <div className="mb-6">
              <label className="block text-white mb-2" htmlFor="playerName">
                Character Name
              </label>
              <input
                type="text"
                id="playerName"
                value={playerName}
                onChange={(e) => setPlayerName(e.target.value)}
                className="w-full p-2 rounded bg-gray-700 text-white"
                required
              />
            </div>

            {/* Attribute Allocation */}
            <div className="mb-6">
              <div className="flex justify-between items-center mb-2">
                <h3 className="text-white">
                  Distribute your points (30 total)
                </h3>
                <span
                  className={`font-bold ${
                    pointsRemaining === 0
                      ? "text-green-400"
                      : pointsRemaining > 0
                      ? "text-yellow-400"
                      : "text-red-500"
                  }`}>
                  Points remaining: {pointsRemaining}
                </span>
              </div>

              {Object.entries(attributes).map(([attr, value]) => (
                <div key={attr} className="flex items-center mb-4">
                  <label className="w-32 text-white capitalize">{attr}:</label>
                  <div className="w-12 text-white text-center mr-2">
                    {value}
                  </div>
                  <input
                    type="range"
                    min={MIN_ATTRIBUTE}
                    max={MAX_ATTRIBUTE}
                    value={value}
                    onChange={(e) =>
                      handleAttributeChange(attr, parseInt(e.target.value))
                    }
                    className="flex-1 h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer"
                    style={{
                      background: `linear-gradient(to right, #10B981 0%, #10B981 ${
                        ((value - MIN_ATTRIBUTE) /
                          (MAX_ATTRIBUTE - MIN_ATTRIBUTE)) *
                        100
                      }%, #374151 ${
                        ((value - MIN_ATTRIBUTE) /
                          (MAX_ATTRIBUTE - MIN_ATTRIBUTE)) *
                        100
                      }%, #374151 100%)`,
                    }}
                  />
                </div>
              ))}
            </div>

            <button
              type="submit"
              disabled={
                pointsRemaining !== 0 || !playerName.trim() || isSubmitting
              }
              className={`w-full py-2 px-4 rounded font-bold ${
                pointsRemaining === 0 && playerName.trim() && !isSubmitting
                  ? "bg-green-600 hover:bg-green-700 text-white"
                  : "bg-gray-600 text-gray-400 cursor-not-allowed"
              }`}>
              {isSubmitting ? "Creating Game..." : "Begin Your Adventure"}
            </button>
          </form>
        </div>
      </Container>
    </div>
  );
}

export default PlayerCreation;
