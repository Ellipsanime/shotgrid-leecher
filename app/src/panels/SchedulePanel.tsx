import * as React from 'react';
import Box from '@mui/material/Box';
import FormControl from '@mui/material/FormControl';
import {SelectChangeEvent} from '@mui/material/Select';
import ScheduleDataTable from "./ScheduleDataTable";

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
        </Box>
    )
}
