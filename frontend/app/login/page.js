'use client';

import { useState } from 'react';

import {
  Alert,
  Button,
  Center,
  Container,
  Paper,
  PasswordInput,
  Stack,
  Text,
  TextInput,
  Title,
} from '@mantine/core';

import {
  IconAlertCircle,
  IconLeaf,
  IconLogin,
} from '@tabler/icons-react';

import { useRouter } from 'next/navigation';

import AppHeader from '@/components/AppHeader';

import {
  loginAgent,
} from '@/lib/api';

import {
  setAccessToken,
} from '@/lib/auth';


export default function LoginPage() {
  const router = useRouter();

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');


  async function handleSubmit(event) {
    event.preventDefault();

    setError('');
    setLoading(true);

    try {
      const response = await loginAgent(
        email,
        password
      );

      setAccessToken(
        response.access_token
      );

      router.push('/agent');
    } catch (requestError) {
      setError(
        requestError.message
        || 'Unable to sign in'
      );
    } finally {
      setLoading(false);
    }
  }


  return (
    <>
      <AppHeader currentView="agent" />

      <Container
        size="xs"
        py={80}
      >
        <Center>
          <Paper
            withBorder
            shadow="sm"
            radius="lg"
            p="xl"
            w="100%"
          >
            <Stack gap="lg">
              <Center>
                <IconLeaf
                  size={42}
                  color="var(--mantine-color-green-7)"
                />
              </Center>

              <div>
                <Title
                  order={2}
                  ta="center"
                >
                  Agent sign in
                </Title>

                <Text
                  c="dimmed"
                  ta="center"
                  mt="xs"
                >
                  Review customer conversations
                  and approve AI-generated replies.
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

              <form
                onSubmit={handleSubmit}
              >
                <Stack>
                  <TextInput
                    label="Email"
                    placeholder="agent@example.com"
                    type="email"
                    required
                    value={email}
                    onChange={(event) =>
                      setEmail(
                        event.currentTarget.value
                      )
                    }
                  />

                  <PasswordInput
                    label="Password"
                    placeholder="Your password"
                    required
                    value={password}
                    onChange={(event) =>
                      setPassword(
                        event.currentTarget.value
                      )
                    }
                  />

                  <Button
                    type="submit"
                    loading={loading}
                    leftSection={
                      <IconLogin
                        size={18}
                      />
                    }
                    fullWidth
                  >
                    Sign in
                  </Button>
                </Stack>
              </form>
            </Stack>
          </Paper>
        </Center>
      </Container>
    </>
  );
}