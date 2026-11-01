'use client';

import {
  SegmentedControl,
} from '@mantine/core';

import {
  IconHeadset,
  IconUser,
} from '@tabler/icons-react';

import {
  useRouter,
} from 'next/navigation';


export default function ViewToggle({
  currentView = 'customer',
}) {
  const router = useRouter();


  function handleChange(nextValue) {
    if (nextValue === 'customer') {
      router.push('/customer');
      return;
    }

    router.push('/agent');
  }


  return (
    <SegmentedControl
      value={currentView}
      onChange={handleChange}
      data={[
        {
          value: 'customer',
          label: (
            <span
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: 6,
              }}
            >
              <IconUser size={16} />
              Customer
            </span>
          ),
        },
        {
          value: 'agent',
          label: (
            <span
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: 6,
              }}
            >
              <IconHeadset size={16} />
              Agent
            </span>
          ),
        },
      ]}
    />
  );
}