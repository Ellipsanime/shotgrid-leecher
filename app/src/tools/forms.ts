import * as yup from "yup";
import {useRef} from "react";

const urlPathRegexp = /^(?!https?:\/\/)(www\.)?[-a-zA-Z0-9@:%._+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_+.~#?&/=]*)/i

export function getScheduleObjectShape(): {} {
    return {
        openpypeProject: yup.string().min(3).required(),
        urlProtocol: yup.string().required(),
        urlPath: yup.string().matches(urlPathRegexp, "Should be a valid url path without protocol type").required(),
        scriptName: yup.string().min(3).required(),
        apiKey: yup.string().min(3).required(),
        shotgridProjectId: yup.number().min(1).required(),
        fieldsMapping: yup.string().nullable(),
    }
}

export function useFirstRender(): boolean {
  const ref = useRef(true);
  const firstRender = ref.current;
  ref.current = false;
  return firstRender;
}
