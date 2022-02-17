import * as React from "react";
import {useState} from "react";
import AlertContext, {IAlert} from "../contexts/Alert";
import Box from "@mui/material/Box";
import MonitoringLogTable from "../components/MonitoringLogTable";
import {Snackbar} from "@mui/material";
import MuiAlert from "@mui/material/Alert";
import {ILog} from "../records/data";
import {LogDataContext} from "../contexts/Monitoring";

export default function MonitoringPanel() {
  const [alert, setAlert] = useState<IAlert>();
  const [logs, setLogs] = useState<ILog[]>([]);
  const alertContextValue = {alert, setAlert};
  const logDataContextValue = {logs, setLogs};
  const handleClose = (event?: React.SyntheticEvent | Event, reason?: string) => {
    if (reason === 'clickaway') return;
    setAlert(undefined);
  };
  return (
    <AlertContext.Provider value={alertContextValue}>
      <LogDataContext.Provider value={logDataContextValue}>
        <Box>
          <MonitoringLogTable/>
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
      </LogDataContext.Provider>
    </AlertContext.Provider>
  );
}
