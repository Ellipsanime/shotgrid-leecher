import axios from "axios";

const commonHeaders = {
      'Access-Control-Allow-Origin': '*',
      'Content-Type': 'application/json',
    };

const apiUrl = process.env.REACT_APP_API_URI || ""

export interface IScheduleProject {
  projectId: number;
  projectName: string;
  datetime: string;
}

export async function fetchProjects(): Promise<Array<IScheduleProject>> {
    const url = `${apiUrl}/schedule/projects`;
    try {
        const response = await axios.get(url, {headers: commonHeaders});
        return response.data;
    } catch (error: any) {
        throw error
    }
}
