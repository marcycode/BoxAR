import { useNavigate } from "react-router";
import { Card, CardContent } from "@/components/ui/card";

function SelectMode() {
  let navigate = useNavigate();

  return (
    <>
      <div className="flex flex-col w-[100vw] justify-center items-center text-center">
        <span className="text-xl md:text-4xl mb-4">
          <b>Select Mode</b>
        </span>
        <div className="flex flew-row gap-8">
          <Card className="rounded-xl">
            <CardContent
              className="flex w-[20vw] h-[20vw] hover:shadow-xl items-center justify-center p-6 bg-free-play bg-cover rounded-xl cursor-pointer"
              onClick={() => navigate("/play")}
            >
              <span className="text-2xl font-semibold text-white">
                Free Play
              </span>
            </CardContent>
          </Card>
          <Card className="rounded-xl">
            <CardContent className="flex w-[20vw] h-[20vw] hover:shadow-xl items-center justify-center p-6 bg-scoring-mode bg-cover rounded-xl cursor-pointer">
              <span className="text-2xl font-semibold text-white">
                Scoring Mode
              </span>
            </CardContent>
          </Card>
          <Card className="rounded-xl">
            <CardContent className="flex w-[20vw] h-[20vw] hover:shadow-xl items-center justify-center p-6 bg-survival bg-cover rounded-xl cursor-pointer">
              <span className="text-2xl font-semibold text-white">
                Survival
              </span>
            </CardContent>
          </Card>
        </div>
      </div>
    </>
  );
}

export default SelectMode;
