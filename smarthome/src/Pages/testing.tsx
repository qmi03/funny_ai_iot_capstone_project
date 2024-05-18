import { useEffect, useState } from "react";

import Mic from "../Components/Mic";
import RealTimeGraph from "../Components/Sensor/RealTimeGraph";
import { backendURL } from "../Utils/getENV";
const Testing = () => {
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
            <Mic />
            {sensorIds.map((sensorId) => (
                <RealTimeGraph key={sensorId} sensorId={sensorId} />
            ))}
        </>
    );
};

export default Testing;
