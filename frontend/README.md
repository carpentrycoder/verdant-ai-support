# Verdant AI Support - Frontend

Next.js + JavaScript + Mantine UI frontend for the Verdant AI customer-support assessment.

## Live Frontend

https://verdant-ai-support-frontend.onrender.com/

## Backend API

https://verdant-ai-support.onrender.com

Swagger:
https://verdant-ai-support.onrender.com/docs

## Features

- Customer and Agent views from one interface
- Agent authentication with JWT
- Agent workspace with Open / Closed conversation filters
- Latest conversation activity and message previews
- Full conversation history
- AI draft review and editing
- Approve AI draft and save the final Agent response
- Close / reopen conversation workflow
- Customer simulator for sending support messages
- Customer view displays customer messages and approved Agent replies only
- Loading, error, empty and not-found states
- Server-side API proxy so backend secrets are never exposed to the browser

## Tech Stack

- Next.js 16
- React 19
- JavaScript
- Mantine UI
- Tabler Icons

## Environment

Create `.env.local`:

```env
NEXT_API_URL=https://verdant-ai-support.onrender.com
```

For local backend testing, point `NEXT_API_URL` to the local backend instead.

## Local Setup

```bash
npm install
npm run dev
```

Open `http://localhost:3000`.

Production validation:

```bash
npm run lint
npm run build
```

## Application Flow

1. Customer enters an ID, name and phone number.
2. Customer sends a support message.
3. Backend creates or reuses the customer's open conversation and generates an AI draft.
4. Agent signs in and opens the conversation.
5. Agent reviews or edits the pending AI suggestion.
6. Agent approves the final response.
7. Customer refreshes the conversation and sees the approved Agent reply.

## Security

The frontend does not contain database credentials, Groq API keys, JWT secrets, or webhook secrets. Backend requests are sent through the Next.js `/api/backend/*` proxy using the server-side `NEXT_API_URL` configuration.
