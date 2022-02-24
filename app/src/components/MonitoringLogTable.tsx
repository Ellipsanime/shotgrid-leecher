import Box from "@mui/material/Box";
import Paper from "@mui/material/Paper";
import {
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TablePagination,
  TableRow
} from "@mui/material";
import * as React from "react";
import {useContext, useEffect, useState} from "react";
import {LogDataContext} from "../contexts/Monitoring";
import {MonitoringLogRow} from "./MonitoringLogRow";
import {toFailure} from "../tools/requests";
import {fetchTopNLogs} from "../services/monitoringService";
import AlertContext from "../contexts/Alert";

export default function MonitoringLogTable() {
  const {setAlert} = useContext(AlertContext);
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(5);
  const {logs, setLogs} = useContext(LogDataContext);
  const handleChangePage = (event: unknown, page: number) => setPage(page);
  const handleChangeRowsPerPage = (event: React.ChangeEvent<HTMLInputElement>) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };
  async function fetchAndProcessRows() {
    try {
      const logs = await fetchTopNLogs(20);
      setLogs(logs);
    } catch (error: any) {
      setAlert({message: toFailure(error).errorMessage, severity: "error"});
    }
  }
  const emptyRows = page > 0 ? Math.max(0, (1 + page) * rowsPerPage - logs.length) : 0;
  useEffect(() => {
    const _ = fetchAndProcessRows();
  }, []);
  return (
    <Box>
      <Paper sx={{maxWidth: 1000, minWidth: 350}}>
        <TableContainer component={Paper}>
          <Table aria-label="log table">
            <TableHead>
              <TableRow>
                <TableCell/>
                <TableCell>Result</TableCell>
                <TableCell align="right">Log ID</TableCell>
                <TableCell align="right">Project Name</TableCell>
                <TableCell align="right">Project ID</TableCell>
                <TableCell align="right">Duration(sec)</TableCell>
                <TableCell align="right">Log datetime</TableCell>
                <TableCell/>
              </TableRow>
            </TableHead>
            <TableBody>
              {logs
                .slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage)
                .map((row, index) => {
                  return (
                    <MonitoringLogRow key={"row-log-" + index}
                                      row={row}
                                      index={index}/>)
                })}
              {emptyRows > 0 && (
                <TableRow style={{height: 53 * emptyRows}}>
                  <TableCell colSpan={6}/>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </TableContainer>
        <TablePagination
          rowsPerPageOptions={[5, 10, 25]}
          component="div"
          count={logs.length}
          rowsPerPage={rowsPerPage}
          page={page}
          onPageChange={handleChangePage}
          onRowsPerPageChange={handleChangeRowsPerPage}
        />
      </Paper>
    </Box>
  );
}
