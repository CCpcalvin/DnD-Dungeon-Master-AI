import { useNavigate } from "react-router-dom";
import BaseButton from "./ui/BaseButton";

function NewAdventureButton({
  className = "",
  size = "md",
  collapsible = true,
}) {
  const navigate = useNavigate();

  const handleClick = () => {
    navigate("/player-creation");
  };

  return (
    <BaseButton
      onClick={handleClick}
      variant="primary"
      size={size}
      className={className}>
      {collapsible ? (
        <>
          <span className="hidden sm:inline">+ New Adventure</span>
          <span className="sm:hidden">+ New</span>
        </>
      ) : (
        <span>+ New Adventure</span>
      )}
    </BaseButton>
  );
}

export default NewAdventureButton;
