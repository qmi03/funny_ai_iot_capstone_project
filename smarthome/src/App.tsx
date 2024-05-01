import "./index.css";
import Dashboard from "./Pages/Dashboard";
import Header from "./Components/Header";
import { BrowserRouter, Routes, Route } from "react-router-dom";
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
                    </Routes>
                </Header>
            </BrowserRouter>
        </div>
    );
}
