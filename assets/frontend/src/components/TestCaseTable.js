import * as React from 'react';
import { DataGrid } from '@mui/x-data-grid';
import { Box } from '@mui/material';

export default function TestCaseTable({ testCases }) {
  if (!testCases || testCases.length === 0)
    return <Box sx={{ mt: 3 }}>No test cases generated yet.</Box>;

  const columns = [
    { field: 'id', headerName: 'ID', width: 120 },
    { field: 'preconditions', headerName: 'Preconditions', flex: 1, minWidth: 150 },
    { field: 'steps', headerName: 'Steps', flex: 2, minWidth: 250 },
    { field: 'expectedResults', headerName: 'Expected Results', flex: 2, minWidth: 250 },
  ];

  const rows = testCases.map((tc, idx) => ({ ...tc, id: tc.id || idx }));

  return (
    <Box sx={{ height: 400, width: '100%', mt: 3 }}>
      <DataGrid
        rows={rows}
        columns={columns}
        pageSize={5}
        rowsPerPageOptions={[5]}
        disableSelectionOnClick
      />
    </Box>
  );
}
