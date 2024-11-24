import { useState, useEffect } from "react";
import { PuffLoader } from "react-spinners";
import { useSearchParams } from "react-router";

function Play() {
  const [searchParams] = useSearchParams();

  const mode = searchParams.get("mode");

  let page_width = window.innerWidth;
  let page_height = window.innerHeight;

  const [gameloaded, setGameLoaded] = useState(false);

  const pushToStorage = (name: string, score: number) => {
    const jsonData = JSON.parse(localStorage.getItem(name)!);

    jsonData.push({
      initials: "TST",
      highscore: score.toString(),
    });

    const jsonString = JSON.stringify(jsonData);

    localStorage.setItem(name, jsonString);
  };

  useEffect(() => {
    const interval = setInterval(() => {
      fetch("http://localhost:8000/score")
        .then((response) => {
          if (!response.ok) {
            throw new Error("Failed to fetch high scores");
          }
          return response.json();
        })
        .then((data) => {
          if (data.finished == "True") {
            if (mode == "scoring-mode") {
              pushToStorage("highscores", data.score);
              clearInterval(interval);
            } else if (mode == "survival") {
              pushToStorage("survivalScores", data.score);
              clearInterval(interval);
            }
          }
        })
        .catch((error) => console.error("Error saving score", error));
    }, 1000);

    return () => clearInterval(interval);
  }, []);

  // Function to restart the game
  const restartGame = async () => {
    try {
      const response = await fetch("http://localhost:8000/restart", {
        method: "POST",
      });
      if (response.ok) {
        alert("Game restarted successfully!");
        // Optionally reload the current page to restart the game session
        window.location.reload();
      } else {
        alert("Failed to restart the game.");
      }
    } catch (error) {
      console.error("Error restarting the game:", error);
      alert("An error occurred while restarting the game.");
    }
  };

  return (
    <>
      <div className="flex flex-col w-[100vw] justify-center items-center text-center">
        {/* Loader while the game is loading */}
        {gameloaded ? null : <PuffLoader size={400} color="#e53e3e" />}

        {/* Game feed */}
        <img
          onLoad={() => setGameLoaded(true)}
          style={gameloaded ? {} : { display: "none" }}
          src={`http://localhost:8000/boxing_feed?page_width=${page_width}&page_height=${page_height}&mode=${mode}`}
          alt="BoxAR Interactive window"
        />
      </div>

      {/* Restart Game Button */}
      <div className="flex justify-center mt-8">
        <button
          onClick={restartGame}
          className="px-6 py-3 bg-red-500 text-white font-semibold rounded-lg hover:bg-red-600 shadow-md"
        >
          Restart Game
        </button>
      </div>
    </>
  );
}

export default Play;
