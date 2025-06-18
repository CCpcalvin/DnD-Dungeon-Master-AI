import { useState, useEffect } from "react";

import { isAuthenticated } from "../../utils/auth";

import "../../App.css";
import styles from "./Home.module.css";

import TopBar from "../../components/TopBar";
import LogoutButton from "../../components/LogoutButton";
import AboutButton from "../../components/AboutButton";
import Container from "../../components/Container";
import NewAdventureButton from "../../components/NewAdventureButton";
import ContinueButton from "../../components/ContinueButton";
import LoginRegisterButton from "../../components/LoginRegisterButton";

import Footer from "../../components/Footer";

function Home() {
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
    <div className="flex flex-col min-h-screen bg-gray-900 w-full">
      <div className="flex-shrink-0">
        <TopBar>
          {isLoggedIn ? (
            <>
              <ContinueButton size="sm" />

              <div className="flex items-center gap-2">
                <AboutButton size="sm" />
                <LogoutButton size="sm" />
              </div>
            </>
          ) : (
            <div className="flex-1 flex justify-between">
              <AboutButton size="sm" />
            </div>
          )}
        </TopBar>
      </div>

      <div className="flex-grow flex items-center">
        <Container>
          <div className="w-full flex items-center justify-center flex-col py-8">
            <h1
              className={`text-2xl text-red-400 mb-4 text-center tracking-widest drop-shadow-lg font-UnifrakturCook ${styles.h1}`}>
              How high can you climb?
            </h1>
            <div className="flex flex-col items-center w-full max-w-md mt-4 gap-2">
              <h2 className="text-white text-xl font-bold">
                {isLoggedIn
                  ? "Welcome Back, Adventurer!"
                  : "Begin Your Adventure"}
              </h2>
              <div className="flex justify-center w-full">
                {isLoggedIn ? (
                  <>
                    <NewAdventureButton collapsible={false} />
                  </>
                ) : (
                  <div className="flex flex-col items-center gap-2">
                    <LoginRegisterButton />
                    <p className="text-gray-400 text-sm text-center">
                      Create an account to save your progress
                    </p>
                  </div>
                )}
              </div>
            </div>
          </div>
        </Container>
      </div>
      <Footer />
    </div>
  );
}

export default Home;
