import "./index.css";
import Dashboard from "./Pages/Dashboard";
import Header from "./Components/Header";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Camera from "./Pages/Camera";
import Report from "./Pages/Report";
import Schedule from "./Pages/Schdule";
import { useEffect } from "react";
import addNotification, { Notifications } from "react-push-notification";
import { socket } from "./Utils/socket";
import Testing from "./Pages/testing";
export default function App() {
    useEffect(() => {
        const handleNotification = (data: any) => {
            console.log("notification from app", data.message);
            addNotification({
                title: "Hello title",
                subtitle: "This is a subtitle",
                message: data.message,
                theme: "darkblue",
                native: false,
            });
        };

        socket.on("notification", handleNotification);

        return () => {
            socket.off("notification", handleNotification);
        };
    }, []);

    return (
        <div className="app min-h-screen">
            <Notifications />
            <BrowserRouter>
                <Header>
                    <Routes>
                        <Route
                            path="/dashboard"
                            element={<Dashboard />}
                        ></Route>
                        <Route path="/camera" element={<Camera />}></Route>
                        <Route path="/report" element={<Report />}></Route>
                        <Route path="/schedule" element={<Schedule />}></Route>
                        <Route path="/test" element={<Testing />}></Route>
                    </Routes>
                </Header>
            </BrowserRouter>
        </div>
    );
}
