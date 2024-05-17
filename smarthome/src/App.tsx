import "./index.css";
import Dashboard from "./Pages/Dashboard";
import Header from "./Components/Header";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Camera from "./Pages/Camera";
import Report from "./Pages/Report";
import Schedule from "./Pages/Schdule";
import { useEffect } from "react";
import addNotification, { Notifications } from "react-push-notification";
import { ws } from "./Utils/socket";
import Testing from "./Pages/testing";
export default function App() {
    useEffect(() => {
        ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            addNotification({
                title: "Notification",
                subtitle: "Alert",
                message: data.message,
                theme: "darkblue",
                native: false,
            });
        };

        ws.onopen = () => {
            console.log("WebSocket connection opened");
        };

        ws.onclose = () => {
            console.log("WebSocket connection closed");
        };

        ws.onerror = (error) => {
            console.error("WebSocket error", error);
        };

        return () => {
            if (ws.readyState === 1) {
                ws.close();
            }
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
