import {ILog} from "../records/data";
import {createContext} from "react";

export interface ILogDataContext {
  logs: ILog[]
  setLogs: (_: ILog[]) => any
}

export const LogDataContext = createContext<ILogDataContext>({logs: [], setLogs: () => {}})
