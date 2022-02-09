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
import {Controller, SubmitHandler, useForm} from 'react-hook-form';
import {pink} from "@mui/material/colors";
import React from "react";
import {AlertColor} from "@mui/material/Alert/Alert";
import {IBatchFormData} from "../records/batch";
import {batch} from "../services/batchService";

const urlPathRegexp = /(www\.)?[-a-zA-Z0-9@:%._+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_+.~#?&//=]*)/gi

const batchSchema: ObjectSchema<{}> = yup.object().shape({
    openpypeProject: yup.string().min(3).required(),
    urlProtocol: yup.string().default("http").required(),
    urlPath: yup.string().matches(urlPathRegexp, "Should be a valid url path").required(),
    scriptName: yup.string().min(3).required(),
    apiKey: yup.string().min(3).required(),
    shotgridProjectId: yup.number().min(1).required(),
    fieldsMapping: yup.string().nullable(),
    overwrite: yup.boolean().default(false).required()
})

export default function BatchPanel() {
    const [bubble, setBubble] = React.useState(false);
    const [severity, setSeverity] = React.useState<AlertColor>("success");
    const handleClose = (event?: React.SyntheticEvent | Event, reason?: string) => {
        if (reason === 'clickaway') return;
        setBubble(false);
    };
    const onSubmit: SubmitHandler<IBatchFormData> = async (data) => {
        console.log('remote url: ', process.env.REACT_APP_API_URI);
        console.log('data submitted: ', data);
        const result = await batch(data);
        setBubble(true);
    }
    const {
        control,
        handleSubmit,
        formState: {errors},
    } = useForm<IBatchFormData>({resolver: yupResolver(batchSchema)})
    return (
        <Box component="form"
             sx={{'& .MuiTextField-root': {m: 1, width: '50ch'},}}
             noValidate
             autoComplete="off" onSubmit={handleSubmit(onSubmit)}>
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
                                                defaultValue={"http"}>
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
                                           type="search"
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
                                <FormControlLabel
                                    control={<Checkbox {...field} sx={{
                                        color: pink[800],
                                        '&.Mui-checked': {color: pink[600],},
                                    }}/>}
                                    label="Overwrite existing project"/>
                            )}
                />
            </FormGroup>
            <FormGroup sx={{m: 1, width: '50ch'}}>
                <Controller control={control} name="fieldsMapping"
                            render={({field}) => (
                                <TextareaAutosize
                                    {...field}
                                    aria-label="SG fields mapping"
                                    minRows={8}
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
                <Button variant="contained" type="submit"
                        sx={{width: '20ch', marginTop: 1}}>Batch</Button>
            </Box>
            <Snackbar open={bubble} autoHideDuration={6000}
                      anchorOrigin={{vertical: "top", horizontal: "center"}}
                      onClose={handleClose}>
                <MuiAlert onClose={handleClose} severity={severity}
                          sx={{width: '100%'}} elevation={6} variant="filled">
                    This is a success message!
                </MuiAlert>
            </Snackbar>
        </Box>
    )
}
