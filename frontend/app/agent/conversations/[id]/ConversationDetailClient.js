'use client';

import {
  Alert,
  Badge,
  Button,
  Container,
  Divider,
  Group,
  Loader,
  Paper,
  Stack,
  Text,
  Title,
} from '@mantine/core';

import {
  IconAlertCircle,
  IconArrowLeft,
  IconCheck,
  IconRefresh,
  IconUser,
} from '@tabler/icons-react';

import {
  notifications,
} from '@mantine/notifications';

import {
  useCallback,
  useEffect,
  useState,
} from 'react';

import {
  useRouter,
} from 'next/navigation';

import AppHeader
  from '@/components/AppHeader';

import AiDraftEditor
  from '@/components/AiDraftEditor';

import ChatMessage
  from '@/components/ChatMessage';

import {
  approveDraft,
  getConversation,
  getPendingDrafts,
  updateConversationStatus,
} from '@/lib/api';

import {
  getAccessToken,
  removeAccessToken,
} from '@/lib/auth';


export default function ConversationDetailClient({
  conversationId,
}) {
  const router = useRouter();

  const [
    conversation,
    setConversation,
  ] = useState(null);

  const [
    pendingDraft,
    setPendingDraft,
  ] = useState(null);

  const [loading, setLoading] =
    useState(true);

  const [approving, setApproving] =
    useState(false);

  const [
    statusLoading,
    setStatusLoading,
  ] = useState(false);

  const [error, setError] =
    useState('');


  const loadConversation =
    useCallback(
      async () => {
        if (!getAccessToken()) {
          router.replace('/login');
          return;
        }

        setLoading(true);
        setError('');

        try {
          const [
            conversationData,
            draftsData,
          ] = await Promise.all([
            getConversation(
              conversationId
            ),

            getPendingDrafts({
              limit: 100,
            }),
          ]);

          setConversation(
            conversationData
          );

          const customerMessageIds =
            new Set(
              (
                conversationData.messages
                || []
              )
                .filter(
                  (message) =>
                    message.sender_type
                    === 'CUSTOMER'
                )
                .map(
                  (message) =>
                    message.id
                )
            );

          const matchingDraft =
            (
              draftsData.items || []
            ).find(
              (draft) =>
                customerMessageIds.has(
                  draft.message_id
                )
            );

          setPendingDraft(
            matchingDraft || null
          );
        } catch (requestError) {
          if (
            requestError.status === 401
          ) {
            removeAccessToken();
            router.replace('/login');
            return;
          }

          setError(
            requestError.message
            || 'Unable to load conversation'
          );
        } finally {
          setLoading(false);
        }
      },
      [
        conversationId,
        router,
      ]
    );


  useEffect(() => {
    loadConversation();
  }, [loadConversation]);


  async function handleApprove(
    draftId,
    approvedText
  ) {
    setApproving(true);

    try {
      await approveDraft(
        draftId,
        approvedText
      );

      notifications.show({
        color: 'green',
        title: 'Reply approved',
        message:
          'The approved response was added to the conversation.',
      });

      await loadConversation();
    } catch (requestError) {
      notifications.show({
        color: 'red',
        title:
          'Unable to approve reply',
        message:
          requestError.message
          || 'Approval failed.',
      });
    } finally {
      setApproving(false);
    }
  }


  async function handleStatusChange() {
    if (!conversation) {
      return;
    }

    const nextStatus =
      conversation.status === 'OPEN'
        ? 'CLOSED'
        : 'OPEN';

    setStatusLoading(true);

    try {
      await updateConversationStatus(
        conversation.id,
        nextStatus
      );

      notifications.show({
        color:
          nextStatus === 'OPEN'
            ? 'green'
            : 'gray',

        title:
          nextStatus === 'OPEN'
            ? 'Conversation reopened'
            : 'Conversation closed',

        message:
          `Conversation is now ${nextStatus.toLowerCase()}.`,
      });

      await loadConversation();
    } catch (requestError) {
      notifications.show({
        color: 'red',
        title:
          'Status update failed',
        message:
          requestError.message
          || 'Unable to update conversation.',
      });
    } finally {
      setStatusLoading(false);
    }
  }


  return (
    <>
      <AppHeader currentView="agent" />

      <Container
        size="lg"
        py="xl"
      >
        {loading ? (
          <Stack
            align="center"
            py={80}
          >
            <Loader />

            <Text c="dimmed">
              Loading conversation...
            </Text>
          </Stack>
        ) : error ? (
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
        ) : conversation ? (
          <Stack gap="xl">
            <Group
              justify="space-between"
              align="flex-start"
            >
              <Group
                align="flex-start"
              >
                <Button
                  variant="subtle"
                  color="gray"
                  px="xs"
                  onClick={() =>
                    router.push('/agent')
                  }
                >
                  <IconArrowLeft size={21} />
                </Button>

                <div>
                  <Group gap="xs">
                    <Title order={2}>
                      {
                        conversation
                          .customer
                          ?.name
                        || 'Customer'
                      }
                    </Title>

                    <Badge
                      color={
                        conversation.status
                        === 'OPEN'
                          ? 'green'
                          : 'gray'
                      }
                    >
                      {conversation.status}
                    </Badge>
                  </Group>

                  <Group
                    gap={6}
                    mt={5}
                  >
                    <IconUser size={15} />

                    <Text
                      c="dimmed"
                      size="sm"
                    >
                      {
                        conversation
                          .customer
                          ?.external_id
                        || conversation.customer_id
                      }
                    </Text>
                  </Group>
                </div>
              </Group>

              <Group>
                <Button
                  variant="light"
                  leftSection={
                    <IconRefresh size={17} />
                  }
                  onClick={
                    loadConversation
                  }
                >
                  Refresh
                </Button>

                <Button
                  color={
                    conversation.status
                    === 'OPEN'
                      ? 'gray'
                      : 'green'
                  }
                  variant="light"
                  loading={statusLoading}
                  leftSection={
                    <IconCheck size={17} />
                  }
                  onClick={
                    handleStatusChange
                  }
                >
                  {
                    conversation.status
                    === 'OPEN'
                      ? 'Close Conversation'
                      : 'Reopen Conversation'
                  }
                </Button>
              </Group>
            </Group>

            <Paper
              withBorder
              radius="lg"
              p="lg"
            >
              <Stack gap="lg">
                <Title order={3}>
                  Conversation history
                </Title>

                <Divider />

                {
                  conversation.messages?.length
                    ? (
                      <Stack gap="lg">
                        {
                          conversation
                            .messages
                            .map(
                              (message) => (
                                <ChatMessage
                                  key={
                                    message.id
                                  }
                                  message={
                                    message
                                  }
                                />
                              )
                            )
                        }
                      </Stack>
                    )
                    : (
                      <Text c="dimmed">
                        No messages available.
                      </Text>
                    )
                }
              </Stack>
            </Paper>

            {
              conversation.status === 'OPEN'
              && (
                <AiDraftEditor
                  draft={pendingDraft}
                  loading={approving}
                  onApprove={
                    handleApprove
                  }
                />
              )
            }
          </Stack>
        ) : null}
      </Container>
    </>
  );
}