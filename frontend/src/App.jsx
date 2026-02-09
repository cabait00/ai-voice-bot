import { useState, useEffect, useRef } from "react";
import "./App.css";
import VoiceButton from "./components/VoiceButton";
import ChatMessage from "./components/ChatMessage";
import axios from "axios";
import schunkLogo from "./assets/schunk-logo.png";

const API_BASE_URL = "http://localhost:8000";

function App() {
  const [messages, setMessages] = useState([]);
  const [isListening, setIsListening] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [transcript, setTranscript] = useState("");
  const [isProcessing, setIsProcessing] = useState(false);
  const [apiStatus, setApiStatus] = useState("checking");

  const recognitionRef = useRef(null);
  const synthRef = useRef(window.speechSynthesis);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    checkBackendHealth();
  }, []);

  const checkBackendHealth = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/health`);
      if (response.data.status === "healthy") {
        setApiStatus("connected");
      } else {
        setApiStatus("error");
        addSystemMessage("Backend nicht erreichbar. Bitte Backend starten.");
      }
    } catch (error) {
      setApiStatus("error");
      addSystemMessage("Backend nicht erreichbar. Bitte Backend starten.");
    }
  };

  const initializeSpeechRecognition = () => {
    const SpeechRecognition =
      window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
      addSystemMessage(
        "Sprachfunktion wird von diesem Browser nicht unterstützt. Bitte nutzen Sie Chrome oder Edge.",
      );
      return null;
    }

    const recognition = new SpeechRecognition();
    recognition.lang = "de-DE";
    recognition.continuous = false;
    recognition.interimResults = true;

    recognition.onstart = () => {
      setIsListening(true);
      setTranscript("");
    };

    recognition.onresult = (event) => {
      let interimTranscript = "";
      let finalTranscript = "";

      for (let i = event.resultIndex; i < event.results.length; i++) {
        const result = event.results[i];
        if (result.isFinal) {
          finalTranscript += result[0].transcript;
        } else {
          interimTranscript += result[0].transcript;
        }
      }

      setTranscript(interimTranscript || finalTranscript);

      if (finalTranscript.trim()) {
        handleQuestion(finalTranscript.trim());
      }
    };

    recognition.onerror = (event) => {
      setIsListening(false);
      if (event.error === "not-allowed") {
        addSystemMessage(
          "Mikrofon-Zugriff wurde verweigert. Bitte erlauben Sie den Zugriff in den Browser-Einstellungen.",
        );
      } else {
        addSystemMessage(
          "Fehler bei der Spracherkennung. Bitte erneut versuchen.",
        );
      }
    };

    recognition.onend = () => {
      setIsListening(false);
      setTranscript("");
    };

    return recognition;
  };

  const startListening = () => {
    if (!recognitionRef.current) {
      recognitionRef.current = initializeSpeechRecognition();
    }

    if (recognitionRef.current && !isProcessing) {
      recognitionRef.current.start();
    }
  };

  const stopListening = () => {
    if (recognitionRef.current) {
      recognitionRef.current.stop();
    }
  };

  const speakText = (text) => {
    if (!window.speechSynthesis) {
      return;
    }

    window.speechSynthesis.cancel();

    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = "de-DE";
    utterance.rate = 1;
    utterance.pitch = 1;

    utterance.onstart = () => setIsSpeaking(true);
    utterance.onend = () => setIsSpeaking(false);
    utterance.onerror = () => setIsSpeaking(false);

    synthRef.current.speak(utterance);
  };

  const stopSpeaking = () => {
    if (window.speechSynthesis) {
      window.speechSynthesis.cancel();
      setIsSpeaking(false);
    }
  };

  const addMessage = (type, text) => {
    setMessages((prev) => [...prev, { type, text, timestamp: new Date() }]);
  };

  const addUserMessage = (text) => addMessage("user", text);
  const addBotMessage = (text) => addMessage("bot", text);
  const addSystemMessage = (text) => addMessage("system", text);

  const handleQuestion = async (question) => {
    if (!question.trim() || isProcessing) return;

    addUserMessage(question);
    setIsProcessing(true);

    try {
      const response = await axios.post(`${API_BASE_URL}/api/ask`, {
        question: question,
      });

      const answer = response.data.answer;
      addBotMessage(answer);
      speakText(answer);
    } catch (error) {
      addSystemMessage(
        "Fehler beim Abrufen der Antwort. Bitte prüfen Sie die Backend-Verbindung.",
      );
    } finally {
      setIsProcessing(false);
    }
  };

  const handleTextSubmit = (e) => {
    e.preventDefault();
    const input = e.target.elements.question;
    if (input.value.trim()) {
      handleQuestion(input.value);
      input.value = "";
    }
  };

  const renderStatusText = () => {
    if (apiStatus === "connected") return "Online";
    if (apiStatus === "checking") return "Pruefe Verbindung";
    return "Offline";
  };

  return (
    <div className="app">
      <header className="schunk-header">
        <div className="schunk-topbar">
          <div className="schunk-topbar-inner">
            <div className="schunk-brand">
              <img className="schunk-logo" src={schunkLogo} alt="SCHUNK" />
              <div className="schunk-claim">Hand in hand for tomorrow</div>
            </div>

            <div className={`schunk-status ${apiStatus}`}>
              {renderStatusText()}
            </div>
          </div>
        </div>

        <div className="schunk-subbar">
          <div className="schunk-subbar-inner">
            <div className="schunk-subbar-title">Voice Agent</div>
          </div>
        </div>

        <div className="schunk-hero">
          <div className="schunk-hero-inner">
            <h1 className="hero-title">PGN-plus-P Voice Agent</h1>
            <p className="hero-subtitle">
              Ihr intelligenter Produktberater für den Universalgreifer
            </p>
          </div>
        </div>
      </header>

      <main className="app-main">
        <div className="chat-shell">
          <div className="chat-header-row">
            <div className="chat-header-title">Chat</div>
          </div>

          <div className="chat-messages">
            {messages.map((message, index) => (
              <ChatMessage key={index} message={message} />
            ))}
            {transcript && (
              <div className="transcript-preview">
                <div className="transcript-label">Erkannt:</div>
                <div className="transcript-text">{transcript}</div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          <div className="chat-input-area">
            <form className="text-input-form" onSubmit={handleTextSubmit}>
              <input
                type="text"
                name="question"
                placeholder="Frage zum PGN-plus-P..."
                disabled={isProcessing || apiStatus !== "connected"}
              />
              <button
                type="submit"
                disabled={isProcessing || apiStatus !== "connected"}
              >
                Senden
              </button>
            </form>

            <div className="voice-area">
              <VoiceButton
                isListening={isListening}
                isSpeaking={isSpeaking}
                onStart={startListening}
                onStop={stopListening}
                onStopSpeaking={stopSpeaking}
                disabled={isProcessing || apiStatus !== "connected"}
              />
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}

export default App;
