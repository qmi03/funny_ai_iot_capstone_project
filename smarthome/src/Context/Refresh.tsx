import { createContext } from "react";

export const RefreshContext = createContext({
    refreshKey: 0,
    refresh: () => {},
});
