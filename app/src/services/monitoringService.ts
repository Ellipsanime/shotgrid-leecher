import {ILog} from "../records/data";
import axios from "axios";
import {CommonHeaders, formatDatetime} from "../tools/requests";
import {loadConfig} from "../tools/config";


export async function fetchTopNLogs(top: number): Promise<ILog[]> {
  const apiUrl = loadConfig().activeUri;
  const url = `${apiUrl}/schedule/logs?sort_field=datetime&sort_order=-1&limit=${top}`;
  try {
    const response = await axios.get(url, {headers: CommonHeaders});
    return (response.data || []).map((x: any) => ({
      id: x.id,
      projectName: x.project_name,
      projectId: x.project_id,
      data: !!x.data ? JSON.stringify(x.data, null, 2) : undefined,
      result: x.batch_result,
      datetime: formatDatetime(x.datetime),
      duration: x.duration?.toFixed(2),
    } as ILog)) || [];
  } catch (error: any) {
    throw error;
  }
}
