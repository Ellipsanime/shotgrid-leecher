import React from 'react';
import './App.css';
import Box from '@mui/material/Box';
import Tab from '@mui/material/Tab';
import Tabs from '@mui/material/Tabs';
import {createTheme, CssBaseline, ThemeProvider} from "@mui/material";
import {TabPanel} from "./panels/TabPanel";
import BatchPanel from "./panels/BatchPanel";
import SchedulePanel from "./panels/SchedulePanel";
import MonitoringPanel from "./panels/MonitoringPanel";
import ConfigPanel from "./panels/ConfigPanel";
import EnvContext, {IEnv} from "./contexts/Env";
import {currentEnvName} from "./tools/config";

function a11yProps(index: number) {
  return {
    id: `simple-tab-${index}`,
    'aria-controls': `simple-tabpanel-${index}`,
  };
}

function App() {
  const darkTheme = createTheme({
    palette: {
      mode: 'dark',
    },
  });
  const [value, setValue] = React.useState(0);
  const [env, setEnv] = React.useState<IEnv>({name: currentEnvName()});
  const envContext = {env, setEnv};
  const handleChange = (event: React.SyntheticEvent, newValue: number) => {
    setValue(newValue);
  };
  return (
    <EnvContext.Provider value={envContext}>
      <ThemeProvider theme={darkTheme}>
        <CssBaseline/>
        <Box sx={{
          borderBottom: 1,
          borderColor: 'divider',
          bgcolor: 'background.paper'
        }}>
          <Tabs value={value} onChange={handleChange}
                aria-label="basic tabs example">
            <Tab label="Batch" {...a11yProps(0)} />
            <Tab label="Schedule" {...a11yProps(1)} />
            <Tab label="Monitoring" {...a11yProps(2)} />
            <Tab label={`Config (${envContext.env.name})`} {...a11yProps(2)} />
          </Tabs>
        </Box>
        <TabPanel value={value} index={0}>
          <BatchPanel/>
        </TabPanel>
        <TabPanel value={value} index={1}>
          <SchedulePanel/>
        </TabPanel>
        <TabPanel value={value} index={2}>
          <MonitoringPanel/>
        </TabPanel>
        <TabPanel value={value} index={3}>
          <ConfigPanel/>
        </TabPanel>
      </ThemeProvider>
    </EnvContext.Provider>
  );
}

export default App;
