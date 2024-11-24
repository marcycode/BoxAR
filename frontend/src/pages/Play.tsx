import { useState } from "react";
import { PuffLoader } from "react-spinners";
import { useSearchParams } from "react-router";

function Play() {
  const [searchParams] = useSearchParams();

  const mode = searchParams.get("mode");

  let page_width = window.innerWidth;
  let page_height = window.innerHeight;

  const [gameloaded, setGameLoaded] = useState(false);

  return (
    <>
      <div className="flex flex-col w-[100vw] justify-center items-center text-center">
        {gameloaded ? null : <PuffLoader size={400} color="#e53e3e" />}
        <img
          onLoad={() => setGameLoaded(true)}
          style={gameloaded ? {} : { display: "none" }}
          src={`http://localhost:8000/boxing_feed?page_width=${page_width}&page_height=${page_height}&mode=${mode}`}
          alt="BoxAR Interactive window"
        />
      </div>
      <div></div>
    </>
  );
}

export default Play;
