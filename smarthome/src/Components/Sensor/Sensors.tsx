import { useEffect, useState } from "react";
import { backendURL } from "../../Utils/getENV";
import RealTimeGraph from "./RealTimeGraph";
import { Card } from "flowbite-react";
const Sensors = () => {
    const [sensorIds, setSensorIds] = useState<string[]>([]);

    useEffect(() => {
        const fetchSensorIds = async () => {
            try {
                const response = await fetch(`${backendURL}/sensor/ids`);
                const data: string[] = await response.json();
                setSensorIds(data);
            } catch (error) {
                console.error("Error fetching sensor IDs:", error);
            }
        };

        fetchSensorIds();
    }, []);

    return (
        <>
            <Card>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 p-4">
                    {sensorIds.map((sensorId) => (
                        <RealTimeGraph key={sensorId} sensorId={sensorId} />
                    ))}
                </div>
            </Card>
        </>
    );
};
export default Sensors;
