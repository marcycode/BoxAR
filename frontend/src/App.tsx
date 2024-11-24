import logoDark from "@/assets/boxar-logo-dark.png";
//import logoLight from "@/assets/boxer-logo-light.png";

function App() {
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
