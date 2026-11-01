import { NextResponse } from 'next/server';


const BACKEND_URL =
  process.env.NEXT_API_URL;


async function proxyRequest(
  request,
  context
) {
  if (!BACKEND_URL) {
    return NextResponse.json(
      {
        detail:
          'Backend URL is not configured',
      },
      {
        status: 500,
      }
    );
  }

  const { path } =
    await context.params;

  const backendPath =
    path.join('/');

  const incomingUrl =
    new URL(request.url);

  const targetUrl =
    new URL(
      `${BACKEND_URL}/${backendPath}`
    );

  incomingUrl.searchParams.forEach(
    (value, key) => {
      targetUrl.searchParams.append(
        key,
        value
      );
    }
  );

  const headers =
    new Headers();

  const contentType =
    request.headers.get(
      'content-type'
    );

  const authorization =
    request.headers.get(
      'authorization'
    );

  if (contentType) {
    headers.set(
      'Content-Type',
      contentType
    );
  }

  if (authorization) {
    headers.set(
      'Authorization',
      authorization
    );
  }

  const hasBody =
    ![
      'GET',
      'HEAD',
    ].includes(request.method);

  let body;

  if (hasBody) {
    body =
      await request.arrayBuffer();
  }

  try {
    const response =
      await fetch(
        targetUrl,
        {
          method: request.method,
          headers,
          body:
            hasBody
              ? body
              : undefined,
          cache: 'no-store',
        }
      );

    const responseBody =
      await response.arrayBuffer();

    return new NextResponse(
      responseBody,
      {
        status: response.status,
        headers: {
          'Content-Type':
            response.headers.get(
              'content-type'
            )
            || 'application/json',
        },
      }
    );
  } catch (error) {
    console.error(
      'Backend proxy failed:',
      error
    );

    return NextResponse.json(
      {
        detail:
          'Unable to connect to backend',
      },
      {
        status: 502,
      }
    );
  }
}


export async function GET(
  request,
  context
) {
  return proxyRequest(
    request,
    context
  );
}


export async function POST(
  request,
  context
) {
  return proxyRequest(
    request,
    context
  );
}


export async function PATCH(
  request,
  context
) {
  return proxyRequest(
    request,
    context
  );
}


export async function PUT(
  request,
  context
) {
  return proxyRequest(
    request,
    context
  );
}


export async function DELETE(
  request,
  context
) {
  return proxyRequest(
    request,
    context
  );
}