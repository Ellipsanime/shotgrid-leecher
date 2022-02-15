import {createContext} from "react";
import {IScheduleProject} from "../services/scheduleService";

export interface IScheduleDeleteContext {
    projectToDelete?: IScheduleProject
    setProjectToDelete: (_: IScheduleProject | undefined) => any
}

const ScheduleDeleteContext = createContext<IScheduleDeleteContext>({setProjectToDelete: () => {}});

export default ScheduleDeleteContext;
