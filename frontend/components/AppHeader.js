'use client';

import {
  Box,
  Container,
  Group,
  Text,
  ThemeIcon,
} from '@mantine/core';

import {
  IconLeaf,
} from '@tabler/icons-react';

import ViewToggle from './ViewToggle';


export default function AppHeader({
  currentView = 'customer',
}) {
  return (
    <Box
      component="header"
      bg="white"
      style={{
        borderBottom:
          '1px solid #e9ecef',
      }}
    >
      <Container
        size="lg"
        py="md"
      >
        <Group justify="space-between">
          <Group gap="sm">
            <ThemeIcon
              size="lg"
              radius="md"
              color="green"
            >
              <IconLeaf size={20} />
            </ThemeIcon>

            <div>
              <Text
                fw={700}
                size="lg"
              >
                Verdant AI Support
              </Text>

              <Text
                size="xs"
                c="dimmed"
              >
                Human-reviewed AI customer support
              </Text>
            </div>
          </Group>

          <ViewToggle
            currentView={currentView}
          />
        </Group>
      </Container>
    </Box>
  );
}