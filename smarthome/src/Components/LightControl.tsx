import Toggle from "./Toggle";
import { Card } from "flowbite-react";
import { useEffect, useState } from "react";
interface LightControllerProps {
    room: string;
    lights: string[];
}

const LightController: React.FC<LightControllerProps> = ({ room, lights }) => {
    const handleToggle = (lightId: string, state: boolean) => {
        fetch("http://192.168.1.20:8000/light", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                room: room,
                light_id: lightId,
                state: state ? "ON" : "OFF",
            }),
        })
            .then((response) => response.json())
            .then((data) => console.log(data))
            .catch((error) => {
                console.error("Error:", error);
            });
    };
    const [lightStates, setLightStates] = useState<Record<string, boolean>>({});

    useEffect(() => {
        lights.forEach((light) => {
            console.log("fetching");
            fetch(
                `http://192.168.1.20:8000/light_state?room=${room}&light_id=${light}`
            )
                .then((response) => response.json())
                .then((data) =>
                    setLightStates((prevStates) => ({
                        ...prevStates,
                        [light]: data.state === "ON",
                    }))
                )
                .catch((error) => console.error("Error:", error));
        });
    }, [room, lights]);

    return (
        <Card className="max-w-sm rounded-xl m-2">
            <h1 className=" text">Điều khiển đèn phòng {room}</h1>
            {lights.map((light: string) => (
                <div
                    key={light}
                    className="flex justify-between items-center mb-4"
                >
                    <h2>Đèn {light}</h2>
                    <Toggle
                        onToggle={(state) => handleToggle(light, state)}
                        initialState={lightStates[light]}
                    />
                </div>
            ))}
        </Card>
    );
};
export default LightController;
