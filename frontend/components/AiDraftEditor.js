'use client';

import {
  Alert,
  Badge,
  Button,
  Group,
  Paper,
  Stack,
  Text,
  Textarea,
  Title,
} from '@mantine/core';

import {
  IconAlertCircle,
  IconCheck,
  IconRobot,
} from '@tabler/icons-react';

import {
  useEffect,
  useState,
} from 'react';


export default function AiDraftEditor({
  draft,
  onApprove,
  loading = false,
}) {
  const [text, setText] =
    useState('');

  const [error, setError] =
    useState('');


  useEffect(() => {
    setText(
      draft?.draft_text || ''
    );

    setError('');
  }, [draft]);


  if (!draft) {
    return (
      <Paper
        withBorder
        radius="lg"
        p="lg"
      >
        <Group>
          <IconRobot
            size={26}
            color="var(--mantine-color-gray-5)"
          />

          <div>
            <Text fw={600}>
              No pending AI draft
            </Text>

            <Text
              size="sm"
              c="dimmed"
            >
              No AI-generated response is
              waiting for review.
            </Text>
          </div>
        </Group>
      </Paper>
    );
  }


  async function handleApprove() {
    const approvedText =
      text.trim();

    if (!approvedText) {
      setError(
        'Approved response cannot be empty.'
      );

      return;
    }

    setError('');

    await onApprove(
      draft.id,
      approvedText
    );
  }


  return (
    <Paper
      withBorder
      radius="lg"
      p="lg"
      bg="blue.0"
      style={{
        borderColor:
          'var(--mantine-color-blue-2)',
      }}
    >
      <Stack>
        <Group
          justify="space-between"
        >
          <Group gap="xs">
            <IconRobot
              size={26}
              color="var(--mantine-color-blue-7)"
            />

            <Title order={4}>
              AI Suggested Reply
            </Title>
          </Group>

          <Badge
            color="blue"
            variant="light"
          >
            {draft.status}
          </Badge>
        </Group>

        <Text
          c="dimmed"
          size="sm"
        >
          Review and edit the AI response
          before approving it.
        </Text>

        {error && (
          <Alert
            color="red"
            icon={
              <IconAlertCircle
                size={18}
              />
            }
          >
            {error}
          </Alert>
        )}

        <Textarea
          label="Final response"
          description="This exact response will be added to the conversation."
          minRows={6}
          autosize
          maxRows={14}
          value={text}
          onChange={(event) =>
            setText(
              event.currentTarget.value
            )
          }
        />

        <Group justify="flex-end">
          <Button
            color="green"
            loading={loading}
            leftSection={
              <IconCheck size={18} />
            }
            onClick={handleApprove}
          >
            Approve & Save Reply
          </Button>
        </Group>
      </Stack>
    </Paper>
  );
}