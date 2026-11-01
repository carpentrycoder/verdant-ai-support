import {
  getAccessToken,
  removeAccessToken,
} from './auth';


const API_URL = '/api/backend';


export class ApiError extends Error {
  constructor(
    message,
    status,
    data = null
  ) {
    super(message);

    this.name = 'ApiError';
    this.status = status;
    this.data = data;
  }
}


export async function apiFetch(
  path,
  options = {}
) {
  const {
    auth = false,
    headers = {},
    ...fetchOptions
  } = options;

  const requestHeaders =
    new Headers(headers);

  if (
    fetchOptions.body
    && !requestHeaders.has(
      'Content-Type'
    )
  ) {
    requestHeaders.set(
      'Content-Type',
      'application/json'
    );
  }

  if (auth) {
    const token =
      getAccessToken();

    if (!token) {
      throw new ApiError(
        'Authentication required',
        401
      );
    }

    requestHeaders.set(
      'Authorization',
      `Bearer ${token}`
    );
  }

  let response;

  try {
    response = await fetch(
      `${API_URL}${path}`,
      {
        ...fetchOptions,
        headers: requestHeaders,
        cache: 'no-store',
      }
    );
  } catch {
    throw new ApiError(
      'Unable to connect to backend',
      0
    );
  }

  const contentType =
    response.headers.get(
      'content-type'
    ) || '';

  let data = null;

  if (
    contentType.includes(
      'application/json'
    )
  ) {
    data = await response.json();
  } else {
    data = await response.text();
  }

  if (!response.ok) {
    if (
      auth
      && response.status === 401
    ) {
      removeAccessToken();
    }

    let message =
      'Request failed';

    if (
      data
      && typeof data === 'object'
    ) {
      if (
        typeof data.detail === 'string'
      ) {
        message = data.detail;
      }
    }

    throw new ApiError(
      message,
      response.status,
      data
    );
  }

  return data;
}


/* =========================================
   Authentication
========================================= */

export function loginAgent(
  email,
  password
) {
  return apiFetch(
    '/api/v1/auth/login',
    {
      method: 'POST',

      body: JSON.stringify({
        email,
        password,
      }),
    }
  );
}


export function getCurrentAgent() {
  return apiFetch(
    '/api/v1/auth/me',
    {
      auth: true,
    }
  );
}


/* =========================================
   Customers
========================================= */

export function getCustomers({
  search = '',
  limit = 20,
  offset = 0,
} = {}) {
  const params =
    new URLSearchParams();

  params.set(
    'limit',
    String(limit)
  );

  params.set(
    'offset',
    String(offset)
  );

  if (search.trim()) {
    params.set(
      'search',
      search.trim()
    );
  }

  return apiFetch(
    `/api/v1/customers?${params.toString()}`,
    {
      auth: true,
    }
  );
}


export function getCustomer(
  customerId
) {
  return apiFetch(
    `/api/v1/customers/${customerId}`,
    {
      auth: true,
    }
  );
}


export function getCustomerConversations(
  customerId
) {
  return apiFetch(
    `/api/v1/customers/${customerId}/conversations`,
    {
      auth: true,
    }
  );
}


/* =========================================
   Conversations
========================================= */

export function getConversations({
  status,
  limit = 20,
  offset = 0,
} = {}) {
  const params =
    new URLSearchParams();

  params.set(
    'limit',
    String(limit)
  );

  params.set(
    'offset',
    String(offset)
  );

  if (status) {
    params.set(
      'status',
      status
    );
  }

  return apiFetch(
    `/api/v1/conversations?${params.toString()}`,
    {
      auth: true,
    }
  );
}


export function getConversation(
  conversationId
) {
  return apiFetch(
    `/api/v1/conversations/${conversationId}`,
    {
      auth: true,
    }
  );
}


export function getConversationMessages(
  conversationId
) {
  return apiFetch(
    `/api/v1/conversations/${conversationId}/messages`,
    {
      auth: true,
    }
  );
}


export function updateConversationStatus(
  conversationId,
  status
) {
  return apiFetch(
    `/api/v1/conversations/${conversationId}/status`,
    {
      method: 'PATCH',
      auth: true,

      body: JSON.stringify({
        status,
      }),
    }
  );
}


/* =========================================
   AI Drafts
========================================= */

export function getPendingDrafts({
  limit = 100,
  offset = 0,
} = {}) {
  const params =
    new URLSearchParams();

  params.set(
    'limit',
    String(limit)
  );

  params.set(
    'offset',
    String(offset)
  );

  return apiFetch(
    `/api/v1/ai-drafts/pending?${params.toString()}`,
    {
      auth: true,
    }
  );
}


export function getDraft(
  draftId
) {
  return apiFetch(
    `/api/v1/ai-drafts/${draftId}`,
    {
      auth: true,
    }
  );
}


export function approveDraft(
  draftId,
  approvedText
) {
  return apiFetch(
    `/api/v1/ai-drafts/${draftId}/approve`,
    {
      method: 'POST',
      auth: true,

      body: JSON.stringify({
        approved_text:
          approvedText,
      }),
    }
  );
}

export function sendCustomerMessage({
  externalId,
  name,
  phone,
  text,
}) {
  return apiFetch(
    '/api/v1/customer/messages',
    {
      method: 'POST',

      body: JSON.stringify({
        customer: {
          external_id:
            externalId,
          name,
          phone,
        },

        text,
      }),
    }
  );
}

export function getCustomerConversation(
  externalId
) {
  return apiFetch(
    (
      '/api/v1/customer/'
      + encodeURIComponent(
        externalId
      )
      + '/conversation'
    )
  );
}

