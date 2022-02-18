import Box from "@mui/material/Box";
import * as React from "react";
import {useContext} from "react";
import DialogTitle from "@mui/material/DialogTitle";
import DialogContent from "@mui/material/DialogContent";
import DialogActions from "@mui/material/DialogActions";
import Button from "@mui/material/Button";
import Dialog from "@mui/material/Dialog";
import {
  FormControl,
  FormGroup,
  InputLabel,
  MenuItem,
  Select,
  Stack,
  TextareaAutosize,
  TextField
} from "@mui/material";
import {
  Controller,
  SubmitHandler,
  useForm,
  UseFormSetValue
} from "react-hook-form";
import {IScheduleFormData} from "../records/forms";
import {yupResolver} from "@hookform/resolvers/yup";
import * as yup from "yup";
import {ObjectSchema} from "yup";
import {getScheduleObjectShape, useFirstRender} from "../tools/forms";
import {ScheduleDataContext, ScheduleDialogContext} from "../contexts/Schedule";
import AlertContext, {IAlert} from "../contexts/Alert";
import {createSchedule, fetchProjects} from "../services/scheduleService";
import {toFailure} from "../tools/requests";
import {IScheduleProject} from "../records/data";

export interface IScheduleCreateProps {
}

function getObjectSchema(): ObjectSchema<{}> {
  return yup.object().shape({
    ...getScheduleObjectShape(),
  })
}

function setValues(setValue: UseFormSetValue<IScheduleFormData>) {
  setValue("openpypeProject", "");
  setValue("apiKey", "");
  setValue("scriptName", "");
  setValue("shotgridProjectId", 0);
  setValue("urlPath", "");
  setValue("urlProtocol", "https");
  setValue("fieldsMapping", "");
}

function setOnSubmitHandler(setAlert: (_: IAlert) => any,
                            setCreate: (_: boolean) => any,
                            setProjects: (_: IScheduleProject[]) => any): SubmitHandler<IScheduleFormData> {
  return async (data) => {
    setAlert({severity: "info", message: "Working..."});

    const result = await createSchedule(data);

    if ("errorStatus" in result)
      return setAlert({severity: "error", message: result.errorMessage});
    setCreate(false);
    try {
      const projects = await fetchProjects();
      setProjects(projects);
    } catch (error: any) {
      return setAlert({message: toFailure(error).errorMessage, severity: "error"});
    }
    return setAlert({severity: "success", message: "New schedule was registered"});
  }
}

export default function ScheduleCreate(_: IScheduleCreateProps) {
  const {create, setCreate} = React.useContext(ScheduleDialogContext);
  const {setProjects, projects} = React.useContext(ScheduleDataContext);
  const {setAlert} = useContext(AlertContext);
  const {
    control,
    handleSubmit,
    setValue,
    formState: {errors},
  } = useForm<IScheduleFormData>({resolver: yupResolver(getObjectSchema())});
  const onSubmit = setOnSubmitHandler(setAlert, setCreate, setProjects);
  if (useFirstRender())
    setValues(setValue);

  return (
    <Dialog open={create} onClose={() => {
    }}>
      <Box component="form" noValidate autoComplete="on"
           onSubmit={handleSubmit(onSubmit)}>

        <DialogTitle>Add schedule</DialogTitle>
        <DialogContent>
          <Box sx={{'& .MuiTextField-root': {m: 1, width: '50ch'},}}
               component="div">
            <FormGroup>
              <Controller control={control} name="openpypeProject"
                          render={({field}) => (
                            <TextField {...field}
                                       label="Openpype project name"
                                       type="search"
                                       error={!!errors.openpypeProject}
                                       helperText={errors?.openpypeProject?.message || ''}/>
                          )}
              />
            </FormGroup>
            <FormGroup>
              <Stack direction="row" spacing={2} sx={{width: '52ch'}}>
                <FormControl sx={{m: 1, width: '15ch'}}>
                  <InputLabel id="protocol-label">Protocol</InputLabel>
                  <Controller control={control} name="urlProtocol"
                              render={({field}) => (
                                <Select {...field} label="Protocol"
                                        defaultValue={"https"}>
                                  <MenuItem
                                    value={"http"}>HTTP</MenuItem>
                                  <MenuItem
                                    value={"https"}>HTTPS</MenuItem>
                                </Select>
                              )}/>
                </FormControl>
                <Controller control={control} name="urlPath"
                            render={({field}) => (
                              <TextField {...field} label="Shotgrid url"
                                         type="search"
                                         error={!!errors.urlPath}
                                         helperText={errors?.urlPath?.message || ''}/>
                            )}
                />
              </Stack>
            </FormGroup>
            <FormGroup>
              <Controller control={control} name="scriptName"
                          render={({field}) => (
                            <TextField {...field}
                                       label="Shotgrid script name"
                                       type="search"
                                       error={!!errors.scriptName}
                                       helperText={errors?.scriptName?.message || ''}/>
                          )}
              />
            </FormGroup>
            <FormGroup>
              <Controller control={control} name="apiKey"
                          render={({field}) => (
                            <TextField {...field} label="Shotgrid API key"
                                       type="password"
                                       error={!!errors.apiKey}
                                       helperText={errors?.apiKey?.message || ''}/>
                          )}
              />
            </FormGroup>
            <FormGroup>
              <Controller control={control} name="shotgridProjectId"
                          render={({field}) => (
                            <TextField {...field}
                                       label="Shotgrid project ID"
                                       type="number"
                                       error={!!errors.shotgridProjectId}
                                       helperText={errors?.shotgridProjectId?.message || ''}/>
                          )}
              />
            </FormGroup>
            <FormGroup sx={{m: 1, width: '50ch', maxHeight: '70'}}>
              <Controller control={control} name="fieldsMapping"
                          render={({field}) => (
                            <TextareaAutosize
                              {...field}
                              aria-label="SG fields mapping"
                              minRows={8}
                              maxRows={16}
                              placeholder="Shotgrid fields mapping"
                              style={{
                                backgroundColor: "#111213",
                                borderColor: "#5e636e",
                                color: "#c2c9d6"
                              }}
                            />
                          )}/>
            </FormGroup>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => {
            setCreate(false);
          }} variant="outlined">Cancel</Button>
          <Button variant="contained" type="submit">Add</Button>
        </DialogActions>
      </Box>
    </Dialog>
  );
}
