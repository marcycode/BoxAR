import React, { useEffect, useState } from "react";
import './Leaderboard.css';


// Define the TypeScript interface for a player
interface Player {
  initials: string;
  highscore: number;
}

const Leaderboard: React.FC = () => {
  const [players, setPlayers] = useState<Player[]>([]);

  // Fetch high scores from the JSON file
  useEffect(() => {
    fetch("/highscore.json")
      .then((response) => {
        if (!response.ok) {
          throw new Error("Failed to fetch high scores");
        }
        return response.json();
      })
      .then((data: Player[]) => setPlayers(data))
      .catch((error) => console.error("Error loading high scores:", error));
  }, []);

  return (
    <div className="flex flex-col w-[100vw] justify-center items-center text-center">
      <h1 className="text-2xl font-bold mb-4">Leaderboard</h1>
      <div className="w-[50%]">
        <table className="w-full border-collapse border border-gray-300">
          <thead>
            <tr className="bg-gray-200">
              <th className="border border-gray-300 px-4 py-2">Rank</th>
              <th className="border border-gray-300 px-4 py-2">Initials</th>
              <th className="border border-gray-300 px-4 py-2">High Score</th>
            </tr>
          </thead>
          <tbody>
            {players
              .sort((a, b) => b.highscore - a.highscore) // Sort by highscore descending
              .map((player, index) => (
                <tr key={index} className="odd:bg-white even:bg-gray-100">
                  <td className="border border-gray-300 px-4 py-2">{index + 1}</td>
                  <td className="border border-gray-300 px-4 py-2">{player.initials}</td>
                  <td className="border border-gray-300 px-4 py-2">{player.highscore}</td>
                </tr>
              ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default Leaderboard;
