import { useEffect, useState } from "react";
import LightController from "./LightControl";
import { backendURL } from "../../Utils/getENV";
import { Card } from "flowbite-react";

type LightSysType = {
    [key: string]: string[];
};

const Lighting = () => {
    const [lightSys, setLightSys] = useState<LightSysType>({});

    useEffect(() => {
        fetch(`${backendURL}/light/sys`)
            .then((response) => response.json())
            .then((data) => setLightSys(data));
    }, []);

    return (
        <div className="flex flex-wrap justify-start items-start">
            {Object.entries(lightSys).map(([room, lights]) => (
                <LightController key={room} room={room} lights={lights} />
            ))}
        </div>
    );
};
export default Lighting;
