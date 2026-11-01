'use client';

import {
  Badge,
  Group,
  Paper,
  Stack,
  Text,
  UnstyledButton,
} from '@mantine/core';

import {
  IconChevronRight,
  IconMessageCircle,
} from '@tabler/icons-react';

import { useRouter } from 'next/navigation';


function formatDate(value) {
  if (!value) {
    return '';
  }

  return new Intl.DateTimeFormat(
    'en-IN',
    {
      dateStyle: 'medium',
      timeStyle: 'short',
    }
  ).format(new Date(value));
}


export default function ConversationItem({
  conversation,
}) {
  const router = useRouter();

  const customerName =
    conversation.customer?.name
    || conversation.customer?.external_id
    || 'Customer';

  const messages =
    conversation.messages || [];

  const latestMessage =
    messages[messages.length - 1];

  const preview =
    latestMessage?.text
    || 'Open conversation to view messages';

  function handleOpen() {
    router.push(
      `/agent/conversations/${conversation.id}`
    );
  }

  return (
    <UnstyledButton
      w="100%"
      onClick={handleOpen}
    >
      <Paper
        withBorder
        radius="lg"
        p="md"
        style={{
          transition:
            'transform 150ms ease, border-color 150ms ease',
        }}
      >
        <Group
          justify="space-between"
          align="flex-start"
          wrap="nowrap"
        >
          <Group
            align="flex-start"
            wrap="nowrap"
          >
            <IconMessageCircle
              size={24}
              color="var(--mantine-color-green-7)"
            />

            <Stack gap={5}>
              <Group gap="xs">
                <Text fw={700}>
                  {customerName}
                </Text>

                <Badge
                  color={
                    conversation.status === 'OPEN'
                      ? 'green'
                      : 'gray'
                  }
                  variant="light"
                >
                  {conversation.status}
                </Badge>
              </Group>

              <Text
                size="sm"
                c="dimmed"
                lineClamp={1}
              >
                {preview}
              </Text>

              <Text
                size="xs"
                c="dimmed"
              >
                {formatDate(
                  conversation.last_activity_at
                )}
              </Text>
            </Stack>
          </Group>

          <IconChevronRight
            size={20}
            color="var(--mantine-color-gray-5)"
          />
        </Group>
      </Paper>
    </UnstyledButton>
  );
}