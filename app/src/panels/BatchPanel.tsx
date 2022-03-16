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
import React, {useEffect, useState} from "react";
import {AlertColor} from "@mui/material/Alert/Alert";
import {IBatchFormData} from "../records/forms";
import {batch} from "../services/batchService";
import {getScheduleObjectShape, useFirstRender} from "../tools/forms";
import {fetchCredentials} from "../services/configService";


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
  setValue("shotgridUrl", previousData?.shotgridUrl || "");
  setValue("shotgridProjectId", previousData?.shotgridProjectId || 0);
  setValue("fieldsMapping", previousData?.fieldsMapping || "");
  setValue("overwrite", previousData?.overwrite || false);
}

function getLoadPreviousData(setValue: UseFormSetValue<IBatchFormData>) {
  return (_: any) => setValues(setValue, getPreviousData());
}

export default function BatchPanel() {
  const [creds, setCreds] = useState<string[]>([]);
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

  useEffect(() => {
    fetchCredentials()
      .then(x => setCreds("errorMessage" in x ? [] : x));
  }, []);

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
          <FormControl sx={{m: 1, width: '50ch'}}>
            <InputLabel id="protocol-label">Shotgrid instance URL</InputLabel>
            <Controller control={control} name="shotgridUrl"
                        render={({field}) => (
                          <Select {...field} label="Shotgrid instance URL" error={!!errors.shotgridUrl} >
                            {creds.map((x, i) => {
                              return (
                                <MenuItem key={`url-key-${i}`} value={x}>{ new URL(x).host }</MenuItem>
                              )
                            })}
                          </Select>
                        )}/>
          </FormControl>
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
