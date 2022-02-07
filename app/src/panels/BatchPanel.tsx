import {
    Autocomplete,
    Box,
    Checkbox,
    FormControlLabel,
    FormGroup,
    TextareaAutosize,
    TextField
} from "@mui/material";
import {pink} from "@mui/material/colors";


const sgProjects: Array<{}> = []

export default function BatchPanel() {
    // Keep on https://mui.com/components/text-fields/#validation
    return (
        <Box component="form"
             sx={{'& .MuiTextField-root': {m: 1, width: '50ch'},}} noValidate
             autoComplete="off">
            <Autocomplete
                disablePortal
                id="op-project"
                options={sgProjects}
                renderInput={(params) => <TextField {...params}
                                                    label="Openpype Project"/>}
            />
            <TextField id="sg-url" label="Shotgrid url" type="search"/>
            <TextField id="sg-script-name" label="Shotgrid script name"
                       type="search"/>
            <TextField id="sg-api-key" label="Shotgrid API key" type="search"/>
            <TextField id="sg-project-id" label="Shotgrid project ID"
                       type="number"/>
            <FormGroup sx={{m: 1, width: '50ch'}}>
                <FormControlLabel
                    control={<Checkbox id="overwrite-project" sx={{
                        color: pink[800],
                        '&.Mui-checked': {color: pink[600],},
                    }}/>}
                    label="Overwrite existing project"/>
            </FormGroup>
            <FormGroup sx={{m: 1, width: '50ch'}}>
            <TextareaAutosize
                aria-label="SG fields mapping"
                minRows={8}
                placeholder="Shotgrid fields mapping"
                style={{backgroundColor: "#111213", borderColor: "#5e636e", color:"#c2c9d6"}}
            />
            </FormGroup>

        </Box>
    )
}
