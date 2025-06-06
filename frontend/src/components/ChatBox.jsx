import { useState } from 'react'


function ChatBox() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");

  const handleSend = () => {
    if (input.trim() === "") return;
    setMessages([...messages, { sender: "user", text: input }]);
    setInput("");
    // Example bot response
    setTimeout(() => {
      setMessages((msgs) => [
        ...msgs,
        { sender: "bot", text: "The shadows whisper back..." },
      ]);
    }, 600);
  };

  const handleInputKeyDown = (e) => {
    if (e.key === "Enter") handleSend();
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-black to-gray-800 flex flex-col items-center justify-center font-mono">
      <div className="w-full max-w-md bg-gray-900 bg-opacity-90 rounded-xl shadow-2xl border border-gray-800 p-6">
        <h1 className="text-2xl font-bold text-purple-400 mb-4 text-center tracking-widest drop-shadow-lg">
          Whispering Shadows
        </h1>
        <div className="h-72 overflow-y-auto mb-4 flex flex-col gap-2 scrollbar-thin scrollbar-thumb-gray-700 scrollbar-track-gray-900">
          {messages.map((msg, idx) => (
            <div
              key={idx}
              className={`flex ${
                msg.sender === "user" ? "justify-end" : "justify-start"
              }`}>
              <span
                className={`px-4 py-2 rounded-lg max-w-[75%] shadow-lg text-sm
                    ${
                      msg.sender === "user"
                        ? "bg-purple-800 text-purple-100"
                        : "bg-gray-800 text-gray-200 border border-purple-900"
                    }
                    ${msg.sender === "bot" ? "italic" : ""}
                  `}>
                {msg.text}
              </span>
            </div>
          ))}
        </div>
        <div className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleInputKeyDown}
            placeholder="Speak to the darkness..."
            className="flex-1 px-4 py-2 rounded-lg bg-gray-800 text-gray-100 border border-gray-700 focus:outline-none focus:ring-2 focus:ring-purple-700"
          />
          <button
            onClick={handleSend}
            className="px-6 py-2 rounded-lg bg-purple-700 text-white font-bold shadow hover:bg-purple-900 transition">
            Send
          </button>
        </div>
      </div>

      <h1 className="text-2xl font-bold text-purple-400 mb-4 text-center tracking-widest drop-shadow-lg font-Cinzel">
        How far can you reach?
      </h1>
    </div>
  );
}

export default ChatBox;
