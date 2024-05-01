import "./index.css";
import Dashboard from "./Pages/Dashboard";
import Header from "./Components/Header";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Camera from "./Pages/Camera";
import Report from "./Pages/Report";
import Schedule from "./Pages/Schdule";
export default function App() {
    return (
        <div>
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
                    </Routes>
                </Header>
            </BrowserRouter>
        </div>
    );
}
