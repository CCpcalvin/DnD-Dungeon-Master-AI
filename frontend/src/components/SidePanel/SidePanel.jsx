import React, { useEffect, useRef, useState } from "react";
import { FaChevronRight, FaTimes } from "react-icons/fa";
import styles from "./SidePanel.module.css";

const SidePanel = ({ isOpen, onToggle, sessionId, api, children }) => {
  const [sessionInfo, setSessionInfo] = useState(null);
  const [playerInfo, setPlayerInfo] = useState(null);

  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const sidebarRef = useRef(null);

  // Fetch session info when panel is opened
  useEffect(() => {
    const fetchSessionInfo = async () => {
      if (!isOpen || !sessionId || !api) return;
      
      setIsLoading(true);
      setError(null);
      
      try {
        const response = await api.get(`/session/${sessionId}/get-session-info`);
        const { player_info, session_info } = response.data;
        setPlayerInfo(player_info);
        setSessionInfo(session_info);
      } catch (err) {
        console.error('Failed to fetch session info:', err);
        setError('Failed to load session information');
      } finally {
        setIsLoading(false);
      }
    };
    
    fetchSessionInfo();
  }, [isOpen, sessionId, api]);

  // Close sidebar when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (isOpen && sidebarRef.current && !sidebarRef.current.contains(event.target)) {
        // Check if the click is on the toggle button
        const toggleButton = document.querySelector(`.${styles.toggleButton}`);
        if (!toggleButton || !toggleButton.contains(event.target)) {
          onToggle(false);
        }
      }
    };

    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside);
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [isOpen, onToggle]);

  const renderContent = () => {
    if (children) return children;
    
    if (isLoading) {
      return (
        <div className="h-full flex items-center justify-center">
          <div className="animate-pulse text-gray-400 text-xl">Loading...</div>
        </div>
      );
    }
    
    if (error) {
      return <div className="text-red-400 p-4">{error}</div>;
    }
    
    if (sessionInfo) {
      return (
        <div className="space-y-4 p-4">
          <h2 className="text-xl font-semibold mb-4 text-white">Session Information</h2>
          
          <div>
            <h3 className="font-semibold text-gray-300">Theme</h3>
            <p className="text-gray-400">{sessionInfo.theme || 'Not specified'}</p>
          </div>
          
          <div>
            <h3 className="font-semibold text-gray-300">Current Floor</h3>
            <p className="text-gray-400">{sessionInfo.current_floor || 'Not specified'}</p>
          </div>
          
          {playerInfo && (
            <div className="space-y-6">
              <h3 className="text-lg font-semibold text-white border-b border-gray-700 pb-2">Player</h3>
              <div className="bg-gray-800 rounded-lg p-4">
                {/* Player Header */}
                <div className="flex justify-between items-center mb-3">
                  <h4 className="font-medium text-gray-200">
                    {playerInfo.player_name || 'Unnamed Player'}
                    {playerInfo.is_ready && (
                      <span className="ml-2 text-xs bg-green-600 text-white px-2 py-0.5 rounded">
                        Ready
                      </span>
                    )}
                  </h4>
                  <div className="text-sm text-gray-400">
                    HP: <span className="text-red-400">{playerInfo.current_health || 0}</span> / {playerInfo.max_health || 0}
                  </div>
                </div>

                {/* Player Description */}
                {playerInfo.description && (
                  <p className="text-sm text-gray-400 mb-3">
                    {playerInfo.description}
                  </p>
                )}

                {/* Player Attributes */}
                <div className="mt-3 pt-3 border-t border-gray-700">
                  <h5 className="text-sm font-medium text-gray-300 mb-2">Attributes</h5>
                  <div className="grid grid-cols-3 gap-2 text-sm">
                    {playerInfo.strength !== undefined && (
                      <div className="text-gray-400">
                        <span className="text-gray-300">STR</span> {playerInfo.strength}
                      </div>
                    )}
                    {playerInfo.dexterity !== undefined && (
                      <div className="text-gray-400">
                        <span className="text-gray-300">DEX</span> {playerInfo.dexterity}
                      </div>
                    )}
                    {playerInfo.constitution !== undefined && (
                      <div className="text-gray-400">
                        <span className="text-gray-300">CON</span> {playerInfo.constitution}
                      </div>
                    )}
                    {playerInfo.intelligence !== undefined && (
                      <div className="text-gray-400">
                        <span className="text-gray-300">INT</span> {playerInfo.intelligence}
                      </div>
                    )}
                    {playerInfo.wisdom !== undefined && (
                      <div className="text-gray-400">
                        <span className="text-gray-300">WIS</span> {playerInfo.wisdom}
                      </div>
                    )}
                    {playerInfo.charisma !== undefined && (
                      <div className="text-gray-400">
                        <span className="text-gray-300">CHA</span> {playerInfo.charisma}
                      </div>
                    )}
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      );
    }
    
    return <div className="text-gray-400 p-4">No session information available</div>;
  };

  return (
    <>
      <div className={`${styles.sidebarOverlay} ${isOpen ? styles.open : ""}`} />
      <div
        className={`${styles.sidebarContainer} ${isOpen ? styles.open : ""}`}
        ref={sidebarRef}
      >
        <div className={styles.sidebar}>
          <div className={styles.content}>
            {renderContent()}
          </div>
        </div>
        <button
          className={styles.toggleButton}
          onClick={() => onToggle(!isOpen)}
          aria-label={isOpen ? "Close panel" : "Open panel"}
        >
          {isOpen ? <FaTimes /> : <FaChevronRight />}
        </button>
      </div>
    </>
  );
};

export default SidePanel;
