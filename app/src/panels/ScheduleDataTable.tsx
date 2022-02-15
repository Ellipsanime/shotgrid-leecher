import * as React from 'react';
import {useContext, useEffect, useState} from 'react';
import Paper from '@mui/material/Paper';
import {
    Box,
    Collapse,
    IconButton,
    Table,
    TableBody,
    TableCell,
    TableContainer,
    TableHead,
    TablePagination,
    TableRow,
    Tooltip
} from "@mui/material";
import {fetchProjects, IScheduleProject} from "../services/scheduleService";
import KeyboardArrowUpIcon from '@mui/icons-material/KeyboardArrowUp';
import KeyboardArrowDownIcon from '@mui/icons-material/KeyboardArrowDown';
import Typography from "@mui/material/Typography";
import DeleteIcon from '@mui/icons-material/Delete';
import {
    SentimentSatisfiedAlt,
    SentimentVeryDissatisfied
} from "@mui/icons-material";
import AlertDialog from "../dialogs/Confirm";
import ScheduleDeleteContext from "../contexts/Schedule";

type Order = 'asc' | 'desc';


interface IEnhancedTableProps {
    onRequestSort: (event: React.MouseEvent<unknown>, property: keyof IScheduleProject) => void;
    order: Order;
    orderBy: string;
    rowCount: number;
}

function EnhancedTableHead(props: IEnhancedTableProps) {
    const {
        order,
        orderBy,
        rowCount,
        onRequestSort
    } =
        props;
    const createSortHandler =
        (property: keyof IScheduleProject) => (event: React.MouseEvent<unknown>) => {
            onRequestSort(event, property);
        };

    return (
        <TableHead>
            <TableRow>
                <TableCell/>
                <TableCell>Project name</TableCell>
                <TableCell align="right">Project ID</TableCell>
                <TableCell align="right">SG url</TableCell>
                <TableCell align="right">Script name</TableCell>
                <TableCell align="right">Creation time</TableCell>
                <TableCell/>
            </TableRow>
        </TableHead>
    )
}

function EnhancedRow(props: { row: IScheduleProject, index: number }) {
    const {row, index} = props;
    const [open, setOpen] = React.useState(false);
    const {
        projectToDelete,
        setProjectToDelete
    } = useContext(ScheduleDeleteContext);
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

function reducer<T>(state: Array<any>, item: T) {
    return [...state, item]
}

export default function ScheduleDataTable() {
    const [projects, setProjects] = React.useState<Array<IScheduleProject>>([]);
    const [order, setOrder] = React.useState<Order>('asc');
    const [orderBy, setOrderBy] = React.useState<keyof IScheduleProject>('datetime');
    const [page, setPage] = React.useState(0);
    const [rowsPerPage, setRowsPerPage] = React.useState(5);
    const [projectToDelete, setProjectToDelete] = useState<IScheduleProject>();
    const projectDeleteValue = {projectToDelete, setProjectToDelete};

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

    const emptyRows = page > 0 ? Math.max(0, (1 + page) * rowsPerPage - projects.length) : 0;
    useEffect(() => {
        const _ = fetchAndProcessRows()
    }, []);
    return (
        <ScheduleDeleteContext.Provider value={projectDeleteValue}>
            <Box sx={{width: '100%'}}>
                <Paper sx={{maxWidth: 1000, minWidth: 350}}>
                    <TableContainer component={Paper}>
                        <Table aria-label="simple table">
                            <EnhancedTableHead
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
                                            <EnhancedRow key={"row-" + index}
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
                <AlertDialog message="Delete this schedule?"/>
            </Box>
        </ScheduleDeleteContext.Provider>
    )
}
