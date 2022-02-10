import * as React from 'react';
import {useEffect} from 'react';
import * as dayjs from 'dayjs'
import Paper from '@mui/material/Paper';
import {
    Table,
    TableBody,
    TableCell,
    TableContainer,
    TableHead,
    TableRow
} from "@mui/material";
import {fetchProjects, IScheduleProject} from "../services/scheduleService";

interface ITableData {
    projectId: number;
    projectName: string;
    datetime: dayjs.Dayjs;
}

function createData(projectId: number, projectName: string, datetime: string): ITableData {
    return {projectId, projectName, datetime: new dayjs.Dayjs(datetime)};
}

export default function ScheduleDataTable() {
    const [projects, setProjects] = React.useState<Array<IScheduleProject>>([]);

    async function fetchAndProcessRows() {
        try {
            const projects = await fetchProjects();
            setProjects(projects);
        } catch (error: any) {
        }
    }

    useEffect(() => {fetchAndProcessRows()} , []);
    return (
        <TableContainer component={Paper}>
            <Table sx={{minWidth: 650}} aria-label="simple table">
                <TableHead>
                    <TableRow>
                        <TableCell>Project name</TableCell>
                        <TableCell align="right">Project ID</TableCell>
                        <TableCell align="right">Creation time</TableCell>
                    </TableRow>
                </TableHead>
                <TableBody>
                    {projects.map((row) => (
                        <TableRow
                            key={row.projectName}
                            sx={{'&:last-child td, &:last-child th': {border: 0}}}
                        >
                            <TableCell align="right">{row.projectId}</TableCell>
                            <TableCell align="right">{row.datetime}</TableCell>
                        </TableRow>
                    ))}
                </TableBody>
            </Table>
        </TableContainer>
    )
}
