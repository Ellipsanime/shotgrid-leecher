import {
  Box,
  Button,
  Checkbox,
  FormControl,
  FormControlLabel,
  FormGroup,
  InputLabel,
  MenuItem,
  Select,
  Snackbar,
  Stack,
  TextareaAutosize,
  TextField
} from "@mui/material";
import MuiAlert from '@mui/material/Alert';
import * as yup from "yup";
import {ObjectSchema} from "yup";
import {yupResolver} from '@hookform/resolvers/yup';
import {
  Controller,
  SubmitHandler,
  useForm,
  UseFormSetValue
} from 'react-hook-form';
import {pink} from "@mui/material/colors";
import React from "react";
import {AlertColor} from "@mui/material/Alert/Alert";
import {IBatchFormData} from "../records/batch";
import {batch} from "../services/batchService";
import {getScheduleObjectShape, useFirstRender} from "../tools/forms";


function getObjectSchema(): ObjectSchema<{}> {
  return yup.object().shape({
    ...getScheduleObjectShape(),
    overwrite: yup.boolean().required()
  })
}

function getPreviousData(): IBatchFormData {
  const raw = localStorage.getItem("batch.data") || "{}";
  return JSON.parse(raw) as IBatchFormData;
}

function setOnSubmitHandler(setBubble: (x: boolean) => any,
                            setSeverity: (x: AlertColor) => any,
                            setMessage: (x: string) => any): SubmitHandler<IBatchFormData> {
  return async (data) => {
    setSeverity("info");
    setMessage("Working...")
    setBubble(true);
    localStorage.setItem("batch.data", JSON.stringify(data));
    const result = await batch(data);
    if ("errorStatus" in result) {
      setMessage(`Error status: ${result.errorStatus}, message: ${result.errorMessage}`);
      setSeverity("error")
      return;
    }
    setMessage(`Batch operation launched with success`);
    setSeverity("success");
  }
}

function setValues(setValue: UseFormSetValue<IBatchFormData>, previousData?: IBatchFormData) {
  setValue("openpypeProject", previousData?.openpypeProject || "");
  setValue("apiKey", previousData?.apiKey || "");
  setValue("scriptName", previousData?.scriptName || "");
  setValue("shotgridProjectId", previousData?.shotgridProjectId || 0);
  setValue("urlPath", previousData?.urlPath || "");
  setValue("urlProtocol", previousData?.urlProtocol || "https");
  setValue("fieldsMapping", previousData?.fieldsMapping || "");
  setValue("overwrite", previousData?.overwrite || false);
}

function getLoadPreviousData(setValue: UseFormSetValue<IBatchFormData>) {
  return (_: any) => setValues(setValue, getPreviousData());
}

export default function BatchPanel() {

  const [bubble, setBubble] = React.useState(false);
  const [severity, setSeverity] = React.useState<AlertColor>("success");
  const [message, setMessage] = React.useState<string>("");
  const handleClose = (event?: React.SyntheticEvent | Event, reason?: string) => {
    if (reason === 'clickaway') return;
    setBubble(false);
  };
  const {
    control,
    handleSubmit,
    setValue,
    formState: {errors},
  } = useForm<IBatchFormData>({resolver: yupResolver(getObjectSchema())});
  const onSubmit: SubmitHandler<IBatchFormData> = setOnSubmitHandler(
    setBubble,
    setSeverity,
    setMessage,
  );
  if (useFirstRender())
    setValues(setValue);
  const onLoadPreviousClick = getLoadPreviousData(setValue);

  return (
    <Box component="form"
         sx={{'& .MuiTextField-root': {m: 1, width: '50ch'},}}
         noValidate
         autoComplete="on" onSubmit={handleSubmit(onSubmit)}>
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
      <FormGroup sx={{m: 1, width: '50ch'}}>
        <Controller control={control} name="overwrite"
                    render={({field}) => (
                      <FormControlLabel {...field}
                                        control={<Checkbox {...field}
                                                           checked={field.value}
                                                           sx={{
                                                             color: pink[800],
                                                             '&.Mui-checked': {color: pink[600],},
                                                           }}/>}
                                        label="Overwrite existing project"/>
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

      <Box sx={{
        m: 1,
        width: '50ch',
        justifyContent: "flex-end",
        alignItems: "flex-end",
        display: "flex"
      }}>
        <Button variant="outlined" type="button"
                onClick={onLoadPreviousClick}
                sx={{width: '20ch', marginTop: 1, marginRight: 2}}>Previous
          data</Button>
        <Button variant="contained" type="submit"
                sx={{width: '20ch', marginTop: 1}}>Batch</Button>
      </Box>
      <Snackbar open={bubble} autoHideDuration={6000}
                anchorOrigin={{vertical: "top", horizontal: "center"}}
                onClose={handleClose}>
        <MuiAlert onClose={handleClose} severity={severity}
                  sx={{width: '100%'}} elevation={6} variant="filled">
          {message}
        </MuiAlert>
      </Snackbar>
    </Box>
  )
}
