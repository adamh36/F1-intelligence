import { useState, useRef, useEffect } from "react";
import f1Logo from "./assets/f1-logo.png";
import "./App.css";

const TEAMS = [
  { name: "Red Bull Racing", color: "#3671C6" },
  { name: "Ferrari", color: "#E8002D" },
  { name: "Mercedes", color: "#27F4D2" },
  { name: "McLaren", color: "#FF8000" },
  { name: "Aston Martin", color: "#229971" },
  { name: "Alpine", color: "#FF87BC" },
  { name: "Williams", color: "#64C4FF" },
  { name: "Racing Bulls", color: "#6692FF" },
  { name: "Haas", color: "#B6BABD" },
  { name: "Kick Sauber", color: "#52E252" },
];

export default function App() {
  const [messages, setMessages] = useState([
    {
      role: "assistant",
      content:
        "Welcome to F1 Intelligence. Ask me anything — race results, driver comparisons, tire strategy, or weather at any circuit.",
    },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef(null);
  const canvasRef = useRef(null);
  const videoRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  useEffect(() => {
    const sendPlay = () => {
      videoRef.current?.contentWindow?.postMessage(
        '{"event":"command","func":"playVideo","args":""}',
        "*"
      );
    };
    // Wait for iframe to load, then trigger play to dismiss the overlay
    const timer = setTimeout(sendPlay, 2000);
    return () => clearTimeout(timer);
  }, []);

  useEffect(() => {
    const canvas = canvasRef.current;
    const ctx = canvas.getContext("2d");
    let animId;

    const resize = () => {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
    };
    resize();
    window.addEventListener("resize", resize);

    const lines = Array.from({ length: 40 }, () => ({
      x: Math.random() * window.innerWidth,
      y: Math.random() * window.innerHeight,
      length: Math.random() * 200 + 60,
      speed: Math.random() * 10 + 4,
      opacity: Math.random() * 0.25 + 0.05,
    }));

    const draw = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      lines.forEach((l) => {
        const grad = ctx.createLinearGradient(l.x, l.y, l.x + l.length, l.y);
        grad.addColorStop(0, `rgba(225, 6, 0, 0)`);
        grad.addColorStop(1, `rgba(225, 6, 0, ${l.opacity})`);
        ctx.beginPath();
        ctx.moveTo(l.x, l.y);
        ctx.lineTo(l.x + l.length, l.y);
        ctx.strokeStyle = grad;
        ctx.lineWidth = 1.5;
        ctx.stroke();
        l.x += l.speed;
        if (l.x > canvas.width + l.length) {
          l.x = -l.length;
          l.y = Math.random() * canvas.height;
          l.speed = Math.random() * 10 + 4;
        }
      });
      animId = requestAnimationFrame(draw);
    };
    draw();

    return () => {
      cancelAnimationFrame(animId);
      window.removeEventListener("resize", resize);
    };
  }, []);

  async function sendMessage(e) {
    e.preventDefault();
    if (!input.trim() || loading) return;

    const userMessage = input.trim();
    setInput("");
    setMessages((prev) => [...prev, { role: "user", content: userMessage }]);
    setLoading(true);

    try {
      // slice(1) skips the hardcoded welcome message — it's UI only, not from Claude
      const history = messages.slice(1).concat({ role: "user", content: userMessage });
      const res = await fetch("http://localhost:8000/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ messages: history }),
      });
      const data = await res.json();
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: data.response },
      ]);
    } catch {
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: "Connection error. Make sure the backend is running.",
        },
      ]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="app">
      {/* Video background */}
      <div className="video-container">
        <iframe
          ref={videoRef}
          className="video-bg"
          src="https://www.youtube.com/embed/mdnF9R-Bzpg?autoplay=1&mute=1&loop=1&playlist=mdnF9R-Bzpg&controls=0&showinfo=0&rel=0&iv_load_policy=3&modestbranding=1&start=6&enablejsapi=1"
          frameBorder="0"
          allow="autoplay; encrypted-media"
        />
        <div className="video-overlay" />
      </div>

      {/* Speed line animation on top of video */}
      <canvas ref={canvasRef} className="bg-canvas" />

      {/* Header */}
      <div className="header">
        <div className="header-top">
          <div className="logo-block">
            <img src={f1Logo} alt="F1" className="f1-logo" />
            <div className="header-text">
              <span className="header-title">Intelligence</span>
              <span className="header-sub">
                Powered by Claude · FastF1 · Real-time data
              </span>
            </div>
          </div>
          <div className="header-meta">
            <span className="creator">Built by Adam Hammoud</span>
            <span className="disclaimer">
              Not affiliated with Formula 1® or FOM
            </span>
          </div>
        </div>

        {/* Team badges */}
        <div className="teams-bar">
          {TEAMS.map((t) => (
            <span
              key={t.name}
              className="team-badge"
              style={{ borderColor: t.color, color: t.color }}
            >
              {t.name}
            </span>
          ))}
        </div>
      </div>

      {/* Chat */}
      <div className="chat-window">
        {messages.map((m, i) => (
          <div key={i} className={`message ${m.role}`}>
            <div className="bubble">{m.content}</div>
          </div>
        ))}
        {loading && (
          <div className="message assistant">
            <div className="bubble loading">
              <span />
              <span />
              <span />
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      {/* Input */}
      <form className="input-bar" onSubmit={sendMessage}>
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask about any race, driver, or circuit..."
          disabled={loading}
          autoFocus
        />
        <button type="submit" disabled={loading || !input.trim()}>
          Send
        </button>
      </form>
    </div>
  );
}
