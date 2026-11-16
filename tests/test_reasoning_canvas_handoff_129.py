"""129 画布交接：协议校验、任务隔离、显式保存与 GDRP 门禁。"""
import copy
import json
import os
import subprocess
import unittest
from unittest import mock

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXT = os.path.join(ROOT, "extensions", "reasoning-canvas")


def packet(problem="如何减少城市配送在高峰期的重复空驶？", route="measure"):
    return {
        "schema": "gooddesign-research-packet-1.0",
        "status": "prepared_context_not_executed",
        "requirement": {
            "title": "城市配送调度研究",
            "problem": problem,
            "outcome": "减少无效里程，同时不降低配送准时率",
            "constraints": "不能牺牲司机安全与客户隐私",
            "status": "research_proposed_not_customer_confirmed",
            "revision": 1,
        },
        "route": route,
        "project_references": [
            {"id": "2019-s19", "name": "电动压裂泵", "research": True, "relation": "reference_not_adoption_proof"}
        ],
        "method_references": ["R48", "R42"],
        "unknowns": ["实时订单分布与验收口径"],
        "pending_clarifications": [
            {"field": "operating_context", "value": "先限定一个城市", "actor": "研究人员", "status": "pending_confirmation", "saved_at": "2026-11-15T00:00:00Z"}
        ],
        "model_calls": 0,
        "source_projects_modified": False,
        "engineering_validated": False,
        "expert_reviewed": False,
    }


def envelope(task_id="task-city-001"):
    return {
        "schema": "gooddesign-canvas-handoff-1.0",
        "task_id": task_id,
        "created_at": "2026-11-15T01:02:03Z",
        "packet": packet(),
    }


class StateJavaScriptTests(unittest.TestCase):
    def run_state(self, body, initial=None, search=""):
        data_path = os.path.join(EXT, "data.js")
        state_path = os.path.join(EXT, "state.js")
        harness = r"""
const fs = require('fs');
const vm = require('vm');
const store = new Map(Object.entries(INITIAL_STORE));
const localStorage = {
  getItem(key) { return store.has(key) ? store.get(key) : null; },
  setItem(key, value) { store.set(key, String(value)); },
  removeItem(key) { store.delete(key); }
};
const context = {
  console,
  URLSearchParams,
  store,
  localStorage,
  location: { pathname: '/canvas/', search: INITIAL_SEARCH },
  history: { replaceState() {} }
};
context.window = context;
vm.createContext(context);
vm.runInContext(fs.readFileSync(DATA_PATH, 'utf8'), context);
vm.runInContext(fs.readFileSync(STATE_PATH, 'utf8'), context);
const result = vm.runInContext(`(function () { BODY })()`, context);
console.log(JSON.stringify(result));
"""
        harness = harness.replace("INITIAL_STORE", json.dumps(initial or {}, ensure_ascii=False))
        harness = harness.replace("INITIAL_SEARCH", json.dumps(search))
        harness = harness.replace("DATA_PATH", json.dumps(data_path))
        harness = harness.replace("STATE_PATH", json.dumps(state_path))
        harness = harness.replace("BODY", body)
        completed = subprocess.run(
            ["node", "-e", harness], cwd=ROOT, text=True, capture_output=True, timeout=20
        )
        if completed.returncode:
            self.fail(f"Node state scenario failed:\n{completed.stderr}\n{completed.stdout}")
        return json.loads(completed.stdout.strip().splitlines()[-1])

    def test_invalid_envelopes_and_packets_are_explicit_errors(self):
        base = envelope()
        cases = []

        def add(name, path, value):
            changed = copy.deepcopy(base)
            target = changed
            for key in path[:-1]:
                target = target[key]
            target[path[-1]] = value
            cases.append((name, changed))

        add("envelope schema", ["schema"], "other")
        add("task id", ["task_id"], "")
        add("created at", ["created_at"], "not-a-date")
        add("packet schema", ["packet", "schema"], "other")
        add("packet executed", ["packet", "status"], "executed")
        add("problem blank", ["packet", "requirement", "problem"], "  ")
        add("requirement confirmed", ["packet", "requirement", "status"], "customer_confirmed")
        add("route invalid", ["packet", "route"], "agents")
        add("route object invalid", ["packet", "route"], {"id": "agents"})
        add("route wrong type", ["packet", "route"], 42)
        add("model calls", ["packet", "model_calls"], 1)
        add("source modified", ["packet", "source_projects_modified"], True)
        add("engineering validated", ["packet", "engineering_validated"], True)
        add("expert reviewed", ["packet", "expert_reviewed"], True)
        add("reference promoted", ["packet", "project_references", 0, "relation"], "adoption_proof")
        add("clarification confirmed", ["packet", "pending_clarifications", 0, "status"], "confirmed")
        result = self.run_state(
            """
const cases = CASES;
const failures = [];
for (const [name, value] of cases) {
  try { RC_State.validateHandoff(value); failures.push(name + ':accepted'); }
  catch (error) { if (!error.message.startsWith('交接导入失败：')) failures.push(name + ':' + error.message); }
}
try { RC_State.parseHandoff('{bad json'); failures.push('malformed:accepted'); }
catch (error) { if (!error.message.includes('JSON')) failures.push('malformed:' + error.message); }
return failures;
""".replace("CASES", json.dumps(cases, ensure_ascii=False))
        )
        self.assertEqual(result, [])

    def test_invalid_boot_never_falls_back_to_demo(self):
        bad = envelope()
        bad["packet"]["requirement"]["problem"] = ""
        initial = {
            "gd-reasoning-canvas-handoff-v1": json.dumps(bad, ensure_ascii=False),
            "gd-reasoning-canvas-v1": '{"selected":"n4"}',
        }
        result = self.run_state(
            """
const boot = RC_State.boot();
return {
  error: boot.error || '',
  hasState: !!boot.state,
  handoffPreserved: store.has(RC_State.HANDOFF_KEY),
  demoPreserved: store.get(RC_State.LS_KEY)
};
""",
            initial=initial,
        )
        self.assertIn("problem", result["error"])
        self.assertFalse(result["hasState"])
        self.assertTrue(result["handoffPreserved"])
        self.assertEqual(result["demoPreserved"], '{"selected":"n4"}')

    def test_all_nullable_routes_validate(self):
        values = [(None, None), ("measure", "measure"), ("functions", "functions"), ("concepts", "concepts"), ({"id": "measure", "name": "先验证问题与量测"}, "measure")]
        result = self.run_state(
            """
const routes = ROUTES;
return routes.map(([route, expected]) => {
  const value = BASE;
  value.packet.route = route;
  RC_State.validateHandoff(value);
  const actual = RC_State.researchState(value).workspace.route;
  if (actual !== expected) throw Error('route mismatch: ' + actual);
  return actual;
});
""".replace("ROUTES", json.dumps(values, ensure_ascii=False)).replace("BASE", json.dumps(envelope(), ensure_ascii=False))
        )
        self.assertEqual(result, [expected for _, expected in values])

    def test_mapping_storage_single_consumption_refresh_and_export(self):
        original = json.dumps(envelope(), ensure_ascii=False)
        initial = {
            "gd-reasoning-canvas-handoff-v1": original,
            "gd-reasoning-canvas-v1": '{"selected":"n5","demoMarker":true}',
            "gd-reasoning-canvas-workspace-v1:other-task": '{"other":true}',
        }
        result = self.run_state(
            """
const first = RC_State.boot();
if (first.error) throw Error(first.error);
const state = first.state;
RC_State.addNote(state, 'n1', '我', '保留这条本地编辑');
if (!RC_State.save(state)) throw Error('save failed');
const markdown = RC_State.exportMarkdown(state);
const consumed = !store.has(RC_State.HANDOFF_KEY);
store.set(RC_State.HANDOFF_KEY, '{invalid later handoff');
location.search = '?workspace=task-city-001';
const second = RC_State.boot();
const secondMarkdown = RC_State.exportMarkdown(second.state);
return {
  imported: first.imported === true,
  id: state.workspace.id,
  kind: state.workspace.kind,
  title: state.workspace.title,
  route: state.workspace.route,
  groups: state.intent.map(group => ({key: group.key, items: group.items})),
  statuses: state.statuses,
  runtime: {
    evMarks: state.evMarks,
    subproblems: state.subproblems,
    redteam: state.redteam,
    priorities: state.priorities,
    engineConfirmed: state.engineConfirmed,
    flow: state.flow,
    extraEvidence: state.extraEvidence
  },
  sourceProblem: state.workspace.sourcePacket.requirement.problem,
  consumed,
  workspaceSaved: store.has(RC_State.workspaceKey('task-city-001')),
  demo: store.get(RC_State.LS_KEY),
  other: store.get(RC_State.workspaceKey('other-task')),
  secondError: second.error || '',
  laterHandoffUntouched: store.get(RC_State.HANDOFF_KEY),
  noteRestored: second.state.notes.n1[0].text,
  markdown,
  secondMarkdown,
  demoMarkdown: RC_State.exportMarkdown(RC_State.defaultState())
};
""",
            initial=initial,
        )
        self.assertTrue(result["imported"])
        self.assertEqual(result["id"], "task-city-001")
        self.assertEqual(result["kind"], "needs-research")
        self.assertEqual(result["title"], "城市配送调度研究")
        self.assertEqual(result["route"], "measure")
        self.assertEqual([g["key"] for g in result["groups"]], ["用户陈述", "需要", "约束", "待补证"])
        self.assertNotIn("事实", [g["key"] for g in result["groups"]])
        self.assertNotIn("假设", [g["key"] for g in result["groups"]])
        self.assertEqual(result["groups"][0]["items"], [packet()["requirement"]["problem"]])
        self.assertEqual(result["statuses"], {"n1": "doing", "n2": "todo", "n3": "todo", "n4": "todo", "n5": "todo", "n6": "todo", "n7": "todo"})
        for key in ["evMarks", "subproblems", "redteam", "priorities", "engineConfirmed", "extraEvidence"]:
            self.assertEqual(result["runtime"][key], {} if key in {"evMarks", "priorities"} else [], key)
        self.assertEqual(result["runtime"]["flow"], {"runs": 0, "log": [], "dirty": False})
        self.assertEqual(result["sourceProblem"], packet()["requirement"]["problem"])
        self.assertTrue(result["consumed"])
        self.assertTrue(result["workspaceSaved"])
        self.assertEqual(result["demo"], initial["gd-reasoning-canvas-v1"])
        self.assertEqual(result["other"], initial["gd-reasoning-canvas-workspace-v1:other-task"])
        self.assertEqual(result["secondError"], "")
        self.assertEqual(result["laterHandoffUntouched"], "{invalid later handoff")
        self.assertEqual(result["noteRestored"], "保留这条本地编辑")
        for markdown in [result["markdown"], result["secondMarkdown"]]:
            self.assertIn("城市配送调度研究", markdown)
            self.assertIn("参考项目线索[2019-s19] 电动压裂泵", markdown)
            for polluted in ["割胶", "形成层", "月壤", "柔顺限深", "GD-CRE", "K1]", "胶园"]:
                self.assertNotIn(polluted, markdown)
        self.assertIn("割胶机器人", result["demoMarkdown"])

    def test_two_tasks_and_reset_only_touch_their_own_local_key(self):
        first = envelope("task-one")
        second = envelope("task-two")
        second["packet"]["requirement"]["title"] = "第二项研究"
        second["packet"]["requirement"]["problem"] = "如何降低实验室样品的重复登记？"
        initial = {"gd-reasoning-canvas-v1": '{"demo":true}'}
        result = self.run_state(
            """
const one = RC_State.researchState(ONE);
const two = RC_State.researchState(TWO);
RC_State.save(one);
RC_State.save(two);
RC_State.intentAdd(one, '需要', '只加入第一个任务');
RC_State.save(one);
location.search = '?workspace=task-two';
const loadedTwo = RC_State.boot().state;
const reset = RC_State.reset(one);
return {
  oneNeeds: one.intent.find(group => group.key === '需要').items,
  twoNeeds: loadedTwo.intent.find(group => group.key === '需要').items,
  oneExists: store.has(RC_State.workspaceKey('task-one')),
  twoExists: store.has(RC_State.workspaceKey('task-two')),
  demoExists: store.has(RC_State.LS_KEY),
  resetIsDemo: !RC_State.isResearch(reset)
};
""".replace("ONE", json.dumps(first, ensure_ascii=False)).replace("TWO", json.dumps(second, ensure_ascii=False)),
            initial=initial,
        )
        self.assertIn("只加入第一个任务", result["oneNeeds"])
        self.assertNotIn("只加入第一个任务", result["twoNeeds"])
        self.assertFalse(result["oneExists"])
        self.assertTrue(result["twoExists"])
        self.assertTrue(result["demoExists"])
        self.assertTrue(result["resetIsDemo"])

    def test_storage_failure_and_missing_url_workspace_are_not_hidden(self):
        original = json.dumps(envelope(), ensure_ascii=False)
        result = self.run_state(
            """
localStorage.setItem = function () { throw Error('denied'); };
const imported = RC_State.boot();
location.search = '?workspace=missing-task';
const missing = RC_State.boot();
return {
  importedState: !!imported.state,
  warning: imported.warning || '',
  handoffPreserved: store.has(RC_State.HANDOFF_KEY),
  missingError: missing.error || '',
  missingState: !!missing.state
};
""",
            initial={"gd-reasoning-canvas-handoff-v1": original},
        )
        self.assertTrue(result["importedState"])
        self.assertIn("本地保存失败", result["warning"])
        self.assertTrue(result["handoffPreserved"])
        self.assertIn("本地任务不存在", result["missingError"])
        self.assertFalse(result["missingState"])


class MapperAndFrontendContractTests(unittest.TestCase):
    def test_mapper_rejects_needs_research_before_reading_frozen_pack(self):
        import sys
        sys.path.insert(0, os.path.join(ROOT, "scripts"))
        import canvas_gdrp_mapper
        state = {"workspace": {"id": "task-city-001", "kind": "needs-research"}}
        with mock.patch.object(canvas_gdrp_mapper, "FROZEN_PACK", new=mock.Mock()) as frozen:
            with self.assertRaisesRegex(ValueError, "拒绝套用割胶冻结研究包"):
                canvas_gdrp_mapper.map_canvas_to_gdrp(state, "task-city-001", 1)
            frozen.is_file.assert_not_called()

    def test_only_explicit_save_posts_and_double_click_is_locked(self):
        js = open(os.path.join(EXT, "reasoning-canvas.js"), encoding="utf-8").read()
        self.assertNotIn("queueRemoteSave", js)
        self.assertNotIn("setTimeout(persistRemote", js)
        self.assertEqual(js.count("apiPost(`${RC_API}/state`"), 1)
        self.assertIn("document.getElementById('rc-save').addEventListener('click', persistRemote)", js)
        self.assertIn("if (!state || remoteSaving) return;", js)
        self.assertIn("saveBtn.disabled = true;", js)
        self.assertIn("if (!boot.hasLocal && !boot.imported)", js)
        self.assertNotIn("state = Object.assign(S.defaultState(), j.result.state || {});\n      workspaceRevision", js)

    def test_root_legacy_api_and_asset_fallbacks(self):
        js = open(os.path.join(EXT, "reasoning-canvas.js"), encoding="utf-8").read()
        html = open(os.path.join(EXT, "index.html"), encoding="utf-8").read()
        self.assertIn("/^\\/(?:inno\\/)?canvas\\//", js)
        self.assertIn("'/inno/canvas/api/rc' : '/api/rc'", js)
        self.assertIn("location.pathname}?workspace=", js)
        self.assertIn("gd-reasoning-canvas-handoff-v1", open(os.path.join(EXT, "state.js"), encoding="utf-8").read())
        for path in ["/inno/method-workbench/vendor/tokens.css", "/inno/design-system/gooddesign.css"]:
            self.assertIn(path, html)
        self.assertIn('id="rc-handoff-error"', html)
        self.assertIn('id="rc-workspace-title"', html)


class NeedsResearchHttpGateTests(unittest.TestCase):
    def setUp(self):
        import http.client
        import socketserver
        import sys
        import tempfile
        import threading
        sys.path.insert(0, os.path.join(ROOT, "scripts"))
        import reasoning_canvas_server as srv
        self.http_client = http.client
        self.tmp = tempfile.TemporaryDirectory()
        srv.STATE_DB = os.path.join(self.tmp.name, "canvas.sqlite3")
        handler = lambda *args, **kwargs: srv.Handler(*args, directory=ROOT, **kwargs)
        socketserver.TCPServer.allow_reuse_address = True
        self.httpd = socketserver.TCPServer(("127.0.0.1", 0), handler)
        threading.Thread(target=self.httpd.serve_forever, daemon=True).start()
        self.port = self.httpd.server_address[1]

    def tearDown(self):
        self.httpd.shutdown()
        self.httpd.server_close()
        self.tmp.cleanup()

    def request(self, method, path, payload=None):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8") if payload is not None else None
        headers = {"Content-Type": "application/json"} if body else {}
        conn = self.http_client.HTTPConnection("127.0.0.1", self.port, timeout=10)
        conn.request(method, path, body=body, headers=headers)
        response = conn.getresponse()
        result = json.loads(response.read().decode("utf-8"))
        status = response.status
        conn.close()
        return status, result

    def test_gdrp_and_report_reject_new_task_without_deleting_revision(self):
        state = {"workspace": {"id": "http-needs-129", "kind": "needs-research"}}
        status, saved = self.request("POST", "/api/rc/state", {"workspace_id": "http-needs-129", "base_revision": 0, "state": state})
        self.assertEqual(status, 200)
        self.assertEqual(saved["result"]["revision"], 1)
        for endpoint in ["gdrp", "gdrp_package"]:
            status, result = self.request("GET", f"/api/rc/{endpoint}?workspace_id=http-needs-129")
            self.assertEqual(status, 400)
            self.assertFalse(result["ok"])
            self.assertIn("拒绝套用割胶冻结研究包", result["error"])
        status, revisions = self.request("GET", "/api/rc/revisions?workspace_id=http-needs-129")
        self.assertEqual(status, 200)
        self.assertEqual(len(revisions["result"]), 1)


if __name__ == "__main__":
    unittest.main()
