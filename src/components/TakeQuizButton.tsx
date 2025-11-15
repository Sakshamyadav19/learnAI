import { Button } from "@/components/ui/button";

interface TakeQuizButtonProps {
  onClick: () => void;
  disabled?: boolean;
}

const TakeQuizButton = ({ onClick, disabled = false }: TakeQuizButtonProps) => {
  return (
    <Button
      onClick={onClick}
      disabled={disabled}
      className="px-8 py-6 text-lg"
      style={{
        backgroundColor: disabled ? "#cccccc" : "#FE5C02",
        color: "#FFFFFF",
        cursor: disabled ? "not-allowed" : "pointer",
      }}
      onMouseEnter={(e) => {
        if (!disabled) {
          e.currentTarget.style.backgroundColor = "#e54d00";
        }
      }}
      onMouseLeave={(e) => {
        if (!disabled) {
          e.currentTarget.style.backgroundColor = "#FE5C02";
        }
      }}
    >
      Take Quiz
    </Button>
  );
};

export default TakeQuizButton;

