import * as React from "react";
import {
  Box,
  Collapse,
  IconButton,
  TableCell,
  TableRow,
  TextareaAutosize
} from "@mui/material";
import KeyboardArrowUpIcon from "@mui/icons-material/KeyboardArrowUp";
import KeyboardArrowDownIcon from "@mui/icons-material/KeyboardArrowDown";
import Typography from "@mui/material/Typography";
import {
  SentimentSatisfiedAlt,
  SentimentVeryDissatisfied
} from "@mui/icons-material";
import {ILog} from "../records/data";

export interface IMonitoringLogRowProps {
  row: ILog
  index: number
}

export function MonitoringLogRow(props: IMonitoringLogRowProps) {
  const {row, index} = props;
  const [open, setOpen] = React.useState(false);
  const labelId = `enhanced-log-row-${index}`;
  return (
    <React.Fragment>
      <TableRow sx={{'& > *': {borderBottom: 'unset'}}} key={labelId}>
        <TableCell>
          <IconButton
            sx={{visibility: row.data ? "visible" : "hidden"}}
            aria-label="expand row"
            size="small"
            onClick={() => setOpen(!open)}
          >
            {open ? <KeyboardArrowUpIcon/> :
              <KeyboardArrowDownIcon/>}
          </IconButton>
        </TableCell>
        <TableCell component="th"
                   scope="row">{row.result.toLocaleLowerCase() === "ok" ?
          <SentimentSatisfiedAlt
            sx={{color: "green"}}/> :
          <SentimentVeryDissatisfied
            sx={{color: "orange"}}/>}</TableCell>
        <TableCell align="right">{row.id}</TableCell>
        <TableCell align="right">{row.projectName}</TableCell>
        <TableCell align="right">{row.projectId}</TableCell>
        <TableCell align="right">{row.duration}</TableCell>
        <TableCell align="right">{row.datetime}</TableCell>
      </TableRow>
      <TableRow key={`${labelId}-log-sub`}>
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
                Failure details
              </Typography>
              <Box>
                <TextareaAutosize
                  aria-label="failure details"
                  minRows={8}
                  maxRows={16}
                  readOnly={true}
                  placeholder="failure details..."
                  value={row.data}
                  style={{
                    width: "100%",
                    backgroundColor: "#111213",
                    borderColor: "#5e636e",
                    color: "#c2c9d6",
                  }}
                />
              </Box>
            </Box>
          </Collapse>
        </TableCell>
      </TableRow>
    </React.Fragment>
  );
}
