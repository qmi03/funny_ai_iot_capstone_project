import React, { useState } from "react";
import { Button, ButtonGroup } from "flowbite-react";
import VideoStream from "../Components/VideoStream";

export default function Camera() {
    const [cameraId, setCameraId] = useState(0);

    const handleCameraChange = (newCameraId: React.SetStateAction<number>) => {
        setCameraId(newCameraId);
    };

    return (
        <div>
            <ButtonGroup className="flex justify-center">
                <Button color="gray" onClick={() => handleCameraChange(0)}>
                    Camera 1
                </Button>
                <Button color="gray" onClick={() => handleCameraChange(1)}>
                    Camera 2
                </Button>
                <Button color="gray" onClick={() => handleCameraChange(2)}>
                    Camera 3
                </Button>
            </ButtonGroup>

            <VideoStream id={cameraId} />
        </div>
    );
}
