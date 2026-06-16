const { test, expect } = require("@playwright/test");
const fs = require("fs");
const os = require("os");
const path = require("path");
const { execFileSync, spawn } = require("child_process");

const root = process.env.SUSHI_TEST_ROOT || path.resolve(__dirname, "../..");
const mode = process.env.SUSHI_BDD_MODE || "multi";
const port = Number(process.env.SUSHI_TEST_PORT || 19080 + Math.floor(Math.random() * 1000));
const baseURL = `http://127.0.0.1:${port}`;

let server;
let tmpRoot;
let env;

async function gotoApp(page) {
  await page.goto(baseURL, { waitUntil: "domcontentloaded", timeout: 10000 });
}

function runBin(name, args = []) {
  return execFileSync(path.join(root, "bin", name), args, {
    env,
    encoding: "utf8",
    stdio: ["ignore", "pipe", "pipe"]
  });
}

function createIssueTask(title, detail) {
  try {
    runBin("ticket", ["--project", "SUSH", title, detail]);
  } catch {
    try {
      runBin("ticket", ["--project", "DEMO", title, detail]);
    } catch {
      // Preserve the original test failure if ticket creation also fails.
    }
  }
}

async function withIssueTaskOnFailure(title, detail, fn) {
  try {
    await fn();
  } catch (error) {
    createIssueTask(title, `${detail}\n\nDetected failure:\n${error.message}`);
    throw error;
  }
}

async function expectNoHorizontalOverflow(page, selector) {
  const offenders = await page.locator(selector).evaluateAll(elements => elements
    .map((element, index) => {
      const rect = element.getBoundingClientRect();
      return {
        index,
        text: element.textContent.trim().slice(0, 80),
        left: rect.left,
        right: rect.right,
        scrollWidth: element.scrollWidth,
        clientWidth: element.clientWidth
      };
    })
    .filter(item => item.left < -1 || item.right > window.innerWidth + 1 || item.scrollWidth > item.clientWidth + 1)
  );
  expect(offenders, `${selector} should fit horizontally`).toEqual([]);
}

async function waitForServer(request) {
  const deadline = Date.now() + 10000;
  while (Date.now() < deadline) {
    try {
      const response = await request.get(`${baseURL}/api/status`);
      if (response.ok()) return;
    } catch {
      // Server is still starting.
    }
    await new Promise(resolve => setTimeout(resolve, 250));
  }
  throw new Error(`GUI server did not start on ${baseURL}`);
}

function seedState() {
  runBin("project", ["create", "Demo and Experiments", "DEMO"]);
  runBin("ticket", ["--project", "DEMO", "Example task", "Show the clean vanilla workflow"]);

  if (mode !== "vanilla") {
    runBin("project", ["create", "Sushi Company Improvements", "SUSH"]);
    runBin("ticket", ["--project", "SUSH", "Improve Web UI", "Group tasks by project"]);
    runBin("project", ["create", "Ability Draft Plus", "ADPL"]);
    runBin("ticket", ["--project", "ADPL", "Fix combo import", "Validate Ability Draft Plus task grouping"]);
    runBin("project", ["use", "SUSH"]);
  } else {
    runBin("project", ["use", "DEMO"]);
  }
}

test.beforeAll(async ({ request }) => {
  tmpRoot = fs.mkdtempSync(path.join(os.tmpdir(), "sushi-bdd-"));
  env = {
    ...process.env,
    HOME: path.join(tmpRoot, "home"),
    SUSHI_HOME: path.join(tmpRoot, "sushi-home"),
    SUSHI_STATE_DIR: path.join(tmpRoot, "state"),
    SUSHI_GUI_PORT: String(port),
    SUSHI_CLI: path.join(root, "tests", "fixtures", "fake-sushi-cli.sh"),
    COMPANY_DIR: root
  };
  fs.mkdirSync(env.HOME, { recursive: true });
  seedState();
  server = spawn("python3", [path.join(root, "gui", "server.py")], {
    cwd: root,
    env,
    stdio: ["ignore", "pipe", "pipe"]
  });
  await waitForServer(request);
});

test.afterAll(async () => {
  if (server && !server.killed) {
    server.kill();
  }
  if (tmpRoot) {
    fs.rmSync(tmpRoot, { recursive: true, force: true });
  }
});

test("web UI loads and shows project task groups", async ({ page }) => {
  await gotoApp(page);
  await expect(page.locator(".brand-title")).toHaveText("Sushi Company");
  await expect(page.getByText("Project Tasks")).toBeVisible();
  await expect(page.locator("#overview-tasks").getByText("DEMO", { exact: true })).toBeVisible();
  await page.getByRole("button", { name: "Tasks" }).first().click();
  await expect(page.getByText("Tasks by Project")).toBeVisible();
  await expect(page.locator("#task-board").getByText("DEMO-0001")).toBeVisible();

  if (mode !== "vanilla") {
    await expect(page.locator("#task-board").getByText("SUSH", { exact: true })).toBeVisible();
    await expect(page.locator("#task-board").getByText("ADPL", { exact: true })).toBeVisible();
    await expect(page.locator("#task-board").getByText("SUSH-0001")).toBeVisible();
    await expect(page.locator("#task-board").getByText("ADPL-0001")).toBeVisible();
  }
});

test("creating a task through the UI adds it to the selected project", async ({ page }) => {
  await gotoApp(page);
  await page.getByRole("button", { name: "Tasks" }).first().click();
  await page.locator("#task-project").fill("DEMO");
  await page.locator("#task-title").fill("Second example task");
  await page.locator("#task-desc").fill("Created by the BDD browser flow");
  await page.getByRole("button", { name: "Create Task" }).click();
  await expect(page.locator("#task-board").getByText("DEMO-0002")).toBeVisible();
  await expect(page.locator("#task-board").getByText("Second example task")).toBeVisible();
});

test("tasks page fits laptop viewport without clipped form fields or wrapped task IDs", async ({ page }) => {
  await withIssueTaskOnFailure(
    "Fix laptop task layout overflow",
    "The BDD laptop layout scenario detected clipped form fields, horizontal overflow, or wrapped task IDs.",
    async () => {
      await page.setViewportSize({ width: 1366, height: 768 });
      const ticketId = mode === "vanilla" ? "DEMO-0001" : "SUSH-0001";
      await gotoApp(page);
      await page.getByRole("button", { name: "Tasks" }).first().click();
      await expect(page.getByText("Tasks by Project")).toBeVisible();
      await expect(page.locator("#task-board").getByText(ticketId)).toBeVisible();

      const documentWidth = await page.evaluate(() => document.documentElement.scrollWidth);
      expect(documentWidth, "document should not have horizontal overflow").toBeLessThanOrEqual(1366);
      await expectNoHorizontalOverflow(page, "#page-tasks .panel, #page-tasks input, #page-tasks textarea, #page-tasks button, #page-tasks .task-card, #page-tasks .code");

      const wrappedCodes = await page.locator("#page-tasks .task-card .code").evaluateAll(elements => elements
        .map(element => ({
          text: element.textContent.trim(),
          height: element.getBoundingClientRect().height,
          lineHeight: Number.parseFloat(getComputedStyle(element).lineHeight)
        }))
        .filter(item => item.height > item.lineHeight * 1.5)
      );
      expect(wrappedCodes, "task IDs should stay on one line").toEqual([]);
    }
  );
});

test("doctor panel runs from the browser UI", async ({ page }) => {
  await gotoApp(page);
  await page.getByRole("button", { name: "Run Doctor" }).click();
  await expect(page.locator("#doctor-status")).toContainText(/PASS|FAIL/);
});

test("shipping from the Web UI starts a run without a duplicate-run abort", async ({ page }) => {
  await withIssueTaskOnFailure(
    "Fix Web UI ship launch automation",
    "The BDD Ship button scenario detected that a GUI-triggered ship did not start cleanly.",
    async () => {
      const ticketId = mode === "vanilla" ? "DEMO-0001" : "SUSH-0001";
      await gotoApp(page);
      await page.getByRole("button", { name: "Tasks" }).first().click();
      const taskCard = page.locator(".task-card").filter({ hasText: ticketId }).first();
      await expect(taskCard).toBeVisible();
      await taskCard.getByRole("button", { name: "Ship" }).click();
      await expect(page.locator("#terminal-title")).toContainText(`${ticketId} output`);
      await expect(page.locator("#terminal-output")).toContainText(/GUI Triggered Ship|Shipping|SHIP START|fake-sushi-cli/, { timeout: 10000 });
      await expect(page.locator("#terminal-output")).not.toContainText("ABORT: another ship/sushi is already running");
      await expect(page.locator("#terminal-output")).toContainText("fake-sushi-cli: APPROVED", { timeout: 10000 });
    }
  );
});
