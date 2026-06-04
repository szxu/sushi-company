// @ts-check
const { defineConfig } = require("@playwright/test");

module.exports = defineConfig({
  testDir: "./tests/bdd",
  timeout: 30000,
  expect: { timeout: 5000 },
  fullyParallel: false,
  workers: 1,
  reporter: [["list"]],
  use: {
    browserName: "chromium",
    trace: "retain-on-failure"
  }
});
