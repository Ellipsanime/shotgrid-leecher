import {createContext} from "react";
import {IScheduleProject} from "../services/scheduleService";

export interface IScheduleDataContext {
  projectToDelete?: IScheduleProject
  setProjectToDelete: (_: IScheduleProject | undefined) => any
  projects: Array<IScheduleProject>
  setProjects: (_: Array<IScheduleProject>) => any
}

export interface IScheduleDialogContext {
  create: boolean
  setCreate: (_: boolean) => any
}

const ScheduleDataContext = createContext<IScheduleDataContext>({
  setProjectToDelete: () => {},
  setProjects: () => {},
  projects: [],
});

const ScheduleDialogContext = createContext<IScheduleDialogContext>({
  create: false,
  setCreate: () => {},
});

export {ScheduleDialogContext, ScheduleDataContext};
