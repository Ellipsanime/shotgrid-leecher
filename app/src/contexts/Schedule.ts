import {createContext} from "react";
import {IScheduleProject} from "../records/data";

export interface IScheduleDataContext {
  projectToDelete?: IScheduleProject
  setProjectToDelete: (_: IScheduleProject | undefined) => any
  projects: IScheduleProject[]
  setProjects: (_: IScheduleProject[]) => any
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
