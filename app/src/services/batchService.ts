import {IBatchFormData, Result} from "../records/batch";
import axios from "axios";

const apiUrl = process.env.REACT_APP_API_URI || ""
const commonHeaders = {
      'Access-Control-Allow-Origin': '*',
      'Content-Type': 'application/json',
    };

function toLeecherBatch(formData: IBatchFormData): {[_: string]: any } {
    return {
      "shotgrid_url": formData.urlProtocol + "://" + formData.urlPath,
      "shotgrid_project_id": formData.shotgridProjectId,
      "script_name": formData.scriptName,
      "script_key": formData.apiKey,
      "overwrite": formData.overwrite,
      "fields_mapping": JSON.parse(formData?.fieldsMapping || "{}")
    }
}

export async function batch(formData: IBatchFormData): Promise<Result> {
    const url = `${apiUrl}/batch/${formData.openpypeProject}`;
    const data = toLeecherBatch(formData);
    try {
        const response = await axios.post(url, data, {headers: commonHeaders});
        return {status: response.status};
    } catch (error: any) {
        return {
            errorStatus: error?.response?.status || -1,
            errorMessage: ""+ error+", details: "+ JSON.stringify(error?.response?.data),
        };
    }
}
