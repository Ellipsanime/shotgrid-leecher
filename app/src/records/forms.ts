export interface IBatchFormData {
    openpypeProject: string;
    urlProtocol: string;
    urlPath: string;
    scriptName: string;
    apiKey: string;
    shotgridProjectId: number;
    overwrite: boolean;
    fieldsMapping: string;
}

export interface IScheduleFormData {
    openpypeProject: string;
    urlProtocol: string;
    urlPath: string;
    scriptName: string;
    apiKey: string;
    shotgridProjectId: number;
    fieldsMapping: string;
}

export interface Success {
    status: number;
}

export interface Failure {
    errorMessage: string;
    errorStatus: number;
}

export type Result = Success | Failure
