import {ILog} from "../records/data";
import axios from "axios";
import {CommonHeaders, formatDatetime} from "../tools/requests";

const apiUrl = process.env.REACT_APP_API_URI || "";

export async function fetchTopNLogs(top: number): Promise<ILog[]> {
  const url = `${apiUrl}/schedule/logs?sort_field=datetime&sort_order=-1&limit=${top}`;
  try {
    const response = await axios.get(url, {headers: CommonHeaders});
    return (response.data || []).map((x: any) => ({
      id: x.id,
      projectName: x.project_name,
      projectId: x.project_id,
      data: JSON.stringify(x.data, null, 2),
      result: x.batch_result,
      datetime: formatDatetime(x.datetime),
    } as ILog)) || [];
  } catch (error: any) {
    throw error;
  }
}
