const { chromium } = require('playwright');

async function demonstratePlaywright() {
  console.log('🚀 Starting Playwright MCP Server Demo...');

  const browser = await chromium.launch();
  const page = await browser.newPage();

  // Navigate to a test page
  await page.goto('https://example.com');
  console.log('✅ Successfully navigated to example.com');

  // Take a screenshot
  await page.screenshot({ path: 'example-screenshot.png' });
  console.log('✅ Screenshot saved as example-screenshot.png');

  // Get page title
  const title = await page.title();
  console.log(`✅ Page title: ${title}`);

  // Get page content
  const content = await page.textContent('h1');
  console.log(`✅ Main heading: ${content}`);

  await browser.close();
  console.log('✅ Browser closed successfully');
  console.log('🎭 Playwright MCP Server capabilities demonstrated!');
}

demonstratePlaywright().catch(console.error);
