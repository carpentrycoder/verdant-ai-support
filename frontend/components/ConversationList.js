'use client';

import {
  Alert,
  Loader,
  Stack,
  Text,
} from '@mantine/core';

import {
  IconAlertCircle,
  IconInbox,
} from '@tabler/icons-react';

import ConversationItem
  from './ConversationItem';


export default function ConversationList({
  conversations = [],
  loading = false,
  error = '',
}) {
  if (loading) {
    return (
      <Stack
        align="center"
        py={60}
      >
        <Loader />

        <Text c="dimmed">
          Loading conversations...
        </Text>
      </Stack>
    );
  }

  if (error) {
    return (
      <Alert
        color="red"
        icon={
          <IconAlertCircle size={18} />
        }
      >
        {error}
      </Alert>
    );
  }

  if (!conversations.length) {
    return (
      <Stack
        align="center"
        py={60}
      >
        <IconInbox
          size={44}
          color="var(--mantine-color-gray-5)"
        />

        <Text fw={600}>
          No conversations found
        </Text>

        <Text
          c="dimmed"
          size="sm"
          ta="center"
        >
          New customer messages will appear here.
        </Text>
      </Stack>
    );
  }

  return (
    <Stack>
      {conversations.map(
        (conversation) => (
          <ConversationItem
            key={conversation.id}
            conversation={conversation}
          />
        )
      )}
    </Stack>
  );
}