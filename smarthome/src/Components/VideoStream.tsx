import { useState } from "react";
import Toggle from "./Toggle";
import { backendURL } from "../Utils/getENV";

interface VideoStreamProps {
    id: number;
}

const VideoStream: React.FC<VideoStreamProps> = ({ id }) => {
    const [detectionEnabled, setDetectionEnabled] = useState(false);
    const streamUrl = `${backendURL}/video_feed/?id=${id}&box=${detectionEnabled}`;

    const handleToggle = async (state: boolean) => {
        setDetectionEnabled(state);
        const response = await fetch(
            `${backendURL}/detection/${
                state ? "start" : "stop"
            }?stream_id=${id}`,
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
            }
        );

        const data = await response.json();
        console.log(data.message);
    };
    return (
        <div className="flex flex-col items-center">
            <div className="w-full max-w-md p-4 bg-white dark:bg-gray-800 rounded-lg shadow-md">
                <Toggle onToggle={handleToggle} initialState={false} />
                <text> Chạy model trong nền và gửi thông báo</text>
            </div>
            <img
                className="h-auto max-w-lg mx-auto rounded-lg shadow-xl dark:shadow-gray-800 object-contain mt-4"
                src={streamUrl}
                alt="image description"
            />
        </div>
    );
};

export default VideoStream;
