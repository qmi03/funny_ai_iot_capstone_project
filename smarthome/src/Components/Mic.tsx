import { useState, useRef } from "react";
const mimeType = "audio/flac";
import { backendURL, huggingfaceKEY } from "../Utils/getENV";
const Mic = () => {
    const [permission, setPermission] = useState(false);
    const [stream, setStream] = useState<MediaStream | null>(null);
    const mediaRecorder = useRef<MediaRecorder | null>(null);
    const [recordingStatus, setRecordingStatus] = useState("inactive");
    const [audioChunks, setAudioChunks] = useState<BlobPart[]>([]);
    const [audio, setAudio] = useState<string | null>(null);
    const sendAudioToServer = async (audioBlob: Blob): Promise<any> => {
        const formData = new FormData();
        formData.append("file", audioBlob, "audio.flac");

        const response = await fetch(`${backendURL}/audio`, {
            method: "POST",
            body: formData,
        });

        return response.json();
    };
    const startRecording = async () => {
        if (stream) {
            setRecordingStatus("recording");
            //create new Media recorder instance using the stream
            const media = new MediaRecorder(stream);
            //set the MediaRecorder instance to the mediaRecorder ref
            mediaRecorder.current = media;
            //invokes the start method to start the recording process
            mediaRecorder.current.start();
            let localAudioChunks: BlobPart[] = [];
            mediaRecorder.current.ondataavailable = (event: BlobEvent) => {
                if (typeof event.data === "undefined") return;
                if (event.data.size === 0) return;
                localAudioChunks.push(event.data);
            };
            setAudioChunks(localAudioChunks);
        }
    };
    const stopRecording = () => {
        if (mediaRecorder.current) {
            setRecordingStatus("inactive");
            //stops the recording instance
            mediaRecorder.current.stop();
            mediaRecorder.current.onstop = async () => {
                //creates a blob file from the audiochunks data
                const audioBlob = new Blob(audioChunks, { type: mimeType });
                //creates a playable URL from the blob file.
                const audioUrl = URL.createObjectURL(audioBlob);
                setAudio(audioUrl);
                setAudioChunks([]);
                try {
                    const result = await sendAudioToServer(audioBlob);
                    console.log(result);
                } catch (error) {
                    console.error("Error:", error);
                }
            };
        }
    };

    const getMicrophonePermission = async () => {
        if ("MediaRecorder" in window) {
            try {
                const streamData = await navigator.mediaDevices.getUserMedia({
                    audio: true,
                    video: false,
                });
                setPermission(true);
                setStream(streamData);
            } catch (err: any) {
                alert(err.message);
            }
        } else {
            alert("The MediaRecorder API is not supported in your browser.");
        }
    };
    return (
        <div className="audio-controls">
            {!permission ? (
                <button onClick={getMicrophonePermission} type="button">
                    Get Microphone
                </button>
            ) : null}
            {permission && recordingStatus === "inactive" ? (
                <button onClick={startRecording} type="button">
                    Start Recording
                </button>
            ) : null}
            {recordingStatus === "recording" ? (
                <button onClick={stopRecording} type="button">
                    Stop Recording
                </button>
            ) : null}
            {audio ? (
                <div className="audio-container">
                    <audio src={audio} controls></audio>
                </div>
            ) : null}
        </div>
    );
};
export default Mic;
