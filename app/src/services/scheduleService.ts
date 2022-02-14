import axios from "axios";
import format from 'date-fns/format'

const commonHeaders = {
    'Access-Control-Allow-Origin': '*',
    'Content-Type': 'application/json',
};

const apiUrl = process.env.REACT_APP_API_URI || ""

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

export async function deleteSchedule(project:IScheduleProject): Promise<any> {
    const url = `${apiUrl}/schedule/${project.projectName}`;
    try {
        return await axios.delete(url, {headers: commonHeaders});
    } catch (error: any) {
        throw error
    }
}

export async function fetchProjects(): Promise<Array<IScheduleProject>> {
    const url = `${apiUrl}/schedule/enhanced-projects?sort_field=datetime&sort_order=-1`;
    try {
        const response = await axios.get(url, {headers: commonHeaders});
        return (response.data || []).map((x: any) => ({
            projectId: x.project_id,
            projectName: x.project_name,
            scriptName: x.credential_script,
            url: x.credential_url,
            latestLogs: x.latest_logs?.map((y: any) => ({
                batchResult: y.batch_result,
                datetime: format(Date.parse(x.datetime), "yy-MM-dd' at 'HH:mm"),
                id: y.id,
                data: y.data,
            })) || [],
            datetime: format(Date.parse(x.datetime), "yy-MM-dd' at 'HH:mm"),
        }));
    } catch (error: any) {
        throw error
    }
}
