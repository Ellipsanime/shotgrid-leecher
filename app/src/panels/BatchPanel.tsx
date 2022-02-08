import {
    Autocomplete,
    Box,
    Button,
    Checkbox,
    FormControlLabel,
    FormGroup,
    TextareaAutosize,
    TextField
} from "@mui/material";
import * as yup from "yup";
import {yupResolver} from '@hookform/resolvers/yup';
import {Controller, SubmitHandler, useForm} from 'react-hook-form';
import {pink} from "@mui/material/colors";

const sgProjects: Array<{}> = []

interface IBatchFormData {
    openpypeProject: string
    url: string
    scriptName: string
    apiKey: string
    shotgridProjectId: number
    overwrite: boolean
    fieldsMapping?: string
}

const batchSchema = yup.object().shape({
    openpypeProject: yup.string().required(),
    url: yup.string().url().required(),
    scriptName: yup.string().min(3).required(),
    apiKey: yup.string().min(3).required(),
    shotgridProjectId: yup.number().min(1).required(),
})

const onSubmit: SubmitHandler<IBatchFormData> = (data) => console.log('data submitted: ', data);

export default function BatchPanel() {
    // const {project, url, scriptName, apiKey, overwrite, mappings} = this.state
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
            {/*https://stackoverflow.com/questions/61655199/proper-way-to-use-react-hook-form-controller-with-material-ui-autocomplete*/}
            <Controller control={control} name="openpypeProject"
                render={({field}) => (
                    <Autocomplete
                        {...field}
                        disablePortal
                        options={sgProjects}
                        renderInput={(params) => <TextField {...params}
                                                            label="Openpype Project"
                                                            error={!!errors.openpypeProject}
                                                            helperText={errors?.openpypeProject?.message || ''}/>}
                    />
                )}/>
            <FormGroup>
                <Controller control={control} name="url" render={({field}) => (
                    <TextField {...field} label="Shotgrid url" type="search"
                               error={!!errors.url}
                               helperText={errors?.url?.message || ''}/>
                )}
                />
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
                <TextareaAutosize
                    aria-label="SG fields mapping"
                    minRows={8}
                    placeholder="Shotgrid fields mapping"
                    style={{
                        backgroundColor: "#111213",
                        borderColor: "#5e636e",
                        color: "#c2c9d6"
                    }}
                />
            </FormGroup>

            <Box sx={{
                m: 1,
                width: '50ch',
                justifyContent: "flex-end",
                alignItems: "flex-end",
                display: "flex"
            }}>
                <Button variant="contained" type="submit"
                        sx={{width: '20ch'}}>Batch</Button>
            </Box>
        </Box>
    )
}
