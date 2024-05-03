import { backendURL } from "../Utils/getENV";
interface VideoStreamProps {
    id: number;
}

const VideoStream: React.FC<VideoStreamProps> = ({ id }) => {
    const streamUrl = `${backendURL}/video_feed/${id}`;

    return (
        <img
            className="h-auto max-w-lg mx-auto rounded-lg shadow-xl dark:shadow-gray-800 object-contain"
            src={streamUrl}
            alt="image description"
        />
    );
};

export default VideoStream;
