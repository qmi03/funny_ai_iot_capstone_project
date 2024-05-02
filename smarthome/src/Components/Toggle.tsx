import { useState } from "react";
import { Switch } from "@headlessui/react";

interface ToggleProp {
    onToggle: (state: boolean) => void;
    initialState: boolean;
}
const Toggle: React.FC<ToggleProp> = ({ onToggle, initialState }) => {
    const [enabled, setEnabled] = useState(initialState);

    const handleChange = (state: boolean) => {
        setEnabled(state);
        onToggle(state);
    };

    return (
        <Switch
            checked={enabled}
            onChange={handleChange}
            className={`${
                enabled ? "bg-green-400" : "bg-gray-200"
            } relative inline-flex h-6 w-11 items-center rounded-full`}
        >
            <span className="sr-only">Enable notifications</span>
            <span
                className={`${
                    enabled ? "translate-x-6" : "translate-x-1"
                } inline-block h-4 w-4 transform rounded-full bg-white transition`}
            />
        </Switch>
    );
};
export default Toggle;
