'use client';

import {
  Alert,
  Button,
  Center,
  Stack,
  Text,
  Title,
} from '@mantine/core';

import {
  IconAlertTriangle,
  IconRefresh,
} from '@tabler/icons-react';


export default function ErrorPage({
  error,
  reset,
}) {
  return (
    <Center mih="100vh">
      <Stack
        maw={500}
        w="100%"
        p="xl"
      >
        <IconAlertTriangle
          size={52}
          color="var(--mantine-color-red-6)"
        />

        <Title order={2}>
          Something went wrong
        </Title>

        <Text c="dimmed">
          Verdant AI Support could not
          complete this request.
        </Text>

        {error?.message && (
          <Alert color="red">
            {error.message}
          </Alert>
        )}

        <Button
          leftSection={
            <IconRefresh size={17} />
          }
          onClick={reset}
        >
          Try Again
        </Button>
      </Stack>
    </Center>
  );
}