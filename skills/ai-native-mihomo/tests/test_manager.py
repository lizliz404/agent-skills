#!/usr/bin/env python3
"""mihomo_manager.py 的离线测试：全部在临时目录里跑，不碰真实 ~/.config，不连 mihomo。"""

import argparse
import importlib.util
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

import yaml

SKILL_DIR = Path(__file__).resolve().parent.parent
FIX = SKILL_DIR / "tests" / "fixtures"

spec = importlib.util.spec_from_file_location("mm", SKILL_DIR / "scripts" / "mihomo_manager.py")
mm = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mm)


class Sandbox(unittest.TestCase):
    """把所有运行时路径重定向到临时目录。"""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="mm-test-"))
        self._saved = {}
        mapping = {
            "CONF_DIR": self.tmp / "mihomo",
            "LIVE": self.tmp / "mihomo" / "config.yaml",
            "SOURCES_DIR": self.tmp / "mihomo" / "sources",
            "BASE_FILE": self.tmp / "mihomo" / "sources" / "base.yaml",
            "BACKUP_DIR": self.tmp / "mihomo" / "backups",
            "MANAGER_DIR": self.tmp / "mihomo" / "manager",
            "MANIFEST": self.tmp / "mihomo" / "manager" / "manifest.json",
            "STAGING_DIR": self.tmp / "mihomo" / ".staging",
            "CANDIDATE": self.tmp / "mihomo" / ".staging" / "candidate.yaml",
            "STATE_DIR": self.tmp / "state",
            "STATE_FILE": self.tmp / "state" / "state.json",
            "LOCK_FILE": self.tmp / "state" / "reconcile.lock",
        }
        for key, value in mapping.items():
            self._saved[key] = getattr(mm, key)
            setattr(mm, key, value)

    def tearDown(self):
        for key, value in self._saved.items():
            setattr(mm, key, value)
        shutil.rmtree(self.tmp, ignore_errors=True)

    # -- helpers ---------------------------------------------------------
    def policy(self):
        return mm.load_policy()

    def seed_base(self, fixture="full_config.yaml"):
        mm.SOURCES_DIR.mkdir(parents=True, exist_ok=True)
        data = yaml.safe_load((FIX / fixture).read_text(encoding="utf-8"))
        mm.atomic_write(
            mm.BASE_FILE, yaml.safe_dump(data, allow_unicode=True, sort_keys=False), 0o600
        )

    def drop(self, fixture):
        mm.SOURCES_DIR.mkdir(parents=True, exist_ok=True)
        shutil.copy2(FIX / fixture, mm.SOURCES_DIR / fixture)

    def sentinel_live(self, text="secret: sentinel\nproxies: []\n"):
        mm.atomic_write(mm.LIVE, text, 0o600)
        return text

    def reconcile(self, dry_run=False):
        return mm.cmd_reconcile(argparse.Namespace(dry_run=dry_run))


class TestSchema(Sandbox):
    def test_full_config(self):
        proxies, kind = mm.read_input(FIX / "full_config.yaml")
        self.assertEqual(kind, "full-config")
        self.assertEqual(len(proxies), 2)

    def test_provider(self):
        proxies, kind = mm.read_input(FIX / "provider.yaml")
        self.assertEqual(kind, "provider")
        self.assertEqual(len(proxies), 1)

    def test_proxy_list_json(self):
        proxies, kind = mm.read_input(FIX / "proxy_list.json")
        self.assertEqual(kind, "proxy-list")
        self.assertEqual(len(proxies), 1)

    def test_bad_schema_rejected(self):
        with self.assertRaises(mm.SchemaError) as ctx:
            mm.read_input(FIX / "bad_schema.yaml")
        self.assertIn("proxies", str(ctx.exception))

    def test_empty_proxies_rejected(self):
        with self.assertRaises(mm.SchemaError):
            mm.read_input(FIX / "empty_proxies.yaml")

    def test_scalar_rejected(self):
        with self.assertRaises(mm.SchemaError):
            mm.extract_proxies("just a string", "x")

    def test_list_of_scalars_rejected(self):
        with self.assertRaises(mm.SchemaError):
            mm.extract_proxies([1, 2, 3], "x")


class TestNormalizeMerge(Sandbox):
    def test_random_fingerprint_normalized(self):
        policy = self.policy()
        proxies, _ = mm.read_input(FIX / "full_config.yaml")
        merged, _, fixes, _ = mm.merge_proxies([("f", proxies)], policy)
        by_name = {p["name"]: p for p in merged}
        self.assertEqual(by_name["美国测试·AWSJP·1倍消耗"]["client-fingerprint"], "chrome")
        self.assertEqual(by_name["香港测试·直连·3倍消耗"]["client-fingerprint"], "safari")
        self.assertEqual(len(fixes), 1)

    def test_dedupe_same_definition(self):
        policy = self.policy()
        proxies, _ = mm.read_input(FIX / "full_config.yaml")
        merged, conflicts, _, _ = mm.merge_proxies(
            [("a", proxies), ("b", list(proxies))], policy
        )
        self.assertEqual(len(merged), 2)
        self.assertEqual(conflicts, [])

    def test_conflict_renamed_keeping_prefix(self):
        policy = self.policy()
        first, _ = mm.read_input(FIX / "full_config.yaml")
        second, _ = mm.read_input(FIX / "dup_conflict.yaml")
        merged, conflicts, _, _ = mm.merge_proxies([("a", first), ("b", second)], policy)
        names = [p["name"] for p in merged]
        self.assertIn("美国测试·AWSJP·1倍消耗", names)
        self.assertIn("美国测试·AWSJP·1倍消耗 (2)", names)
        self.assertTrue(all(n.startswith("美国") for n in names if "美国测试" in n))
        self.assertEqual(len(conflicts), 1)
        self.assertEqual(conflicts[0]["renamed_to"], "美国测试·AWSJP·1倍消耗 (2)")

    def test_excluded_fake_nodes(self):
        policy = self.policy()
        second, _ = mm.read_input(FIX / "dup_conflict.yaml")
        merged, _, _, excluded = mm.merge_proxies([("b", second)], policy)
        names = [p["name"] for p in merged]
        self.assertNotIn("官网：example.invalid", names)
        self.assertNotIn("永久流量:100.0G", names)
        self.assertEqual(len(excluded), 2)

    def test_idempotent(self):
        policy = self.policy()
        first, _ = mm.read_input(FIX / "full_config.yaml")
        second, _ = mm.read_input(FIX / "dup_conflict.yaml")
        sources = [("a", first), ("b", second)]
        a = json.dumps(mm.merge_proxies(sources, policy)[0], sort_keys=True, ensure_ascii=False)
        b = json.dumps(mm.merge_proxies(sources, policy)[0], sort_keys=True, ensure_ascii=False)
        self.assertEqual(a, b)

    def test_order_independent_dedupe(self):
        """同样两个输入，正反顺序去重结果一致（同名同定义不会累积）。"""
        policy = self.policy()
        first, _ = mm.read_input(FIX / "full_config.yaml")
        forward = mm.merge_proxies([("a", first), ("b", list(first))], policy)[0]
        reverse = mm.merge_proxies([("b", first), ("a", list(first))], policy)[0]
        self.assertEqual(len(forward), len(reverse))


class TestGroups(Sandbox):
    def test_region_order_and_hk_last(self):
        policy = self.policy()
        names = [
            "香港测试·直连·3倍消耗",
            "美国测试·AWSJP·1倍消耗",
            "日本测试·AWSJP·1倍消耗",
            "其他测试·AWSJP·2倍消耗",
        ]
        groups = mm.build_groups(names, policy)
        self.assertEqual(groups[0]["name"], policy["group_name"])
        self.assertEqual(groups[0]["type"], "select")
        self.assertEqual([g["name"] for g in groups[1:]], ["美国优选", "日本优选", "其他优选", "香港优选"])
        self.assertEqual(groups[0]["proxies"][0], "美国测试·AWSJP·1倍消耗")
        self.assertEqual(groups[0]["proxies"][-1], "香港测试·直连·3倍消耗")
        for g in groups[1:]:
            self.assertEqual(g["type"], "url-test")
            self.assertIn("url", g)

    def test_groups_follow_policy_sot(self):
        """换一份 policy 的地区顺序，生成的分组顺序必须跟着变（证明没有第二份硬编码）。"""
        policy = dict(self.policy())
        policy["region_order"] = ["其他", "香港", "台湾", "新加坡", "日本", "美国"]
        policy["region_fallback"] = "其他"
        names = ["香港测试·直连·3倍消耗", "美国测试·AWSJP·1倍消耗", "其他测试·AWSJP·2倍消耗"]
        groups = mm.build_groups(names, policy)
        self.assertEqual([g["name"] for g in groups[1:]], ["其他优选", "香港优选", "美国优选"])
        self.assertEqual(groups[0]["proxies"][-1], "美国测试·AWSJP·1倍消耗")

    def test_region_matches_flag_prefixed_provider_names(self):
        """备线机场给名字加国旗 emoji —— 不能因此把节点全归到「其他」。"""
        policy = self.policy()
        cases = {
            "🇺🇸 美国-01 | AI | 解锁": "美国",
            "🇯🇵 日本-01 | AI | 解锁": "日本",
            "🇭🇰 香港-01 | 流媒体": "香港",
            "🇼🇸 台湾-01 | AI | 解锁": "台湾",
            "印度尼西亚·AWSJP·2倍消耗": "其他",
        }
        for name, expect in cases.items():
            self.assertEqual(mm.region_of(name, policy), expect, name)

    def test_manifest_carries_provider_order_and_junk_patterns(self):
        """策略只在 policy.yaml 写一份；selector 从 manifest 读，不硬编码。"""
        policy = self.policy()
        mm.write_manifest(policy, [{"name": "x"}], {"美国": 1})
        data = json.loads(mm.MANIFEST.read_text(encoding="utf-8"))
        self.assertEqual([p["source"] for p in data["provider_order"]],
                         [p["source"] for p in policy["provider_order"]])
        self.assertEqual(data["exclude_name_patterns"], policy["exclude_name_patterns"])
        inline = next(p for p in policy["provider_order"] if p["source"] == "")
        self.assertEqual(data["providers"]["main"]["name"], inline["label"])

    def test_policy_rejects_hk_not_last(self):
        saved = mm.POLICY_PATH
        try:
            bad = self.tmp / "policy.yaml"
            policy = dict(self.policy())
            policy["region_order"] = ["香港", "美国", "日本", "新加坡", "台湾", "其他"]
            bad.write_text(yaml.safe_dump(policy, allow_unicode=True), encoding="utf-8")
            mm.POLICY_PATH = bad
            with self.assertRaises(mm.ManagerError):
                mm.load_policy()
        finally:
            mm.POLICY_PATH = saved


class TestPipeline(Sandbox):
    def test_candidate_invalid_keeps_live(self):
        self.seed_base()
        before = self.sentinel_live()
        self.drop("provider.yaml")
        original = mm.mihomo_test
        mm.mihomo_test = lambda p: (False, "level=error msg=\"boom\"")
        try:
            rc = self.reconcile()
        finally:
            mm.mihomo_test = original
        self.assertEqual(rc, 1)
        self.assertEqual(mm.LIVE.read_text(encoding="utf-8"), before)
        state = mm.read_state()
        self.assertEqual(state["status"], "failed")
        self.assertIn("candidate", state["last_error"])

    def test_success_updates_live_and_manifest(self):
        self.seed_base()
        self.sentinel_live()
        self.drop("provider.yaml")
        original_test, original_reload, original_post = mm.mihomo_test, mm.reload_live, mm.post_check
        mm.mihomo_test = lambda p: (True, "configuration file ... test is successful")
        mm.reload_live = lambda secret, timeout=15: 204
        mm.post_check = lambda secret, expected, group, timeout=15: (True, "ok")
        try:
            rc = self.reconcile()
        finally:
            mm.mihomo_test, mm.reload_live, mm.post_check = original_test, original_reload, original_post
        self.assertEqual(rc, 0)
        text = mm.LIVE.read_text(encoding="utf-8")
        self.assertIn("美国测试·AWSJP·1倍消耗", text)
        self.assertIn("日本测试·AWSJP·1倍消耗", text)
        self.assertNotIn("不该被采纳的组", text)
        self.assertEqual(oct(mm.LIVE.stat().st_mode & 0o777), "0o600")
        self.assertTrue(mm.MANIFEST.is_file())
        state = mm.read_state()
        self.assertEqual(state["status"], "ok")
        self.assertEqual(state["regions"]["美国"], 1)

    def test_input_top_level_policy_not_overridden(self):
        """输入文件里的 dns/tun/rules 不得覆盖 base 的策略。"""
        self.seed_base()
        self.sentinel_live()
        mm.SOURCES_DIR.mkdir(parents=True, exist_ok=True)
        hostile = mm.SOURCES_DIR / "hostile.yaml"
        hostile.write_text(
            "log-level: debug\n"
            "dns:\n  enable: false\n"
            "tun:\n  enable: false\n"
            "rules:\n  - MATCH,REJECT\n"
            "proxies:\n  - name: 日本测试·AWSJP·1倍消耗\n"
            "    type: vless\n    server: 198.51.100.55\n    port: 443\n"
            "    uuid: 00000000-0000-0000-0000-000000000055\n",
            encoding="utf-8",
        )
        original_test, original_reload, original_post = mm.mihomo_test, mm.reload_live, mm.post_check
        mm.mihomo_test = lambda p: (True, "test is successful")
        mm.reload_live = lambda secret, timeout=15: 204
        mm.post_check = lambda secret, expected, group, timeout=15: (True, "ok")
        try:
            self.assertEqual(self.reconcile(), 0)
        finally:
            mm.mihomo_test, mm.reload_live, mm.post_check = original_test, original_reload, original_post
        cfg = yaml.safe_load(mm.LIVE.read_text(encoding="utf-8"))
        # base 里 log-level 是 warning、rules 是 MATCH,DIRECT；hostile 想覆盖成 debug/REJECT —— 必须无效
        self.assertEqual(cfg["log-level"], "warning")
        self.assertEqual(cfg["rules"], ["MATCH,DIRECT"])
        self.assertIs(cfg["dns"]["enable"], True)

    def test_reload_failure_rolls_back(self):
        self.seed_base()
        before = self.sentinel_live()
        original_test, original_reload = mm.mihomo_test, mm.reload_live
        mm.mihomo_test = lambda p: (True, "test is successful")

        def boom(secret, timeout=15):
            raise OSError("connection refused")

        mm.reload_live = boom
        try:
            rc = self.reconcile()
        finally:
            mm.mihomo_test, mm.reload_live = original_test, original_reload
        self.assertEqual(rc, 1)
        self.assertEqual(mm.LIVE.read_text(encoding="utf-8"), before)
        state = mm.read_state()
        self.assertEqual(state["status"], "failed")
        self.assertIn("回滚", state["last_error"])

    def test_dry_run_does_not_touch_live(self):
        self.seed_base()
        before = self.sentinel_live()
        original = mm.mihomo_test
        mm.mihomo_test = lambda p: (True, "test is successful")
        try:
            rc = self.reconcile(dry_run=True)
        finally:
            mm.mihomo_test = original
        self.assertEqual(rc, 0)
        self.assertEqual(mm.LIVE.read_text(encoding="utf-8"), before)
        self.assertFalse(mm.MANIFEST.exists())

    def test_render_is_bit_identical(self):
        """同样输入必须生成逐字节相同的 config（时间戳不进去）。"""
        policy = self.policy()
        proxies, _, _, _ = mm.merge_proxies([("f", mm.read_input(FIX / "full_config.yaml")[0])], policy)
        cfg = mm.build_config({"log-level": "info"}, proxies, policy)
        self.assertEqual(mm.render_config(cfg, policy), mm.render_config(cfg, policy))

    def test_dry_run_idempotent(self):
        self.seed_base()
        self.sentinel_live()
        original = mm.mihomo_test
        mm.mihomo_test = lambda p: (True, "test is successful")
        try:
            self.reconcile(dry_run=True)
            first = mm.file_sha256(mm.CANDIDATE)
            self.reconcile(dry_run=True)
            second = mm.file_sha256(mm.CANDIDATE)
        finally:
            mm.mihomo_test = original
        self.assertEqual(first, second)

    def test_manifest_has_no_secrets(self):
        self.seed_base()
        self.sentinel_live()
        original_test, original_reload, original_post = mm.mihomo_test, mm.reload_live, mm.post_check
        mm.mihomo_test = lambda p: (True, "test is successful")
        mm.reload_live = lambda secret, timeout=15: 204
        mm.post_check = lambda secret, expected, group, timeout=15: (True, "ok")
        try:
            self.reconcile()
        finally:
            mm.mihomo_test, mm.reload_live, mm.post_check = original_test, original_reload, original_post
        blob = mm.MANIFEST.read_text(encoding="utf-8")
        for needle in ("198.51.100", "00000000-0000-0000", "uuid", "reality", "public-key", "server"):
            self.assertNotIn(needle, blob)


class TestLock(Sandbox):
    def test_second_acquire_is_refused(self):
        first = mm.acquire_lock()
        self.assertIsNotNone(first)
        try:
            self.assertIsNone(mm.acquire_lock())
        finally:
            mm.release_lock(first)
        again = mm.acquire_lock()
        self.assertIsNotNone(again)
        mm.release_lock(again)


if __name__ == "__main__":
    sys.exit(0 if unittest.main(exit=False).result.wasSuccessful() else 1)
