import * as React from 'react';
import {useEffect, useState} from 'react';
import Box from '@mui/material/Box';
import FormControl from '@mui/material/FormControl';
import ScheduleDataTable from "../components/ScheduleDataTable";
import {Fab, Snackbar} from "@mui/material";
import AddIcon from '@mui/icons-material/Add';
import AlertContext, {IAlert} from "../contexts/Alert";
import MuiAlert from "@mui/material/Alert";
import ScheduleCreate from "../dialogs/ScheduleCreate";
import {ScheduleDataContext, ScheduleDialogContext} from "../contexts/Schedule";
import {fetchProjects, IScheduleProject} from "../services/scheduleService";
import {toFailure} from "../tools/requests";


export default function SchedulePanel() {
  const [alert, setAlert] = useState<IAlert>();
  const [scheduleCreate, setScheduleCreate] = useState<boolean>(false);
  const alertContextValue = {alert, setAlert};
  const [projects, setProjects] = React.useState<Array<IScheduleProject>>([]);
  const [projectToDelete, setProjectToDelete] = useState<IScheduleProject>();
  const projectDataValue = {
    projectToDelete,
    setProjectToDelete,
    projects,
    setProjects
  };
  const scheduleCreateValue = {
    create: scheduleCreate,
    setCreate: setScheduleCreate
  }
  const handleClose = (event?: React.SyntheticEvent | Event, reason?: string) => {
    if (reason === 'clickaway') return;
    setAlert(undefined);
  };
  const handleAddClick = () => {
    setScheduleCreate(true);
  }

  async function fetchAndProcessRows() {
    try {
      const projects = await fetchProjects();
      setProjects(projects);
    } catch (error: any) {
      setAlert({message: toFailure(error).errorMessage, severity: "error"});
    }
  }

  useEffect(() => {
    const _ = fetchAndProcessRows();
  }, []);

  return (
    <AlertContext.Provider value={alertContextValue}>
      <ScheduleDataContext.Provider value={projectDataValue}>
        <Box sx={{minWidth: 180}}>
          <ScheduleDataTable/>
          <FormControl fullWidth>
          </FormControl>
          <ScheduleDialogContext.Provider value={scheduleCreateValue}>
            <Fab sx={{position: "fixed", left: 16, bottom: 16}}
                 aria-label="Add" color="primary" onClick={handleAddClick}>
              <AddIcon/>
            </Fab>
            <ScheduleCreate/>
          </ScheduleDialogContext.Provider>
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
      </ScheduleDataContext.Provider>
    </AlertContext.Provider>
  )
}
