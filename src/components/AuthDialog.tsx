import { useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";
import {
  RadioGroup,
  RadioGroupItem,
} from "@/components/ui/radio-group";
import { storeAuth, setFastinoUserId } from "@/lib/auth";
import { registerUser } from "@/lib/fastino";
import { toast } from "sonner";

interface AuthDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

const TONE_OPTIONS = [
  { value: "friendly", label: "Friendly & Encouraging" },
  { value: "professional", label: "Professional & Structured" },
  { value: "casual", label: "Casual & Conversational" },
];

const AuthDialog = ({ open, onOpenChange }: AuthDialogProps) => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [name, setName] = useState("");
  const [age, setAge] = useState("");
  const [tone, setTone] = useState("");
  const [error, setError] = useState("");
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");

    // Basic validation
    if (!email.trim()) {
      setError("Email is required");
      return;
    }

    if (!password.trim()) {
      setError("Password is required");
      return;
    }

    if (!name.trim()) {
      setError("Name is required");
      return;
    }

    if (!age.trim()) {
      setError("Age is required");
      return;
    }

    const ageNum = parseInt(age, 10);
    if (isNaN(ageNum) || ageNum < 1 || ageNum > 150) {
      setError("Please enter a valid age");
      return;
    }

    if (!tone) {
      setError("Please select a tone");
      return;
    }

    // Store auth credentials
    storeAuth(email, password);

    // Register user with Fastino (non-blocking)
    try {
      const user_id = await registerUser(email, name, ageNum, tone);
      if (user_id) {
        setFastinoUserId(user_id);
        console.log("✅ User registered with Fastino:", user_id);
      } else {
        console.warn("⚠️  Fastino registration failed, continuing anyway");
        toast.warning("Fastino registration failed, but you can still use the app");
      }
    } catch (error) {
      console.warn("⚠️  Fastino registration error:", error);
      toast.warning("Fastino registration failed, but you can still use the app");
    }

    // Close dialog
    onOpenChange(false);

    // Navigate to Home
    navigate("/Home");
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle>Sign In to Learn.AI</DialogTitle>
          <DialogDescription>
            Enter your details to start learning.
          </DialogDescription>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="name">Name</Label>
            <Input
              id="name"
              type="text"
              placeholder="Your name"
              value={name}
              onChange={(e) => setName(e.target.value)}
              required
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="email">Email</Label>
            <Input
              id="email"
              type="email"
              placeholder="your@email.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="password">Password</Label>
            <Input
              id="password"
              type="password"
              placeholder="Enter your password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="age">Age</Label>
            <Input
              id="age"
              type="number"
              placeholder="Enter your age"
              value={age}
              onChange={(e) => setAge(e.target.value)}
              min="1"
              max="150"
              required
            />
          </div>
          <div className="space-y-2">
            <Label>Learning Tone</Label>
            <RadioGroup value={tone} onValueChange={setTone}>
              {TONE_OPTIONS.map((option) => (
                <div key={option.value} className="flex items-center space-x-2">
                  <RadioGroupItem value={option.value} id={`tone-${option.value}`} />
                  <Label
                    htmlFor={`tone-${option.value}`}
                    className="text-sm font-normal cursor-pointer"
                  >
                    {option.label}
                  </Label>
                </div>
              ))}
            </RadioGroup>
          </div>
          {error && <p className="text-sm text-red-500">{error}</p>}
          <Button
            type="submit"
            className="w-full"
            style={{
              backgroundColor: "#FE5C02",
              color: "#FFFFFF",
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.backgroundColor = "#e54d00";
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.backgroundColor = "#FE5C02";
            }}
          >
            Sign In
          </Button>
        </form>
      </DialogContent>
    </Dialog>
  );
};

export default AuthDialog;

