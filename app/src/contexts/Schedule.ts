import {createContext} from "react";
import {IScheduleProject} from "../services/scheduleService";

export interface IScheduleDataContext {
  projectToDelete?: IScheduleProject
  setProjectToDelete: (_: IScheduleProject | undefined) => any
  projects: Array<IScheduleProject>
  setProjects: (_: Array<IScheduleProject>) => any
}

const ScheduleDataContext = createContext<IScheduleDataContext>({
  setProjectToDelete: () => {},
  setProjects: () => {},
  projects: [],
});

export default ScheduleDataContext;
