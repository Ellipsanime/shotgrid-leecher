import {
  Box,
  Button,
  Divider,
  FormControl,
  FormGroup,
  InputLabel,
  List,
  ListItem,
  ListItemButton,
  ListItemText,
  MenuItem,
  Select,
  Snackbar,
  Stack
} from "@mui/material";
import MuiAlert from '@mui/material/Alert';
import {
  Controller,
  SubmitHandler,
  useForm,
  UseFormSetValue
} from 'react-hook-form';
import React, {useEffect, useState} from "react";
import {useFirstRender} from "../tools/forms";
import {
  activateUrl,
  currentEnvName,
  IConfig,
  loadConfig
} from "../tools/config";
import AlertContext, {IAlert} from "../contexts/Alert";
import EnvContext, {IEnv, IEnvContext} from "../contexts/Env";
import {fetchCredentials} from "../services/configService";
import Typography from "@mui/material/Typography";

export interface IConfigFormData {
  activeUrl: string;
}

function setOnSubmitHandler(setAlert: (_: IAlert) => any,
                            setConfig: (_: IConfig) => any,
                            setEnv: (_: IEnv) => any,): SubmitHandler<IConfigFormData> {
  return (data) => {
    activateUrl(data.activeUrl);
    setConfig({...loadConfig(), activeUri: data.activeUrl});
    setEnv({name: currentEnvName()});
    setAlert({message: "Configuration updated", severity: "success"});
  }
}

function setValues(setValue: UseFormSetValue<IConfigFormData>, previousData?: IConfigFormData) {
  setValue("activeUrl", loadConfig().activeUri);
}

export default function ConfigPanel() {
  const [alert, setAlert] = useState<IAlert>();
  const alertContextValue = {alert, setAlert};
  const [creds, setCreds] = useState<string[]>([]);
  const [config, setConfig] = React.useState<IConfig>(loadConfig())
  const {env, setEnv} = React.useContext<IEnvContext>(EnvContext);
  const handleClose = (event?: React.SyntheticEvent | Event, reason?: string) => {
    if (reason === 'clickaway') return;
    setAlert(undefined);
  };
  const {
    control,
    handleSubmit,
    setValue,
    formState: {errors},
  } = useForm<IConfigFormData>({});
  const onSubmit: SubmitHandler<IConfigFormData> = setOnSubmitHandler(
    setAlert, setConfig, setEnv,
  );
  if (useFirstRender()) setValues(setValue);

  useEffect(() => {
    fetchCredentials()
      .then(x => setCreds("errorMessage" in x ? [] : x));
  }, []);

  return (
    <AlertContext.Provider value={alertContextValue}>
      <Box component="div">
        <Typography variant="h6" gutterBottom component="div">
          Available shotgrid instances
        </Typography>
        <List component="div" sx={{m: 1, width: '50ch'}}>
          {creds.map((url, i) => {
            return (
              <div>
                <ListItem key={`list-item_${i}`} disablePadding>
                  <ListItemButton>
                    <ListItemText primary={url}/>
                  </ListItemButton>
                </ListItem>
                <Divider/>
              </div>
            )
          })}
        </List>
        <Typography variant="h6" gutterBottom component="div">
          Configuration
        </Typography>
        <Box component="form"
             sx={{'& .MuiTextField-root': {m: 1, width: '50ch'},}}
             noValidate
             autoComplete="on" onSubmit={handleSubmit(onSubmit)}>
          <FormGroup>
            <Stack direction="row" spacing={2} sx={{width: '52ch'}}>
              <FormControl sx={{m: 1, width: '52ch'}}>
                <InputLabel id="environment-label">Environment</InputLabel>
                <Controller control={control} name="activeUrl"
                            defaultValue={config.activeUri}
                            render={({field}) => (
                              <Select {...field} label="Environment">
                                {Object.keys(config.envUris)
                                  .map((key, i) => {
                                    return (
                                      <MenuItem
                                        key={`menu-item-${i}`}
                                        value={config.envUris[key]}>{key}</MenuItem>
                                    )
                                  })}
                              </Select>
                            )}/>
              </FormControl>
            </Stack>
          </FormGroup>

          <Box sx={{
            m: 1,
            width: '50ch',
            justifyContent: "flex-end",
            alignItems: "flex-end",
            display: "flex"
          }}>
            <Button variant="contained" type="submit"
                    sx={{width: '20ch', marginTop: 1}}>Save</Button>
          </Box>
          <Snackbar open={!!alertContextValue.alert}
                    autoHideDuration={6000}
                    anchorOrigin={{vertical: "top", horizontal: "center"}}
                    onClose={handleClose}>
            <MuiAlert onClose={handleClose} severity={alert?.severity}
                      sx={{width: '100%'}} elevation={6}
                      variant="filled">
              {alert?.message}
            </MuiAlert>
          </Snackbar>
        </Box>
      </Box>
    </AlertContext.Provider>
  )
}
