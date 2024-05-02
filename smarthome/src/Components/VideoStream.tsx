interface VideoStreamProps {
    id: number;
}

const VideoStream: React.FC<VideoStreamProps> = ({ id }) => {
    // Replace with your Flask server URL
    const streamUrl = `http://192.168.1.20:8000/video_feed/${id}`;

    return (
        <img
            className="h-auto max-w-lg mx-auto rounded-lg shadow-xl dark:shadow-gray-800 object-contain"
            src={streamUrl}
            alt="image description"
        />
    );
};

export default VideoStream;
