import '@mantine/core/styles.css';
import '@mantine/notifications/styles.css';

import './globals.css';

import Providers from './providers';


export const metadata = {
  title: 'Verdant AI Support',
  description: 'AI-assisted customer support workspace',
};


export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>
        <Providers>
          {children}
        </Providers>
      </body>
    </html>
  );
}