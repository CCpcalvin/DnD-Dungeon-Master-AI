import { useState, useEffect } from "react";
import { useNavigate, Link } from "react-router-dom";
import api from "../../api";

import TopBar from "../../components/TopBar";
import HomeButton from "../../components/HomeButton";
import LogoutButton from "../../components/LogoutButton";
import Container from "../../components/Container";

import styles from "./MySessions.module.css";

function MySessions() {
  const [sessions, setSessions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchSessions = async () => {
      try {
        const response = await api.get("get-sessions");
        setSessions(response.data.sessions);
      } catch (err) {
        setError("Failed to load sessions");
        console.error("Error fetching sessions:", err);
      } finally {
        setLoading(false);
      }
    };

    fetchSessions();
  }, []);

  if (loading) {
    return <div>Loading sessions...</div>;
  }

  if (error) {
    return <div className="text-red-500 text-center mt-4">{error}</div>;
  }

  return (
    <div className="min-h-screen bg-gray-900">
      <TopBar>
        <div className="flex justify-between items-center w-full">
          <HomeButton />
          <LogoutButton />
        </div>
      </TopBar>

      <Container>
        <div className="bg-gray-800 rounded-lg p-6">
          <h1 className="text-2xl font-bold text-white mb-6">My Sessions</h1>

          {sessions.length > 0 ? (
            <div className={styles.sessionsGrid}>
              {sessions.map((session) => (
                <button
                  key={session.id}
                  onClick={() => navigate(`/session/${session.id}`)}
                  className={styles.sessionButton}>
                  <div className="text-left w-full">
                    <p>
                      <span className="font-semibold">Theme:</span>{" "}
                      {session.theme}
                    </p>
                    <p>
                      <span className="font-semibold">Player Name:</span>{" "}
                      {session.player_name}
                    </p>
                    <p>
                      <span className="font-semibold">Current Floor:</span>{" "}
                      {session.current_floor}
                    </p>
                    <p>
                      <span className="font-semibold">Game State:</span>{" "}
                      {session.game_state}
                    </p>
                  </div>
                </button>
              ))}
            </div>
          ) : (
            <p className="text-white ">
              No sessions found.{" "}
              <Link
                to="/player-creation"
                className="text-blue-400 hover:underline">
                Create a new session
              </Link>{" "}
              to get started!
            </p>
          )}
        </div>
      </Container>
    </div>
  );
}

export default MySessions;
