import {createContext} from "react";

export interface IEnv {
    name: string
}

export interface IEnvContext {
    env?: IEnv
    setEnv: (_: IEnv) => any
}

const EnvContext = createContext<IEnvContext>({setEnv: () => {}});

export default EnvContext;
