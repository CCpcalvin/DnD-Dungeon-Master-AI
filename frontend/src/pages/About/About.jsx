import { useEffect, useState } from "react";

import styles from "./About.module.css";
import TopBar from "../../components/TopBar";
import HomeButton from "../../components/HomeButton";
import LogoutButton from "../../components/LogoutButton";
import LoginRegisterButton from "../../components/LoginRegisterButton";

import Container from "../../components/Container";

import { isAuthenticated } from "../../utils/auth";

function About() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);

  useEffect(() => {
    const checkAuth = async () => {
      setIsLoggedIn(await isAuthenticated());
    };
    checkAuth();

    // Set up a storage event listener to detect token changes in other tabs
    const handleStorageChange = checkAuth;
    window.addEventListener("storage", handleStorageChange);

    return () => {
      window.removeEventListener("storage", handleStorageChange);
    };
  }, []);

  return (
    <div className={styles.container}>
      <TopBar>
        <HomeButton size="sm" />
        {isLoggedIn ? (
          <LogoutButton size="sm" />
        ) : (
          <LoginRegisterButton size="sm" />
        )}
      </TopBar>

      <Container>
        <div className="bg-gray-800 rounded-lg p-6 mt-4">
          <h2 className="text-2xl font-bold text-white mb-6">
            About D&D Dungeon Master AI
          </h2>
          <div className="text-gray-300 space-y-4 leading-relaxed">
            <p className="text-gray-100 font-medium">
              Welcome to a unique Dungeons & Dragons experience where an AI
              serves as your Dungeon Master. In this text-based adventure, you'll
              explore mysterious locations, solve puzzles, and make crucial
              decisions that shape your journey. Your goal is simple: climb the
              tower, collect treasures, and survive the dangers that lurk
              within. But beware—every choice matters, and one wrong move could
              be your last. Ready to test your wits and courage against the
              tower's endless challenges?
            </p>
          </div>
        </div>
      </Container>
    </div>
  );
}

export default About;
