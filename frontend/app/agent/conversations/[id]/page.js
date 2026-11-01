import { Suspense } from 'react';

import ConversationDetailClient
  from './ConversationDetailClient';


function ConversationLoading() {
  return (
    <div
      style={{
        minHeight: '60vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        color: '#868e96',
        fontFamily: 'sans-serif',
      }}
    >
      Loading conversation...
    </div>
  );
}


async function ConversationPageContent({
  params,
}) {
  const { id } = await params;

  return (
    <ConversationDetailClient
      conversationId={id}
    />
  );
}


export default function ConversationPage({
  params,
}) {
  return (
    <Suspense
      fallback={
        <ConversationLoading />
      }
    >
      <ConversationPageContent
        params={params}
      />
    </Suspense>
  );
}