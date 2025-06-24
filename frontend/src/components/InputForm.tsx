import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { SquarePen, Brain, Send, StopCircle, Zap, Cpu, Globe } from "lucide-react"; // Added Globe
import { Textarea } from "@/components/ui/textarea";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

// Model definitions
const googleModels = [
  { value: "gemini-2.5-flash-lite-preview-06-17", label: "2.0 Flash", icon: <Zap className="h-4 w-4 mr-2 text-yellow-400" /> },
  { value: "gemini-2.5-flash", label: "2.5 Flash", icon: <Zap className="h-4 w-4 mr-2 text-orange-400" /> },
  { value: "gemini-2.5-pro", label: "2.5 Pro", icon: <Cpu className="h-4 w-4 mr-2 text-purple-400" /> },
];

const openAIModels = [
  { value: "gpt-4.1", label: "GPT-4.1", icon: <Cpu className="h-4 w-4 mr-2 text-blue-400" /> }, // Assuming gpt-4.1 maps to gpt-4-turbo
  { value: "o4-mini", label: "o4-mini", icon: <Zap className="h-4 w-4 mr-2 text-green-400" /> },   // Assuming o4-mini maps to gpt-4o-mini
  { value: "o3", label: "o3", icon: <Zap className="h-4 w-4 mr-2 text-teal-400" /> },        // Assuming o3 maps to gpt-3.5-turbo
];


// Updated InputFormProps
interface InputFormProps {
  onSubmit: (inputValue: string, effort: string, modelProvider: string, model: string) => void;
  onCancel: () => void;
  isLoading: boolean;
  hasHistory: boolean;
}

export const InputForm: React.FC<InputFormProps> = ({
  onSubmit,
  onCancel,
  isLoading,
  hasHistory,
}) => {
  const [internalInputValue, setInternalInputValue] = useState("");
  const [effort, setEffort] = useState("medium");
  const [modelProvider, setModelProvider] = useState("google"); // Default to Google
  const [model, setModel] = useState(googleModels[1].value); // Default to Gemini 2.5 Flash

  // Update available models when provider changes
  useEffect(() => {
    if (modelProvider === "google") {
      setModel(googleModels[1].value); // Default to Gemini 2.5 Flash
    } else if (modelProvider === "openai") {
      setModel(openAIModels[0].value); // Default to GPT-4.1
    }
  }, [modelProvider]);

  const handleInternalSubmit = (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!internalInputValue.trim()) return;
    onSubmit(internalInputValue, effort, modelProvider, model);
    // setInternalInputValue(""); // Keep input value for now, maybe clear on successful submission
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    // Submit with Ctrl+Enter (Windows/Linux) or Cmd+Enter (Mac)
    if (e.key === "Enter" && (e.ctrlKey || e.metaKey)) {
      e.preventDefault();
      handleInternalSubmit();
    }
  };

  const isSubmitDisabled = !internalInputValue.trim() || isLoading;

  return (
    <form
      onSubmit={handleInternalSubmit}
      className={`flex flex-col gap-2 p-3 pb-4`}
    >
      <div
        className={`flex flex-row items-center justify-between text-white rounded-3xl rounded-bl-sm ${
          hasHistory ? "rounded-br-sm" : ""
        } break-words min-h-7 bg-neutral-700 px-4 pt-3 `}
      >
        <Textarea
          value={internalInputValue}
          onChange={(e) => setInternalInputValue(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Who won the Euro 2024 and scored the most goals?"
          className={`w-full text-neutral-100 placeholder-neutral-500 resize-none border-0 focus:outline-none focus:ring-0 outline-none focus-visible:ring-0 shadow-none
                        md:text-base  min-h-[56px] max-h-[200px]`}
          rows={1}
        />
        <div className="-mt-3">
          {isLoading ? (
            <Button
              type="button"
              variant="ghost"
              size="icon"
              className="text-red-500 hover:text-red-400 hover:bg-red-500/10 p-2 cursor-pointer rounded-full transition-all duration-200"
              onClick={onCancel}
            >
              <StopCircle className="h-5 w-5" />
            </Button>
          ) : (
            <Button
              type="submit"
              variant="ghost"
              className={`${
                isSubmitDisabled
                  ? "text-neutral-500"
                  : "text-blue-500 hover:text-blue-400 hover:bg-blue-500/10"
              } p-2 cursor-pointer rounded-full transition-all duration-200 text-base`}
              disabled={isSubmitDisabled}
            >
              Search
              <Send className="h-5 w-5" />
            </Button>
          )}
        </div>
      </div>
      <div className="flex items-center justify-between">
        <div className="flex flex-row gap-2 flex-wrap"> {/* Added flex-wrap for responsiveness */}
          {/* Effort Selector */}
          <div className="flex flex-row items-center gap-1 bg-neutral-700 border-neutral-600 text-neutral-300 focus:ring-neutral-500 rounded-xl rounded-t-sm pl-2 pr-1">
            <Brain className="h-4 w-4" />
            <span className="text-sm hidden sm:inline">Effort</span> {/* Hide text on small screens */}
            <Select value={effort} onValueChange={setEffort}>
              <SelectTrigger className="w-[90px] sm:w-[100px] bg-transparent border-none cursor-pointer text-sm">
                <SelectValue placeholder="Effort" />
              </SelectTrigger>
              <SelectContent className="bg-neutral-700 border-neutral-600 text-neutral-300 cursor-pointer">
                <SelectItem value="low" className="hover:bg-neutral-600 focus:bg-neutral-600 cursor-pointer text-sm">Low</SelectItem>
                <SelectItem value="medium" className="hover:bg-neutral-600 focus:bg-neutral-600 cursor-pointer text-sm">Medium</SelectItem>
                <SelectItem value="high" className="hover:bg-neutral-600 focus:bg-neutral-600 cursor-pointer text-sm">High</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {/* Model Provider Selector */}
          <div className="flex flex-row items-center gap-1 bg-neutral-700 border-neutral-600 text-neutral-300 focus:ring-neutral-500 rounded-xl rounded-t-sm pl-2 pr-1">
            <Globe className="h-4 w-4" /> {/* Icon for provider */}
            <span className="text-sm hidden sm:inline">Provider</span> {/* Hide text on small screens */}
            <Select value={modelProvider} onValueChange={setModelProvider}>
              <SelectTrigger className="w-[90px] sm:w-[100px] bg-transparent border-none cursor-pointer text-sm">
                <SelectValue placeholder="Provider" />
              </SelectTrigger>
              <SelectContent className="bg-neutral-700 border-neutral-600 text-neutral-300 cursor-pointer">
                <SelectItem value="google" className="hover:bg-neutral-600 focus:bg-neutral-600 cursor-pointer text-sm">Google</SelectItem>
                <SelectItem value="openai" className="hover:bg-neutral-600 focus:bg-neutral-600 cursor-pointer text-sm">OpenAI</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {/* Model Selector */}
          <div className="flex flex-row items-center gap-1 bg-neutral-700 border-neutral-600 text-neutral-300 focus:ring-neutral-500 rounded-xl rounded-t-sm pl-2 pr-1">
            <Cpu className="h-4 w-4" />
            <span className="text-sm hidden sm:inline">Model</span> {/* Hide text on small screens */}
            <Select value={model} onValueChange={setModel}>
              <SelectTrigger className="w-[120px] sm:w-[140px] bg-transparent border-none cursor-pointer text-sm">
                <SelectValue placeholder="Model" />
              </SelectTrigger>
              <SelectContent className="bg-neutral-700 border-neutral-600 text-neutral-300 cursor-pointer">
                {(modelProvider === "google" ? googleModels : openAIModels).map((m) => (
                  <SelectItem key={m.value} value={m.value} className="hover:bg-neutral-600 focus:bg-neutral-600 cursor-pointer text-sm">
                    <div className="flex items-center">
                      {m.icon} {m.label}
                    </div>
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </div>
        {hasHistory && (
          <Button
            className="bg-neutral-700 border-neutral-600 text-neutral-300 cursor-pointer rounded-xl rounded-t-sm pl-2 "
            variant="default"
            onClick={() => window.location.reload()}
          >
            <SquarePen size={16} />
            New Search
          </Button>
        )}
      </div>
    </form>
  );
};
