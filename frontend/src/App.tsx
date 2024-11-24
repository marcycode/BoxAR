import { useEffect } from "react";
import logoDark from "@/assets/boxar-logo-dark.png";
//import logoLight from "@/assets/boxer-logo-light.png";

function App() {
  // Fetch high scores from the JSON file
  useEffect(() => {
    fetch("/highscore.json")
      .then((response) => {
        if (!response.ok) {
          throw new Error("Failed to fetch high scores");
        }
        return response.json();
      })
      .then((data) => {
        if (localStorage.getItem("highscores") === null) {
          localStorage.setItem("highscores", JSON.stringify(data));
        }
      })
      .catch((error) => console.error("Error setting high scores:", error));

    fetch("/survivalScores.json")
      .then((response) => {
        if (!response.ok) {
          throw new Error("Failed to fetch survival scores");
        }
        return response.json();
      })
      .then((data) => {
        if (localStorage.getItem("survivalScores") === null) {
          localStorage.setItem("survivalScores", JSON.stringify(data));
        }
      })
      .catch((error) => console.error("Error setting survival scores:", error));
  }, []);

  return (
    <>
      <div className="flex flex-col w-[100vw] justify-center items-center text-center">
        <img src={logoDark} alt="BoxAR Logo" width={"30%"} height={"30%"} />
        <span className="mt-4 text-xl md:text-3xl">
          <b>
            Shadow boxing taken to the <i>next level</i>
          </b>
        </span>
      </div>
      <div></div>
    </>
  );
}

export default App;
