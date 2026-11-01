'use client';

import {
  Badge,
  Box,
  Group,
  Paper,
  Stack,
  Text,
} from '@mantine/core';

import {
  IconHeadset,
  IconUser,
} from '@tabler/icons-react';


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


export default function ChatMessage({
  message,
}) {
  const isAgent =
    message.sender_type === 'AGENT';

  return (
    <Group
      justify={
        isAgent
          ? 'flex-end'
          : 'flex-start'
      }
      align="flex-start"
    >
      <Box
        w={{
          base: '92%',
          sm: '75%',
        }}
      >
        <Group
          justify={
            isAgent
              ? 'flex-end'
              : 'flex-start'
          }
          gap={6}
          mb={5}
        >
          {isAgent ? (
            <IconHeadset
              size={16}
              color="var(--mantine-color-green-7)"
            />
          ) : (
            <IconUser size={16} />
          )}

          <Text
            size="xs"
            fw={600}
          >
            {isAgent
              ? 'Agent'
              : 'Customer'}
          </Text>

          <Badge
            size="xs"
            variant="light"
            color={
              isAgent
                ? 'green'
                : 'gray'
            }
          >
            {message.sender_type}
          </Badge>
        </Group>

        <Paper
          radius="lg"
          p="md"
          bg={
            isAgent
              ? 'green.0'
              : 'gray.0'
          }
          style={{
            border:
              isAgent
                ? '1px solid var(--mantine-color-green-2)'
                : '1px solid var(--mantine-color-gray-3)',
          }}
        >
          <Stack gap="xs">
            <Text
              style={{
                whiteSpace: 'pre-wrap',
                wordBreak: 'break-word',
              }}
            >
              {message.text}
            </Text>

            <Text
              size="xs"
              c="dimmed"
              ta={
                isAgent
                  ? 'right'
                  : 'left'
              }
            >
              {formatDate(
                message.created_at
              )}
            </Text>
          </Stack>
        </Paper>
      </Box>
    </Group>
  );
}
