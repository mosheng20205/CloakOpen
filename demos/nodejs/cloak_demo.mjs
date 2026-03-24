/**
 * Cloak 本地 HTTP API 最小示例（POST + JSON）。
 * 需 Node.js 18+（内置 fetch）。
 */
const BASE = (process.env.CLOAK_BASE_URL || "http://127.0.0.1:54381").replace(/\/$/, "");
const CLEANUP = Boolean(process.env.CLOAK_CLEANUP);

async function post(path, body = {}) {
  const res = await fetch(`${BASE}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`HTTP ${res.status}: ${text}`);
  }
  return res.json();
}

function printResult(title, data) {
  console.log(`\n=== ${title} ===`);
  console.log(JSON.stringify(data, null, 2));
}

async function main() {
  console.log("Cloak API demo | base =", BASE);

  printResult("group_list", await post("/group/list", {}));

  const groupName = `demo-node-${Date.now()}`;
  const gr = await post("/group/add", { groupName });
  printResult("group_add", gr);
  let groupId = gr.success && gr.data ? gr.data.id : null;
  if (!groupId) {
    const gl = await post("/group/list", {});
    const list = (gl.data && gl.data.list) || [];
    groupId = list[0] && list[0].id;
  }
  if (!groupId) {
    console.error("无法取得 groupId，退出");
    return;
  }

  const suffix = String(Date.now());
  const br = await post("/browser/update", {
    name: `demo-browser-node-${suffix}`,
    groupId,
    randomFingerprint: true,
    homepageUrl: "https://www.example.com",
  });
  printResult("browser_update (create)", br);
  let browserId = br.success && br.data ? br.data.id : null;

  printResult("browser_list", await post("/browser/list", { page: 0, pageSize: 10 }));

  if (browserId) {
    printResult("browser_open", await post("/browser/open", { id: browserId }));
    printResult("browser_close", await post("/browser/close", { id: browserId }));
  }

  if (CLEANUP && browserId) {
    printResult("browser_delete", await post("/browser/delete", { id: browserId }));
  }
  if (CLEANUP && groupId) {
    printResult("group_delete", await post("/group/delete", { id: groupId }));
  }
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
