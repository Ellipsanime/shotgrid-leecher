import axios from "axios";
import {IScheduleFormData, Result} from "../records/forms";
import {
  CommonHeaders,
  formatDatetime,
  toFailure,
  toLeecherBase
} from "../tools/requests";
import {IScheduleProject} from "../records/data";
import {loadConfig} from "../tools/config";


export async function deleteSchedule(project: IScheduleProject): Promise<Result> {
  const apiUrl = loadConfig().activeUri;
  const url = `${apiUrl}/schedule/${project.projectName}`;
  try {
    const data = await axios.delete(url, {headers: CommonHeaders});
    return {status: data.status};
  } catch (error: any) {
    return toFailure(error);
  }
}

const toLeecherAddSchedule: (_: IScheduleFormData) => { [_: string]: any } = toLeecherBase

export async function createSchedule(data: IScheduleFormData): Promise<Result> {
  const apiUrl = loadConfig().activeUri;
  const url = `${apiUrl}/schedule/${data.openpypeProject}`;
  try {
    const result = await axios.post(url, toLeecherAddSchedule(data), {headers: CommonHeaders});
    return {status: result.status};
  } catch (error: any) {
    return toFailure(error);
  }
}

export async function fetchProjects(): Promise<IScheduleProject[]> {
  const apiUrl = loadConfig().activeUri;
  const url = `${apiUrl}/schedule/enhanced-projects?sort_field=datetime&sort_order=-1`;
  try {
    const response = await axios.get(url, {headers: CommonHeaders});
    return (response.data || []).map((x: any) => ({
      projectId: x.project_id,
      projectName: x.project_name,
      scriptName: x.credential_script,
      url: x.credential_url,
      latestLogs: x.latest_logs?.map((y: any) => ({
        batchResult: y.batch_result,
        datetime: formatDatetime(y.datetime),
        id: y.id,
        data: y.data,
      })) || [],
      datetime: formatDatetime(x.datetime),
    }));
  } catch (error: any) {
    throw error;
  }
}
