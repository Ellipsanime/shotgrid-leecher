import * as React from 'react';
import {useState} from 'react';
import Box from '@mui/material/Box';
import FormControl from '@mui/material/FormControl';
import ScheduleDataTable from "../components/ScheduleDataTable";
import {Fab, Snackbar} from "@mui/material";
import AddIcon from '@mui/icons-material/Add';
import AlertContext, {IAlert} from "../contexts/Alert";
import MuiAlert from "@mui/material/Alert";

export default function SchedulePanel() {
    const [alert, setAlert] = useState<IAlert>();
    const alertContextValue = {alert, setAlert};
    const handleClose = (event?: React.SyntheticEvent | Event, reason?: string) => {
        if (reason === 'clickaway') return;
        setAlert(undefined);
    };
    return (
        <AlertContext.Provider value={alertContextValue}>
            <Box sx={{minWidth: 150}}>
                <ScheduleDataTable/>
                <FormControl fullWidth>
                </FormControl>
                <Fab sx={{position: "fixed", left: 16, bottom: 16}}
                     aria-label="Add" color="primary">
                    <AddIcon/>
                </Fab>
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
        </AlertContext.Provider>
    )
}
