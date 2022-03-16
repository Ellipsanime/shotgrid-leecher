import * as yup from "yup";
import {useRef} from "react";


export function getScheduleObjectShape(): {} {
    return {
        openpypeProject: yup.string().min(3).required(),
        shotgridUrl: yup.string().required(),
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
