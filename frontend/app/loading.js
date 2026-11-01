import {
  Center,
  Loader,
  Stack,
  Text,
} from '@mantine/core';


export default function Loading() {
  return (
    <Center mih="100vh">
      <Stack align="center">
        <Loader size="lg" />

        <Text c="dimmed">
          Loading Verdant AI Support...
        </Text>
      </Stack>
    </Center>
  );
}