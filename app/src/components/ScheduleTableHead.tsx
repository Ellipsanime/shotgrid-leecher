import {IScheduleProject} from "../services/scheduleService";
import * as React from "react";
import {TableCell, TableHead, TableRow} from "@mui/material";

export type Order = 'asc' | 'desc';

export interface IEnhancedTableProps {
  onRequestSort: (event: React.MouseEvent<unknown>, property: keyof IScheduleProject) => void;
  order: Order;
  orderBy: string;
  rowCount: number;
}

export function ScheduleTableHead(props: IEnhancedTableProps) {
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
