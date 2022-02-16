import * as React from 'react';
import {useEffect, useState} from 'react';
import Paper from '@mui/material/Paper';
import {
  Box,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TablePagination,
  TableRow
} from "@mui/material";
import {fetchProjects, IScheduleProject} from "../services/scheduleService";
import ScheduleConfirm from "../dialogs/ScheduleConfirm";
import ScheduleDataContext from "../contexts/Schedule";
import {ScheduleTableRow} from "./ScheduleTableRow";
import {Order, ScheduleTableHead} from "./ScheduleTableHead";


function stableSort<T>(array: readonly T[], comparator: (a: T, b: T) => number): Array<T> {
  const stabilizedThis = array.map((el, index) => [el, index] as [T, number]);
  stabilizedThis.sort((a, b) => {
    const order = comparator(a[0], b[0]);
    if (order !== 0) {
      return order;
    }
    return a[1] - b[1];
  });
  return stabilizedThis.map((el) => el[0]);
}

function descendingComparator<T>(a: T, b: T, orderBy: keyof T) {
  if (b[orderBy] < a[orderBy]) {
    return -1;
  }
  if (b[orderBy] > a[orderBy]) {
    return 1;
  }
  return 0;
}

function getComparator<Key extends keyof any>(
  order: Order,
  orderBy: Key,
): (
  a: { [key in Key]: number | string },
  b: { [key in Key]: number | string },
) => number {
  return order === 'desc'
    ? (a, b) => descendingComparator(a, b, orderBy)
    : (a, b) => -descendingComparator(a, b, orderBy);
}

export default function ScheduleDataTable() {
  const [projects, setProjects] = React.useState<Array<IScheduleProject>>([]);
  const [order, setOrder] = React.useState<Order>('asc');
  const [orderBy, setOrderBy] = React.useState<keyof IScheduleProject>('datetime');
  const [page, setPage] = React.useState(0);
  const [rowsPerPage, setRowsPerPage] = React.useState(5);
  const [projectToDelete, setProjectToDelete] = useState<IScheduleProject>();
  const projectDeleteValue = {projectToDelete, setProjectToDelete, projects, setProjects};

  const handleRequestSort = (
    event: React.MouseEvent<unknown>,
    property: keyof IScheduleProject,
  ) => {
    const isAsc = orderBy === property && order === 'asc';
    setOrder(isAsc ? 'desc' : 'asc');
    setOrderBy(property);
  };

  const handleChangePage = (event: unknown, newPage: number) => {
    setPage(newPage);
  };
  const handleChangeRowsPerPage = (event: React.ChangeEvent<HTMLInputElement>) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  async function fetchAndProcessRows() {
    try {
      const projects = await fetchProjects();
      setProjects(projects);
    } catch (error: any) {
      throw error;
    }
  }

  async function handleRequestRemove(event: React.MouseEvent<unknown>, row: IScheduleProject) {
    await fetchAndProcessRows();
  }

  const emptyRows = page > 0 ? Math.max(0, (1 + page) * rowsPerPage - projects.length) : 0;

  useEffect(() => {
    const _ = fetchAndProcessRows()
  }, []);
  return (
    <ScheduleDataContext.Provider value={projectDeleteValue}>
      <Box sx={{width: '100%'}}>
        <Paper sx={{maxWidth: 1000, minWidth: 350}}>
          <TableContainer component={Paper}>
            <Table aria-label="simple table">
              <ScheduleTableHead
                order={order}
                orderBy={orderBy}
                onRequestSort={handleRequestSort}
                rowCount={projects.length}
              />
              <TableBody>
                {/*{stableSort(projects, getComparator(order, orderBy))*/}
                {projects
                  .slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage)
                  .map((row, index) => {
                    // const isItemSelected = isSelected(row.name);
                    return (
                      <ScheduleTableRow key={"row-" + index}
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
            count={projects.length}
            rowsPerPage={rowsPerPage}
            page={page}
            onPageChange={handleChangePage}
            onRowsPerPageChange={handleChangeRowsPerPage}
          />
        </Paper>
        <ScheduleConfirm message="Delete this schedule?"/>
      </Box>
    </ScheduleDataContext.Provider>
  )
}
