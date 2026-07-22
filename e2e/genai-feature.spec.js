// Layer 3: behavioral end-to-end test.
//
// This test never asserts on the AI feature's response text. It drives the
// real running application and asserts on application state instead: did
// the ticket end up in the right queue after the AI-powered triage feature
// ran. Requires BASE_URL to point at a running instance of the app (a real
// preview or staging environment, not a mocked model client).
//
// Run with: BASE_URL=http://localhost:3000 npx playwright test e2e/

const { test, expect } = require('@playwright/test');

const BASE_URL = process.env.BASE_URL;

test.beforeAll(() => {
  if (!BASE_URL) {
    throw new Error(
      'BASE_URL is required for behavioral E2E tests. Point it at a running app instance.'
    );
  }
});

test.describe('AI-powered support ticket triage', () => {
  test('a billing question is routed to the billing queue', async ({ page }) => {
    await page.goto(`${BASE_URL}/tickets/new`);

    await page.getByLabel('Describe your issue').fill(
      'I was charged twice for my subscription this month and need a refund.'
    );
    await page.getByRole('button', { name: 'Submit ticket' }).click();

    // Wait for the AI triage feature to run and the ticket to persist its
    // resulting queue assignment. This asserts on APPLICATION STATE, not on
    // any text the model generated.
    const ticketId = await page.getByTestId('ticket-id').textContent();
    await expect(page.getByTestId('ticket-queue')).toHaveText('billing', {
      timeout: 15_000,
    });

    // Reload to confirm the routing decision was actually persisted, not
    // just rendered client-side from the AI response.
    await page.goto(`${BASE_URL}/tickets/${ticketId?.trim()}`);
    await expect(page.getByTestId('ticket-queue')).toHaveText('billing');
  });

  test('a technical issue is routed to engineering, not billing', async ({ page }) => {
    await page.goto(`${BASE_URL}/tickets/new`);

    await page.getByLabel('Describe your issue').fill(
      'The app crashes every time I try to upload a profile photo.'
    );
    await page.getByRole('button', { name: 'Submit ticket' }).click();

    await expect(page.getByTestId('ticket-queue')).toHaveText('engineering', {
      timeout: 15_000,
    });
    await expect(page.getByTestId('ticket-queue')).not.toHaveText('billing');
  });
});
