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

export interface IBatchOkResult {
    status: number;
}

export interface IBatchKoResult {
    errorMessage: string;
    errorStatus: number;
}

export type IBatchResult = IBatchOkResult | IBatchKoResult
