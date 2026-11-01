'use client';

import {
  Paper,
  SimpleGrid,
  Stack,
  Text,
  TextInput,
  Title,
} from '@mantine/core';


export default function CustomerSelector({
  externalId,
  name,
  phone,
  onExternalIdChange,
  onNameChange,
  onPhoneChange,
}) {
  return (
    <Paper
      withBorder
      radius="lg"
      p="lg"
    >
      <Stack>
        <div>
          <Title order={4}>
            Customer details
          </Title>

          <Text
            size="sm"
            c="dimmed"
          >
            Enter a customer identity to
            start or continue a conversation.
          </Text>
        </div>

        <SimpleGrid
          cols={{
            base: 1,
            sm: 3,
          }}
        >
          <TextInput
            label="Customer ID"
            placeholder="cust_demo_001"
            required
            value={externalId}
            onChange={(event) =>
              onExternalIdChange(
                event.currentTarget.value
              )
            }
          />

          <TextInput
            label="Name"
            placeholder="Demo Customer"
            value={name}
            onChange={(event) =>
              onNameChange(
                event.currentTarget.value
              )
            }
          />

          <TextInput
            label="Phone"
            placeholder="+919876543210"
            value={phone}
            onChange={(event) =>
              onPhoneChange(
                event.currentTarget.value
              )
            }
          />
        </SimpleGrid>
      </Stack>
    </Paper>
  );
}