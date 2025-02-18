import React, { useEffect, useState } from "react";

function App() {
  const [signals, setSignals] = useState([]);

  useEffect(() => {
    // Fetch signals from the backend
    fetch("https://your-render-backend-url/signals") // Replace with your Render backend URL
      .then((response) => response.json())
      .then((data) => setSignals(data));
  }, []);

  return (
    <div style={{ padding: "20px", fontFamily: "Arial, sans-serif" }}>
      <h1>Stewie Trading Signals</h1>
      <h2>Latest Signals</h2>
      {signals.length > 0 ? (
        <ul style={{ listStyleType: "none", padding: 0 }}>
          {signals.map((signal, index) => (
            <li
              key={index}
              style={{
                padding: "10px",
                margin: "10px 0",
                border: "1px solid #ccc",
                borderRadius: "5px",
                backgroundColor: signal.signal === "buy" ? "#dff0d8" : "#f2dede",
              }}
            >
              <strong>{signal.pair}</strong>: {signal.signal.toUpperCase()} at {signal.price} ({signal.date})
            </li>
          ))}
        </ul>
      ) : (
        <p>No signals generated yet.</p>
      )}
    </div>
  );
}

export default App;
