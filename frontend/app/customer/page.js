'use client';

import {
  Alert,
  Button,
  Container,
  Group,
  Loader,
  Paper,
  Stack,
  Text,
  Textarea,
  Title,
} from '@mantine/core';

import {
  IconAlertCircle,
  IconRefresh,
  IconSend,
} from '@tabler/icons-react';

import {
  notifications,
} from '@mantine/notifications';

import {
  useCallback,
  useState,
} from 'react';

import AppHeader
  from '@/components/AppHeader';

import ChatMessage
  from '@/components/ChatMessage';

import CustomerSelector
  from '@/components/CustomerSelector';

import {
  getCustomerConversation,
  sendCustomerMessage,
} from '@/lib/api';


const SAMPLE_MESSAGES = [
  'What is your return policy?',
  'Where is my order?',
  'Can I cancel my order?',
];


export default function CustomerPage() {
  const [
    externalId,
    setExternalId,
  ] = useState(
    'cust_demo_001'
  );

  const [name, setName] =
    useState(
      'Demo Customer'
    );

  const [phone, setPhone] =
    useState(
      '+919876543210'
    );

  const [message, setMessage] =
    useState('');

  const [
    conversation,
    setConversation,
  ] = useState(null);

  const [sending, setSending] =
    useState(false);

  const [
    refreshing,
    setRefreshing,
  ] = useState(false);

  const [error, setError] =
    useState('');


  const refreshConversation =
    useCallback(
      async () => {
        const customerId =
          externalId.trim();

        if (!customerId) {
          return;
        }

        setRefreshing(true);
        setError('');

        try {
          const data =
            await getCustomerConversation(
              customerId
            );

          setConversation(data);
        } catch (requestError) {
          if (
            requestError.status
            === 404
          ) {
            setConversation(null);
            return;
          }

          setError(
            requestError.message
            || 'Unable to load conversation'
          );
        } finally {
          setRefreshing(false);
        }
      },
      [
        externalId,
      ]
    );


  async function handleSend() {
    const finalMessage =
      message.trim();

    const customerId =
      externalId.trim();

    if (!customerId) {
      setError(
        'Customer ID is required.'
      );

      return;
    }

    if (!finalMessage) {
      setError(
        'Message cannot be empty.'
      );

      return;
    }

    setSending(true);
    setError('');

    try {
      await sendCustomerMessage({
        externalId:
          customerId,

        name:
          name.trim()
          || null,

        phone:
          phone.trim()
          || null,

        text:
          finalMessage,
      });

      setMessage('');

      notifications.show({
        color: 'green',
        title: 'Message sent',
        message:
          'Your support message was received.',
      });

      await refreshConversation();
    } catch (requestError) {
      setError(
        requestError.message
        || 'Unable to send message'
      );
    } finally {
      setSending(false);
    }
  }


  return (
    <>
      <AppHeader
        currentView="customer"
      />

      <Container
        size="lg"
        py="xl"
      >
        <Stack gap="xl">
          <div>
            <Title order={2}>
              Customer Support
            </Title>

            <Text c="dimmed">
              Send a support message and
              view approved agent replies.
            </Text>
          </div>

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

          <CustomerSelector
            externalId={
              externalId
            }
            name={name}
            phone={phone}
            onExternalIdChange={
              setExternalId
            }
            onNameChange={
              setName
            }
            onPhoneChange={
              setPhone
            }
          />

          <Paper
            withBorder
            radius="lg"
            p="lg"
          >
            <Stack>
              <Group
                justify="space-between"
              >
                <div>
                  <Title order={4}>
                    Try a sample message
                  </Title>

                  <Text
                    size="sm"
                    c="dimmed"
                  >
                    Or write your own
                    support question below.
                  </Text>
                </div>
              </Group>

              <Group>
                {
                  SAMPLE_MESSAGES.map(
                    (sample) => (
                      <Button
                        key={sample}
                        size="xs"
                        variant="light"
                        color="gray"
                        onClick={() =>
                          setMessage(
                            sample
                          )
                        }
                      >
                        {sample}
                      </Button>
                    )
                  )
                }
              </Group>

              <Textarea
                label="Message"
                placeholder="How can we help?"
                minRows={4}
                value={message}
                onChange={(event) =>
                  setMessage(
                    event
                      .currentTarget
                      .value
                  )
                }
              />

              <Group
                justify="flex-end"
              >
                <Button
                  color="green"
                  loading={sending}
                  leftSection={
                    <IconSend
                      size={18}
                    />
                  }
                  onClick={
                    handleSend
                  }
                >
                  Send Message
                </Button>
              </Group>
            </Stack>
          </Paper>

          <Paper
            withBorder
            radius="lg"
            p="lg"
          >
            <Stack>
              <Group
                justify="space-between"
              >
                <div>
                  <Title order={3}>
                    Conversation
                  </Title>

                  <Text
                    size="sm"
                    c="dimmed"
                  >
                    AI suggestions are
                    never shown here.
                    Only approved agent
                    replies appear.
                  </Text>
                </div>

                <Button
                  variant="light"
                  loading={
                    refreshing
                  }
                  leftSection={
                    <IconRefresh
                      size={17}
                    />
                  }
                  onClick={
                    refreshConversation
                  }
                >
                  Refresh
                </Button>
              </Group>

              {
                refreshing
                && !conversation
                  ? (
                    <Stack
                      align="center"
                      py="xl"
                    >
                      <Loader />
                    </Stack>
                  )
                  : conversation
                    ?.messages
                    ?.length
                    ? (
                      <Stack
                        gap="lg"
                        mt="md"
                      >
                        {
                          conversation
                            .messages
                            .map(
                              (
                                chatMessage
                              ) => (
                                <ChatMessage
                                  key={
                                    chatMessage.id
                                  }
                                  message={
                                    chatMessage
                                  }
                                />
                              )
                            )
                        }
                      </Stack>
                    )
                    : (
                      <Text
                        c="dimmed"
                        py="lg"
                      >
                        No conversation yet.
                        Send your first message
                        to start.
                      </Text>
                    )
              }
            </Stack>
          </Paper>
        </Stack>
      </Container>
    </>
  );
}