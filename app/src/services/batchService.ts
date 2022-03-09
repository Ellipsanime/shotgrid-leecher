import {IBatchFormData, Result} from "../records/forms";
import axios from "axios";
import {CommonHeaders, toLeecherBase} from "../tools/requests";
import {loadConfig} from "../tools/config";


function toLeecherBatch(formData: IBatchFormData): { [_: string]: any } {
  return {
    ...toLeecherBase(formData),
    "overwrite": formData.overwrite,
  }
}

export async function batch(formData: IBatchFormData): Promise<Result> {
  const apiUrl = loadConfig().activeUri;
  const url = `${apiUrl}/batch/${formData.openpypeProject}`;
  const data = toLeecherBatch(formData);
  try {
    const response = await axios.post(url, data, {headers: CommonHeaders});
    return {status: response.status};
  } catch (error: any) {
    return {
      errorStatus: error?.response?.status || -1,
      errorMessage: "" + error + ", details: " + JSON.stringify(error?.response?.data),
    };
  }
}
