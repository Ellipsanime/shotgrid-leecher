import * as React from 'react';
import Box from '@mui/material/Box';
import FormControl from '@mui/material/FormControl';
import {SelectChangeEvent} from '@mui/material/Select';
import ScheduleDataTable from "./ScheduleDataTable";
import {Fab} from "@mui/material";
import AddIcon from '@mui/icons-material/Add';

export default function SchedulePanel() {
    const [age, setAge] = React.useState('');

    const handleChange = (event: SelectChangeEvent) => {
        setAge(event.target.value as string);
    };
    return (
        <Box sx={{minWidth: 120}}>
            <ScheduleDataTable />
            <FormControl fullWidth>
            </FormControl>
            <Fab sx={{position: "fixed", left: 16, bottom: 16}} aria-label="Add" color="primary">
                <AddIcon />
            </Fab>
        </Box>
    )
}
