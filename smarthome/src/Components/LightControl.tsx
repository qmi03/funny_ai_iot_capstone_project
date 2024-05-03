import Toggle from "./Toggle";
import { Card } from "flowbite-react";
import { useEffect, useState } from "react";
import { backendURL } from "../Utils/getENV";
import { Spinner } from "flowbite-react";
interface LightControllerProps {
    room: string;
    lights: string[];
}

const LightController: React.FC<LightControllerProps> = ({ room, lights }) => {
    const handleToggle = (lightId: string, state: boolean) => {
        fetch(`${backendURL}/light`, {
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
    const [isLoading, setIsLoading] = useState(true); // Add this line

    useEffect(() => {
        const fetches = lights.map((light) => {
            return fetch(
                `${backendURL}/light_state?room=${room}&light_id=${light}`
            )
                .then((response) => response.json())
                .then((data) => data.state);
        });

        Promise.all(fetches)
            .then((states) => {
                const newLightStates: Record<string, boolean> = {};
                lights.forEach((light, index) => {
                    newLightStates[light] = states[index];
                });
                setLightStates(newLightStates);
                setIsLoading(false);
            })
            .catch((error) => console.error("Error:", error));
    }, [room, lights]);

    console.log(lightStates);
    return (
        <Card className="max-w-sm rounded-xl m-2">
            {isLoading ? (
                <Spinner color="purple" aria-label="Purple spinner example" />
            ) : (
                <>
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
                </>
            )}
        </Card>
    );
};
export default LightController;
