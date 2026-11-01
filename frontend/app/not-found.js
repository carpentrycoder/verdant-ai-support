'use client';

import {
  Button,
  Center,
  Stack,
  Text,
  Title,
} from '@mantine/core';

import {
  IconArrowLeft,
  IconError404,
} from '@tabler/icons-react';

import {
  useRouter,
} from 'next/navigation';


export default function NotFound() {
  const router = useRouter();

  return (
    <Center mih="100vh">
      <Stack
        align="center"
        gap="md"
      >
        <IconError404
          size={70}
          color="var(--mantine-color-gray-5)"
        />

        <Title order={2}>
          Page not found
        </Title>

        <Text c="dimmed">
          The requested page does not exist.
        </Text>

        <Button
          variant="light"
          leftSection={
            <IconArrowLeft size={17} />
          }
          onClick={() =>
            router.push('/customer')
          }
        >
          Back to Customer Support
        </Button>
      </Stack>
    </Center>
  );
}