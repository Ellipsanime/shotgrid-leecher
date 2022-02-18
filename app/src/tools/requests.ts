import {Failure, IBatchFormData, IScheduleFormData} from "../records/forms";
import format from "date-fns/format";

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

export function formatDatetime(datetime: string) {
  return format(Date.parse(datetime), "yy-MM-dd' at 'HH:mm");
}

export function toLeecherBase(data: IBatchFormData | IScheduleFormData) {
  return {
    "shotgrid_url": data.urlProtocol + "://" + data.urlPath,
    "shotgrid_project_id": data.shotgridProjectId,
    "script_name": data.scriptName,
    "script_key": data.apiKey,
    "fields_mapping": JSON.parse(data?.fieldsMapping || "{}"),
  }
}
