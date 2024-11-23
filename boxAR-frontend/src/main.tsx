import { BrowserRouter, Routes, Route } from "react-router";
import { createRoot } from "react-dom/client";
import "./index.css";
import App from "./App.tsx";
import NavBar from "./components/navbar.tsx";

/ * IMPORT PAGES * /;
import Play from "@/pages/Play.tsx";

createRoot(document.getElementById("root")!).render(
  <BrowserRouter>
    <NavBar />
    <Routes>
      <Route path="/" element={<App />} />
      <Route path="/play" element={<Play />} />
    </Routes>
  </BrowserRouter>
);
