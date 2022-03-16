export interface IBatchFormData {
    openpypeProject: string;
    shotgridUrl: string;
    shotgridProjectId: number;
    overwrite: boolean;
    fieldsMapping: string;
}

export interface IScheduleFormData {
    openpypeProject: string;
    shotgridUrl: string;
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
