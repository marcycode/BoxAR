import {
  NavigationMenu,
  NavigationMenuItem,
  NavigationMenuLink,
  NavigationMenuList,
} from "@/components/ui/navigation-menu";
import { useNavigate, useLocation } from "react-router";
import logoDark from "@/assets/boxar-logo-dark.png";
//import logoLight from "@/assets/boxer-logo-light.png";

export default function NavBar() {
  let navigate = useNavigate();
  const location = useLocation();
  const { pathname } = location;

  return (
    <div className="flex w-full absolute top-2 justify-between p-2">
      <img
        src={logoDark}
        width={"5%"}
        height={"5%"}
        className="cursor-pointer"
        onClick={() => navigate("/")}
      />
      {pathname == "/" ? (
        <NavigationMenu>
          <NavigationMenuList>
            <NavigationMenuItem className="cursor-pointer">
              <NavigationMenuLink
                className="bg-slate-300 hover:bg-red-500 rounded-md hover:text-white text-black px-[1vw] py-[1.2vw] mx-2"
                onClick={() => navigate("/select-mode")}
              >
                Fight Now
              </NavigationMenuLink>
            </NavigationMenuItem>
            <NavigationMenuItem className="cursor-pointer">
              <NavigationMenuLink
                className="bg-slate-300 hover:bg-blue-500 rounded-md hover:text-white text-black px-[1vw] py-[1.2vw] mx-2"
                onClick={() => navigate("/leaderboard")}
              >
                View Leaderboard
              </NavigationMenuLink>
            </NavigationMenuItem>
          </NavigationMenuList>
        </NavigationMenu>
      ) : (
        <></>
      )}
    </div>
  );
}
