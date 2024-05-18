import { useEffect, useState, FC } from "react";
import { Line } from "react-chartjs-2";
import { Chart, registerables } from "chart.js";
import { backendURL } from "../../Utils/getENV";
Chart.register(...registerables);

interface SensorData {
    sensor_id: string;
    sensor_type: string;
    value: number;
    timestamp: string;
}

interface RealTimeGraphProps {
    sensorId: string;
}

const RealTimeGraph: FC<RealTimeGraphProps> = ({ sensorId }) => {
    const [data, setData] = useState<{
        labels: string[];
        datasets: { label: string; data: number[]; borderColor: string }[];
    }>({
        labels: [],
        datasets: [
            {
                label: `Sensor Data - ${sensorId}`,
                data: [],
                borderColor: "rgba(75, 192, 192, 1)",
            },
        ],
    });

    useEffect(() => {
        const fetchHistoricalData = async () => {
            try {
                const response = await fetch(
                    `${backendURL}/sensor/data/history?sensor_id=${sensorId}&hours=24`
                );
                const historicalData: SensorData[] = await response.json();
                console.log(historicalData);
                const labels = historicalData.map((d) => {
                    const date = new Date(d.timestamp);
                    return `${date.getHours()}:${date.getMinutes()}:${date.getSeconds()}`;
                });
                const values = historicalData.map((d) => d.value);

                setData({
                    labels,
                    datasets: [
                        {
                            label: `Sensor Data - ${sensorId}`,
                            data: values,
                            borderColor: "rgba(75, 192, 192, 1)",
                        },
                    ],
                });
            } catch (error) {
                console.error("Error fetching historical data:", error);
            }
        };

        fetchHistoricalData();

        const ws = new WebSocket("ws://localhost:8000/ws/sensor_data");

        ws.onmessage = (event) => {
            const newData: SensorData = JSON.parse(event.data);

            if (newData.sensor_id === sensorId) {
                setData((prevData) => ({
                    labels: [...prevData.labels, newData.timestamp],
                    datasets: [
                        {
                            ...prevData.datasets[0],
                            data: [...prevData.datasets[0].data, newData.value],
                        },
                    ],
                }));
            }
        };

        return () => {
            if (ws.readyState === 1) {
                ws.close();
            }
        };
    }, [sensorId]);

    return (
        <div className="p-4 w-full h-80">
            <Line data={data} options={{ maintainAspectRatio: false }} />
        </div>
    );
};

export default RealTimeGraph;
