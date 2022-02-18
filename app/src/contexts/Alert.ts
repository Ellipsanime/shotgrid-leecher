import {AlertColor} from "@mui/material/Alert/Alert";
import {createContext} from "react";

export interface IAlert {
    severity: AlertColor
    message: string
    title?: string
}

export interface IAlertContext {
    alert?: IAlert
    setAlert: (_: IAlert | undefined) => any
}

const AlertContext = createContext<IAlertContext>({setAlert: () => {}});

export default AlertContext;
