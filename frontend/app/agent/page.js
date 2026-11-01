'use client';

import {
  Alert,
  Badge,
  Button,
  Container,
  Group,
  Paper,
  SegmentedControl,
  SimpleGrid,
  Stack,
  Text,
  Title,
} from '@mantine/core';

import {
  IconAlertCircle,
  IconLogout,
  IconMessages,
  IconRefresh,
  IconRobot,
} from '@tabler/icons-react';

import {
  useCallback,
  useEffect,
  useState,
} from 'react';

import { useRouter } from 'next/navigation';

import { notifications }
  from '@mantine/notifications';

import AppHeader
  from '@/components/AppHeader';

import ConversationList
  from '@/components/ConversationList';

import {
  getConversation,
  getConversations,
  getCurrentAgent,
  getPendingDrafts,
} from '@/lib/api';

import {
  getAccessToken,
  removeAccessToken,
} from '@/lib/auth';


export default function AgentPage() {
  const router = useRouter();

  const [agent, setAgent] =
    useState(null);

  const [
    conversations,
    setConversations,
  ] = useState([]);

  const [
    pendingDraftCount,
    setPendingDraftCount,
  ] = useState(0);

  const [
    statusFilter,
    setStatusFilter,
  ] = useState('ALL');

  const [loading, setLoading] =
    useState(true);

  const [error, setError] =
    useState('');


  const loadDashboard = useCallback(
    async () => {
      const token =
        getAccessToken();

      if (!token) {
        router.replace('/login');
        return;
      }

      setLoading(true);
      setError('');

      try {
        const [
          currentAgent,
          conversationResult,
          draftResult,
        ] = await Promise.all([
          getCurrentAgent(),

          getConversations({
            status:
              statusFilter === 'ALL'
                ? undefined
                : statusFilter,
            limit: 50,
          }),

          getPendingDrafts({
            limit: 100,
          }),
        ]);

        const detailedConversations =
          await Promise.all(
            conversationResult.items.map(
              async (conversation) => {
                try {
                  return await getConversation(
                    conversation.id
                  );
                } catch {
                  return conversation;
                }
              }
            )
          );

        detailedConversations.sort(
          (first, second) =>
            new Date(
              second.last_activity_at
            )
            - new Date(
              first.last_activity_at
            )
        );

        setAgent(currentAgent);

        setConversations(
          detailedConversations
        );

        setPendingDraftCount(
          draftResult.total
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
          || 'Unable to load agent dashboard'
        );
      } finally {
        setLoading(false);
      }
    },
    [
      router,
      statusFilter,
    ]
  );


  useEffect(() => {
    loadDashboard();
  }, [loadDashboard]);


  function handleLogout() {
    removeAccessToken();
    router.push('/login');
  }


  async function handleRefresh() {
    await loadDashboard();

    notifications.show({
      color: 'green',
      title: 'Dashboard refreshed',
      message:
        'Latest conversations and drafts loaded.',
    });
  }


  return (
    <>
      <AppHeader currentView="agent" />

      <Container
        size="lg"
        py="xl"
      >
        <Stack gap="xl">
          <Group
            justify="space-between"
            align="flex-start"
          >
            <div>
              <Group gap="xs">
                <Title order={2}>
                  Agent workspace
                </Title>

                {agent && (
                  <Badge
                    color="green"
                    variant="light"
                  >
                    Online
                  </Badge>
                )}
              </Group>

              <Text
                c="dimmed"
                mt={4}
              >
                {agent
                  ? `Signed in as ${agent.name}`
                  : 'Loading agent details...'}
              </Text>
            </div>

            <Group>
              <Button
                variant="light"
                leftSection={
                  <IconRefresh
                    size={17}
                  />
                }
                loading={loading}
                onClick={handleRefresh}
              >
                Refresh
              </Button>

              <Button
                variant="light"
                color="red"
                leftSection={
                  <IconLogout
                    size={17}
                  />
                }
                onClick={handleLogout}
              >
                Logout
              </Button>
            </Group>
          </Group>

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

          <SimpleGrid
            cols={{
              base: 1,
              sm: 2,
            }}
          >
            <Paper
              withBorder
              radius="lg"
              p="lg"
            >
              <Group>
                <IconMessages
                  size={30}
                  color="var(--mantine-color-green-7)"
                />

                <div>
                  <Text
                    size="sm"
                    c="dimmed"
                  >
                    Conversations
                  </Text>

                  <Text
                    size="xl"
                    fw={700}
                  >
                    {conversations.length}
                  </Text>
                </div>
              </Group>
            </Paper>

            <Paper
              withBorder
              radius="lg"
              p="lg"
            >
              <Group>
                <IconRobot
                  size={30}
                  color="var(--mantine-color-blue-6)"
                />

                <div>
                  <Text
                    size="sm"
                    c="dimmed"
                  >
                    Pending AI drafts
                  </Text>

                  <Text
                    size="xl"
                    fw={700}
                  >
                    {pendingDraftCount}
                  </Text>
                </div>
              </Group>
            </Paper>
          </SimpleGrid>

          <Paper
            withBorder
            radius="lg"
            p="lg"
          >
            <Stack>
              <Group
                justify="space-between"
                align="flex-start"
              >
                <div>
                  <Title order={3}>
                    Conversations
                  </Title>

                  <Text
                    c="dimmed"
                    size="sm"
                  >
                    Newest activity appears first.
                  </Text>
                </div>

                <SegmentedControl
                  value={statusFilter}
                  onChange={setStatusFilter}
                  data={[
                    {
                      value: 'ALL',
                      label: 'All',
                    },
                    {
                      value: 'OPEN',
                      label: 'Open',
                    },
                    {
                      value: 'CLOSED',
                      label: 'Closed',
                    },
                  ]}
                />
              </Group>

              <ConversationList
                conversations={conversations}
                loading={loading}
                error=""
              />
            </Stack>
          </Paper>
        </Stack>
      </Container>
    </>
  );
}