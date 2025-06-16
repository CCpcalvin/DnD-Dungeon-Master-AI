import { useNavigate } from "react-router-dom";
import styles from "./About.module.css";
import TopBar from "../../components/TopBar";
import HomeButton from "../../components/HomeButton";
import LogoutButton from "../../components/LogoutButton";
import Container from "../../components/Container";

function About() {
  const navigate = useNavigate();

  const handleBack = () => {
    navigate(-1); // Go back to previous page
  };

  return (
    <div className={styles.container}>
      <TopBar>
        <HomeButton onClick={handleBack} />
        <LogoutButton />
      </TopBar>

      <Container>
        <div className="bg-gray-800 rounded-lg p-6 mt-4">
          <h2 className="text-2xl font-bold text-white mb-6">About D&D Dungeon Master AI</h2>
          <div className="text-gray-300 space-y-4 leading-relaxed">
            <p className="text-gray-100 font-medium">
              Welcome to a unique Dungeons & Dragons experience where an AI serves as your Game Master. In this text-based adventure, you'll explore mysterious locations, solve puzzles, and make crucial decisions that shape your journey. Your goal is simple: climb the tower, collect treasures, and survive the dangers that lurk within. But beware—every choice matters, and one wrong move could be your last. Ready to test your wits and courage against the tower's endless challenges?
            </p>
          </div>
        </div>
      </Container>
    </div>
  );
}

export default About;
