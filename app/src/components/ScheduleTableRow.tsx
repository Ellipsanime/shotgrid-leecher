import {IScheduleProject} from "../services/scheduleService";
import * as React from "react";
import {useContext} from "react";
import ScheduleDataContext from "../contexts/Schedule";
import {
  Box,
  Collapse,
  IconButton,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  Tooltip
} from "@mui/material";
import KeyboardArrowUpIcon from "@mui/icons-material/KeyboardArrowUp";
import KeyboardArrowDownIcon from "@mui/icons-material/KeyboardArrowDown";
import DeleteIcon from "@mui/icons-material/Delete";
import Typography from "@mui/material/Typography";
import {
  SentimentSatisfiedAlt,
  SentimentVeryDissatisfied
} from "@mui/icons-material";

export interface IScheduleTableRowProps {
  row: IScheduleProject
  index: number
}

export function ScheduleTableRow(props: IScheduleTableRowProps) {
  const {row, index} = props;
  const [open, setOpen] = React.useState(false);
  const {
    projectToDelete,
    setProjectToDelete,
  } = useContext(ScheduleDataContext);
  const labelId = `enhanced-table-row-${index}`;
  return (
    <React.Fragment>
      <TableRow sx={{'& > *': {borderBottom: 'unset'}}} key={labelId}>
        <TableCell>
          <IconButton
            sx={{visibility: row.latestLogs.length ? "visible" : "hidden"}}
            aria-label="expand row"
            size="small"
            onClick={() => setOpen(!open)}
          >
            {open ? <KeyboardArrowUpIcon/> :
              <KeyboardArrowDownIcon/>}
          </IconButton>
        </TableCell>
        <TableCell component="th" scope="row"
                   align="left">{row.projectName}</TableCell>
        <TableCell
          align="right">{row.projectId}</TableCell>
        <TableCell
          align="right">{row.url}</TableCell>
        <TableCell
          align="right">{row.scriptName}</TableCell>
        <TableCell
          align="right">{row.datetime}</TableCell>
        <TableCell align="right">
          <Tooltip sx={{color: 'red'}} title="Delete scheduling">
            <IconButton onClick={() => setProjectToDelete(row)}>
              <DeleteIcon/>
            </IconButton>
          </Tooltip>
        </TableCell>
      </TableRow>
      <TableRow key={`${labelId}-sub`}>
        <TableCell style={{paddingBottom: 0, paddingTop: 0}}
                   colSpan={7}>
          <Collapse in={open} timeout="auto" unmountOnExit>
            <Box sx={{
              marginTop: 1,
              marginBottom: 1,
              marginLeft: 7,
              marginRight: 7
            }}>
              <Typography variant="h6" gutterBottom
                          component="div">
                Last 5 scheduled batches
              </Typography>
              <Table size="small" aria-label="logs">
                <TableHead>
                  <TableRow>
                    <TableCell
                      align="right">Status</TableCell>
                    <TableCell>Log ID</TableCell>
                    <TableCell>Log datetime</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {row.latestLogs.map((logRow) => (
                    <TableRow key={logRow.id}>
                      <TableCell
                        align="right">{logRow.batchResult ?
                        <SentimentSatisfiedAlt
                          sx={{color: "green"}}/> :
                        <SentimentVeryDissatisfied
                          sx={{color: "orange"}}/>}</TableCell>
                      <TableCell component="th"
                                 scope="row">
                        {logRow.id}
                      </TableCell>
                      <TableCell>{logRow.datetime}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </Box>
          </Collapse>
        </TableCell>
      </TableRow>
    </React.Fragment>
  );
}
