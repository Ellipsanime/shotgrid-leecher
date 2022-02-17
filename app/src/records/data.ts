export interface IScheduleLog {
  batchResult: string
  datetime: string
  id: string
  data: any
}

export interface IScheduleProject {
  projectId: number
  projectName: string
  scriptName: string
  url: string
  datetime: string
  latestLogs: Array<IScheduleLog>
}

export interface ILog {
  id: string
  result: string
  data?: string
  datetime: string
  duration: number
  projectId: number
  projectName: string
}
