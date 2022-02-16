import * as React from 'react';
import {useContext} from 'react';
import Button from '@mui/material/Button';
import Dialog from '@mui/material/Dialog';
import DialogActions from '@mui/material/DialogActions';
import DialogContent from '@mui/material/DialogContent';
import DialogContentText from '@mui/material/DialogContentText';
import DialogTitle from '@mui/material/DialogTitle';
import ScheduleDataContext from "../contexts/Schedule";
import {deleteSchedule} from "../services/scheduleService";
import AlertContext from "../contexts/Alert";

export default function ScheduleConfirm(props: { message: string }) {
  const {
    projectToDelete,
    setProjectToDelete,
    projects,
    setProjects
  } = useContext(ScheduleDataContext);
  const {alert, setAlert} = useContext(AlertContext);
  const [message, _] = React.useState(props.message);
  const [open, setOpen] = React.useState(!!projectToDelete);

  React.useEffect(() => {
    setOpen(!!projectToDelete);
  }, [!!projectToDelete]);

  function handleClose() {
    setProjectToDelete(undefined);
  }

  async function handleConfirm() {
    if (!projectToDelete) {
      setProjectToDelete(undefined);
      return;
    }
    setAlert({severity: "info", message: "Working..."});
    const projectName = projectToDelete.projectName;
    const result = await deleteSchedule(projectToDelete);
    if ("errorStatus" in result)
      setAlert({severity: "error", message: result.errorMessage});
    if ("status" in result) {
      setAlert({
        severity: "success",
        message: `Project ${projectToDelete.projectName} was deleted`
      });
      setProjects(projects.filter(x => x.projectName != projectName));
    }
    setProjectToDelete(undefined);
  }

  return (
    <div>
      <Dialog
        open={open}
        onClose={handleClose}
        aria-labelledby="alert-dialog-title"
        aria-describedby="alert-dialog-description"
      >
        <DialogTitle id="alert-dialog-title">
          {"Attention"}
        </DialogTitle>
        <DialogContent>
          <DialogContentText id="alert-dialog-description">
            {message}
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleClose}>Cancel</Button>
          <Button onClick={handleConfirm} autoFocus>
            Confirm
          </Button>
        </DialogActions>
      </Dialog>
    </div>
  );
}
