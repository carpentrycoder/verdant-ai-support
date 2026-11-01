'use client';

import { MantineProvider, createTheme } from '@mantine/core';
import { Notifications } from '@mantine/notifications';


const theme = createTheme({
  primaryColor: 'green',

  colors: {
    verdant: [
      '#effaf3',
      '#dff4e6',
      '#bce8ca',
      '#95dcae',
      '#75d096',
      '#60c786',
      '#53c17d',
      '#43aa6b',
      '#39975e',
      '#2c834f',
    ],
  },

  primaryShade: 7,

  defaultRadius: 'md',

  fontFamily:
    'Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif',
});


export default function Providers({ children }) {
  return (
    <MantineProvider theme={theme}>
      <Notifications position="top-right" />

      {children}
    </MantineProvider>
  );
}