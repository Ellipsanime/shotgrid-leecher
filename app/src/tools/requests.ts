import {Failure, IBatchFormData, IScheduleFormData} from "../records/forms";

export function toFailure(error: any): Failure {
  return {
    errorStatus: error?.response?.status || -1,
    errorMessage: "" + error + ", details: " + JSON.stringify(error?.response?.data),
  };
}

export const CommonHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Content-Type': 'application/json',
};

export function toLeecherBase(data: IBatchFormData | IScheduleFormData) {
  return {
    "shotgrid_url": data.urlProtocol + "://" + data.urlPath,
    "shotgrid_project_id": data.shotgridProjectId,
    "script_name": data.scriptName,
    "script_key": data.apiKey,
    "fields_mapping": JSON.parse(data?.fieldsMapping || "{}"),
  }
}
